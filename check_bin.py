#!/usr/bin/python
# coding: utf-8

from types import StringTypes
import ipdb
import logging

log = logging.getLogger('')
log.setLevel(logging.DEBUG)

# create console handler and set level to info
log_format = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(log_format)
log.addHandler(ch)

# create file handler and set to debug
fh = logging.FileHandler('check_bin.log')
fh.setFormatter(log_format)
log.addHandler(fh)

from send_sms import SendSMS
import mechanize
from BeautifulSoup import BeautifulSoup
from datetime import datetime
from secrets import postcode, address

# passed the browser and finds the right address option in the selection
def get_address_id(br):
    for item in br.find_control('find-address-select').items:
        text = item.get_labels()[0].text
        name = item.name
        if address in text:
            log.debug("%s = %s" % (text, name))
            return name

# passed html text, finds the right table, parses it and returns
# the next black bin collection date
def get_next_date(html):
    soup = BeautifulSoup(html)

    table =soup.find("table", { 'class' : 'collection-rounds' })

    for row in table.findAll('tr'):
        td = row.findAll('td')
        if len(td) == 0:
            continue
        bin_type = td[0].text
        bin_date = td[3].text

        if bin_type == 'Refuse':
            log.debug("%s on %s" % (bin_type, bin_date))
            return bin_date

# get browser
log.info("starting")
br = mechanize.Browser()
br.open('https://www.bristol.gov.uk/forms/collection-day-finder#step1')

# forms aren't named, so have to use index
br.form = list(br.forms())[1]

# fill in the postcode & submit
br['postcode'] = postcode
response = br.submit()

# get the address id & submit
br.form = list(br.forms())[1]
address_id = get_address_id(br)
assert type(address_id) in StringTypes, "address not found"
br['find-address-select'] = [address_id] # have to assign as sequence
response = br.submit()

# submit again for pointless confirmation stage
br.form = list(br.forms())[1]
response = br.submit()

# parse the date
html = response.read()
next_date = get_next_date(html)
assert type(next_date) in StringTypes, "date not found"

# convert the date to datetime so we can compare
date_object = datetime.strptime(next_date, '%d-%m-%Y')
today = datetime.today()
delta = date_object - today 
log.debug("%d days until collection" % delta.days)

# if the day before
if delta.days == 0:
    sms = SendSMS()
    sms.send('black bins!')
