# import standard python libraries
import json
from datetime import datetime as dt
import pdb
from time import sleep
import urllib.parse


# import our custom utilities + helper classes
import src.utils.twilio_utils as twilio
import src.gpt3 as gpt3
import src.db.dynamo as dynamo
import src.utils.utils as utils

# import our dynamo classes
from src.classes.conversation import Conversation
from src.classes.user import User


# make a data structure that maps state names like "nc" to a phone number, a prompt file, and a bot name
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
        "phone_number": "+18332729100",
        "bot_name": "MyEcoReporterHarris",
        "prompt_filename": "assets/prompts/harris_prompt.txt"
    },
    "ca": {
        "phone_number": "+16507191736",
        "bot_name": "Prop 65 Bot",
        "prompt_filename": "assets/prompts/ca_prompt.txt"
    }
}

def process_incoming_message(username, message, testing, state):
    # get the user and convo from the database (if they exist, otherwise create them)
    user = User.from_username(username)
    convo = Conversation.from_username(username)
    
        
    # pull the relevant state settings from the dictionary
    phone_number = state_settings[state]["phone_number"]
    bot_name = state_settings[state]["bot_name"]
    prompt_filename = state_settings[state]["prompt_filename"]

    # if the chat is only 1 message long, send a custom additional warning message:
    if len(convo.chat) == 0:
        demo_warning_message = "Please note that this is a DEMO ONLY. Your reports will NOT actually be submitted! Text 'RESET' to start over at any time."
        print(bot_name + ": "+ demo_warning_message)
        twilio.send_sms(demo_warning_message, user, phone_number)

    # check the started_at time to see if it's been more than 4 days since the last message
    # if it's been that long, send the user a suggestion to RESET.
    if convo.started_at:
        # this is the format: 2023-02-08 18:12:44.567191+00:00
        convo_started_at_dt = dt.strptime(convo.started_at, "%Y-%m-%d %H:%M:%S.%f%z")
        # get rid of the timezone info
        convo_started_at_dt = convo_started_at_dt.replace(tzinfo=None)
        time_since_convo_started = dt.now() - convo_started_at_dt
        if time_since_convo_started.days > 4:
            response = "It looks like our last chat was more than 4 days ago. If you want to restart and have a new conversation, please text 'RESET'."
            convo.add_message(response, username)
            dynamo.put_conversation_object(convo)
            print(bot_name+": "+response)
            # send the response to the user
            if not testing:
                twilio.send_sms(response, user, phone_number)
    
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
    response = gpt3.chatgpt_completion(convo.chat, prompt_filename, bot_name)

    # handle JSON in the response if it is present.
    # "handle" here just means to clean it up a bit for presentation to the User
    if "{" in response and "}" in response:
        json_string = utils.extract_json(response)
        json_object = json.loads(json_string)
        formatted_summary = ""
        for key in json_object:
            formatted_summary += f"\n{key}: {json_object[key]}"
        response = response.replace(json_string, formatted_summary)
    
    # we need to remove timestamps before we send the response to the user if GPT accidentally added some as part of the response
    if ")" in response[:30]:
        response = response[response.find(")")+1:]

    # save the Conversation and User objects to the database
    convo.add_message(response, bot_name)
    dynamo.put_conversation_object(convo)
    dynamo.put_user_object(user)
    
    # send the response to the user (but only if we're not Smoke Testing locally)
    if testing:
        # print the response to the console if we're testing
        print(bot_name+": "+response)
    else:    
        # send an SMS if we're NOT testing
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
    # setup for local smoke testing: ask for Username, Convo Reset, + State to use
    username = (input("What is your username? ") or "+19192606035")
    new_convo = (input("Do you want to start a new conversation? (y/n) ") or "n")
    state = (input("What state are you in? (nc, tceq, harris, ca) ") or "nc")
    
    # if we want to test a new convo, reset it and load a fresh one
    if new_convo == "y":
        convo = Conversation.from_username(username)
        convo.reset()
        dynamo.put_conversation_object(convo)
        
    # get the correct name to use (User in all cases for now)
    user = User.from_username(username)
    name_to_use = user.first_name or "User"
    
    # keep sending messages back and forth until the user sends "quit" (you can also use the CTRL+C shortcut to kill the running terminal process)
    while True:
        input_message = input(name_to_use + ": ")
        # take the user's message + URL encode it to match what Twilio does
        encoded_input_message = urllib.parse.quote(input_message)
        cleaned_number = user.username[1:] # remove the leading '+' on the phone number
        fake_event = {"body":"Body:"+encoded_input_message+"&FromCo"+"From=aaa"+cleaned_number+"&Api"}
        # call the correct method based on which state the user wants to test. 
        # NOTE that we pass in a testing=True parameter to avoid sending texts while testing locally.
        if state == "nc":
            hello_nc(fake_event, None, testing=True)
        elif state == "tceq":
            hello_tceq(fake_event, None, testing=True)
        elif state == "harris":
            hello_harris(fake_event, None, testing=True)
        elif state == "ca":
            hello_ca(fake_event, None, testing=True)
        if input_message == "quit":
            break 
            