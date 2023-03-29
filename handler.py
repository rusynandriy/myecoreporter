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

    # call GPT3
    response = gpt3.gpt3_completion(convo.chat)

    return response

def process_incoming_message(username, message, testing):
    # print(f"processing incoming message {message} from {username}")

    # get the user and convo from the database (if they exist, otherwise create them)
    user = User.from_username(username)
    convo = Conversation.from_username(username)
    
    # dev thing to help with testing. Can also be used by users if they get stuck.
    if("RESET" == message.strip().upper()): 
        print("ending convo, they just hit the reset button!")
        convo.add_message("RESET", username)
        convo.reset()
        dynamo.put_conversation_object(convo)
        # send the response to the user
        if not testing:
            twilio.send_sms("Reset completed, message me again to start from scratch", user)
            return None
        
    


    # add the latest message to the convo
    convo.add_message(message, username)

    # get the response from GPT3
    response = call_gpt(user, convo)

    # handle JSON in the response.
    if "{" in response and "}" in response:
        # print("Message contains json! Let's format it!")
        # print("""response.rindex("}")+1""", response.rindex("}")+1)
        # print("""response.index("{")""", response.index("{"))
        json_string = utils.extract_json(response)
        json_object = json.loads(json_string)
        # print("message JSON is: ", json_object)
        formatted_summary = ""
        for key in json_object:
            formatted_summary += f"\n{key}: {json_object[key]}"
        response = response.replace(json_string, formatted_summary)
        # print("response (without JSON) is now: ", response)
        # process the data and get a response (prep prompt, call GPT3, save to database, send to user)
        convo.add_message(response, username)
        dynamo.put_conversation_object(convo)
    
    # we need to remove timestamps before we send the response to the user
    if "(" in response and ")" in response:
        response = response[22:]

    # save the convo to the database
    convo.add_message(response, "MyEcoReporter")
    dynamo.put_conversation_object(convo)
    dynamo.put_user_object(user)
    print("MyEcoReporter:", response)
    # send the response to the user
    if not testing:
        #sleep for 5s
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
            
        twilio.send_sms(response, user)

    return response


def hello(event, context, testing=False):
    print("raw event is: ", event)

    # get the data we need from the event
    message = twilio.parse_response(event, "message")
    username = twilio.parse_response(event, "number")
    print("message is: ", message)
    print("username is: ", username)

    
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
            