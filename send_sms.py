'''
use txtlocal sms service
http://www.txtlocal.com/sendsmspost.php
'''
from requests import *
from secrets import number, username, hash
import logging
logger = logging.getLogger(__name__)

class SendSMS():

    def send(self,message):
        test_flag = 0
        sender = 'python'

        values = {'test'    : test_flag,
                  'uname'   : username,
                  'hash'    : hash,
                  'message' : message,
                  'from'    : sender,
                  'selectednums' : (number) }

        url = 'http://www.txtlocal.com/sendsmspost.php'
        try:
            r = get(url,params=values)
            if r.status_code == 200:
                logger.info("SMS sent")
                return True
        except ConnectionError:
            logger.error("connection error")
            return False

