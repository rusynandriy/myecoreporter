import base64
from twilio.rest import Client
import src.utils.utils as utils
import urllib.parse
import os

# load in the Account details we need for Twilio and create a Client we can use to send messages.
twilio_account_sid = (utils.open_file('secret/keys/twilio_account_sid.txt') or os.environ['twilio_account_sid'] )
twilio_auth_token = (utils.open_file('secret/keys/twilio_auth_token.txt') or os.environ['twilio_auth_token'])
twilio_client = Client(twilio_account_sid, twilio_auth_token)

# send an outgoing SMS to a given user from a given phone number
# Note that "phone_number" here is the bot's number, and user.username is the User's number
def send_sms(response, user, phone_number):
     twilio_client.messages.create(
            body=response,
            from_=phone_number, 
            to=user.username)

# Twilio sends messages encoded in base64 (and sometimes URL encoded), so we use this helper method to extract the message OR phone number as needed.
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