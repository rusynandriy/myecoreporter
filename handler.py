# import standard python libraries
import json
from datetime import datetime as dt
from time import sleep
import urllib.parse
import boto3
import os


# import our custom utilities + helper classes
import src.utils.twilio_utils as twilio
import src.gpt3 as gpt3
import src.db.dynamo as dynamo
import src.utils.utils as utils

# import our dynamo classes
from src.classes.conversation import Conversation
from src.classes.user import User

def call_gpt(user, convo):
    # build prompt
    prompt = gpt3.build_myej_prompt(convo, user)
    print("prompt on next line:")
    print(prompt)

    # call GPT3
    response = gpt3.get_response(prompt, user)
    print("response is: ", response)

    return response

def process_incoming_message(username, message, testing):
    print(f"processing incoming message {message} from {username}")

    # get the user and convo from the database (if they exist, otherwise create them)
    user = User.from_username(username)
    convo = Conversation.from_username(username)
    
    # dev thing to help with testing. Can also be used by users if they get stuck.
    if("RESET" == message.strip().upper()): 
        print("ending convo, they just hit the reset button!")
        convo.add_message("RESET", user.first_name)
        convo.reset()
        dynamo.put_conversation_object(convo)
        twilio.send_sms("Reset completed, message me again to start from scratch", user)
        return None
        
    # add the latest message to the convo
    convo.add_message(message, username)

    # get the response from GPT3
    response = call_gpt(user, convo)
    print("response is: ", response)

    # save the convo to the database
    convo.add_message(response, "MyEJConcernBot")
    dynamo.put_conversation_object(convo)
    dynamo.put_user_object(user)

    # send the response to the user
    if not testing:
        #sleep for 5s
        sleep(5)
        twilio.send_sms(response, user)

    return response


def hello(event, context, testing=False):
    print("raw event is: ", event)

    # get the data we need from the event
    message = twilio.parse_response(event, "message")
    username = twilio.parse_response(event, "number")
    print("message is: ", message)
    print("username is: ", username)

    # check if the message is a json object
    if("{" in message):
        print("Message contains json! Looks like we're done!")
        json_object = json.loads(message)
        print("message JSON is: ", json_object)
    # process the data and get a response (prep prompt, call GPT3, save to database, send to user)


    process_incoming_message(username, message, testing)

    # return a success object
    return utils.get_success_object(event)



if __name__ == "__main__":
    username = (input("What is your username? ") or "+19192606035")
    new_convo = (input("Do you want to start a new conversation? (y/n) ") or "n")
    if new_convo == "y":
        convo = Conversation.from_username(username)
        convo.reset()
        dynamo.put_conversation_object(convo)
    user = User.from_username(username)
    name_to_use = user.first_name or "User"
    while True:
        input_message = input(name_to_use + ": ")
        encoded_input_message = urllib.parse.quote(input_message)
        cleaned_number = user.username[1:]
        fake_event = {"body":"Body:"+encoded_input_message+"&FromCo"+"From=aaa"+cleaned_number+"&Api"}
        hello(fake_event, None, True)
        if input_message == "quit":
            break 
            