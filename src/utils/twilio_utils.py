import base64
from twilio.rest import Client
import src.utils.utils as utils
import urllib.parse
import os

twilio_account_sid = (utils.open_file('secret/keys/twilio_account_sid.txt') or os.environ['twilio_account_sid'] )
twilio_auth_token = (utils.open_file('secret/keys/twilio_auth_token.txt') or os.environ['twilio_auth_token'])
twilio_number = (utils.open_file('secret/keys/twilio_number.txt') or os.environ['twilio_number'])
twilio_client = Client(twilio_account_sid, twilio_auth_token)

def send_sms(response, user):
     twilio_client.messages.create(
            body=response,
            from_=twilio_number, 
            to=user.username)

def parse_response(event, target):
        # assume the data is base64 encoded
        body = event['body']
        # convert body to a string from base64
        try:
                body = base64.b64decode(body).decode('utf-8')
        except:
                body = body
        if target == "message":
                sms = urllib.parse.unquote_plus(body[body.find('Bo')+5:body.find('&FromCo')]) # 'hi'
                return sms
        elif target == "number":
                number = "+" + body[body.find('From=')+8:body.find('&Api')] # "+15551236789"
                return number