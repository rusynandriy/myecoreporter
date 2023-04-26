# import standard python libraries
import json
from datetime import datetime as dt
import pdb
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


# make a data structure that maps state names like "nc" to a phone number and a bot name
state_settings = {
    "nc": {
        "phone_number": "+19799852909",
        "bot_name": "MyEcoReporterNC",
        "prompt_filename": "assets/prompts/nc_prompt.txt"
    },
    "tceq": {
        "phone_number": "+18453353583",
        "bot_name": "MyEcoReporterTCEQ",
        "prompt_filename": "assets/prompts/tceq_prompt.txt"
    },
    "harris": {
        "phone_number": "+13462143548",
        "bot_name": "MyEcoReporterHarris",
        "prompt_filename": "assets/prompts/harris_prompt.txt"
    },
    "ca": {
        "phone_number": "+16507191736",
        "bot_name": "Prop 65 Bot",
        "prompt_filename": "assets/prompts/ca_prompt.txt"
    },
}

def call_gpt(user, convo, prompt_filename, bot_name):
    # call GPT3
    response = gpt3.gpt3_completion(convo.chat, prompt_filename, bot_name)
    return response

def process_incoming_message(username, message, testing, state):
    # get the user and convo from the database (if they exist, otherwise create them)
    user = User.from_username(username)
    convo = Conversation.from_username(username)
    phone_number = state_settings[state]["phone_number"]
    bot_name = state_settings[state]["bot_name"]
    prompt_filename = state_settings[state]["prompt_filename"]
    
    # dev thing to help with testing. Can also be used by users if they get stuck.
    if("RESET" == message.strip().upper()): 
        print("ending convo, they just hit the reset button!")
        convo.add_message("RESET", username)
        convo.reset()
        dynamo.put_conversation_object(convo)
        # send the response to the user
        if not testing:
            twilio.send_sms("Reset completed, message me again to start from scratch", user, phone_number)
        return None
        
        
    # add the latest message to the convo
    convo.add_message(message, username)
    
    # get the response from GPT3
    response = call_gpt(user, convo, prompt_filename, bot_name)

    # handle JSON in the response.
    if "{" in response and "}" in response:
        json_string = utils.extract_json(response)
        json_object = json.loads(json_string)
        formatted_summary = ""
        for key in json_object:
            formatted_summary += f"\n{key}: {json_object[key]}"
        response = response.replace(json_string, formatted_summary)
    
    # we need to remove timestamps before we send the response to the user
    if ")" in response[:30]:
        response = response[response.find(")")+1:]

    # save the convo to the database
    convo.add_message(response, bot_name)
    dynamo.put_conversation_object(convo)
    dynamo.put_user_object(user)
    print(bot_name+": "+response)
    # send the response to the user
    if not testing:
        # sleep for 5s
        # sleep(5)
        # we need to clean up the message a bit. It may contain timestamps like this: 
        # "(2023-03-06 11:44:00) (2023-03-06 11:43:59) (2023-03-06 11:43:59) (2023-03-06 11:44:11) Okay, I will make that correction. Thank you for letting me know! Let's confirm the information I have so far"
        # we need to remove the timestamps inline without using any other functions
        # if "(" in response and ")" in response:
            # print("response contains timestamps, cleaning them up")
            # clean_message = ""
            # for word in response.split(" "):
            #     if "(" in word and ")" in word:
            #         continue
            #     clean_message += word + " "
            # print("clean message is: ", clean_message)
            # response = clean_message  
        twilio.send_sms(response, user, phone_number)
    return response


def hello_nc(event, context, testing=False):
    # get the data we need from the event
    message = twilio.parse_response(event, "message")
    username = twilio.parse_response(event, "number")
    print("message is: ", message)
    print("username is: ", username)

    # process the data and get a response (prep prompt, call GPT3, save to database, send to user)
    process_incoming_message(username, message, testing, "nc")

    # return a success object
    return utils.get_success_object(event)

def hello_tceq(event, context, testing=False):
    # get the data we need from the event
    message = twilio.parse_response(event, "message")
    username = twilio.parse_response(event, "number")
    print("message is: ", message)
    print("username is: ", username)

    # process the data and get a response (prep prompt, call GPT3, save to database, send to user)
    process_incoming_message(username, message, testing, "tceq")

    # return a success object
    return utils.get_success_object(event)

def hello_harris(event, context, testing=False):
    # get the data we need from the event
    message = twilio.parse_response(event, "message")
    username = twilio.parse_response(event, "number")
    print("message is: ", message)
    print("username is: ", username)
    
    # process the data and get a response (prep prompt, call GPT3, save to database, send to user)
    process_incoming_message(username, message, testing, "harris")

    # return a success object
    return utils.get_success_object(event)

def hello_ca(event, context, testing=False):
    # get the data we need from the event
    message = twilio.parse_response(event, "message")
    username = twilio.parse_response(event, "number")
    print("message is: ", message)
    print("username is: ", username)
    
    # process the data and get a response (prep prompt, call GPT3, save to database, send to user)
    process_incoming_message(username, message, testing, "ca")

    # return a success object
    return utils.get_success_object(event)

if __name__ == "__main__":
    username = (input("What is your username? ") or "+19192606035")
    new_convo = (input("Do you want to start a new conversation? (y/n) ") or "n")
    state = (input("What state are you in? (nc, tceq, harris, ca) ") or "nc")
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
        if state == "nc":
            hello_nc(fake_event, None, True)
        elif state == "tceq":
            hello_tceq(fake_event, None, True)
        elif state == "harris":
            hello_harris(fake_event, None, True)
        elif state == "ca":
            hello_ca(fake_event, None, True)
        if input_message == "quit":
            break 
            