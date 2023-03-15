import glob
import json

import requests
import src.db.dynamo as dynamo
from datetime import datetime as dt
import os


def open_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as infile:
            return infile.read()
    except:
        return False

def push_to_airtable(file_name):
    # example file name: +12174195787_2023-02-09_17-41-46.txt
    # get the phone number (in this case +12174195787)
    filename_no_dirs = file_name.split("/")[-1]
    phone_number = filename_no_dirs.split("_")[0]
    print("phone number is ", phone_number)
    # get the timestamp (2023-02-09_17-41-46) and convert it to a datetime string that works with the airtable api like this: 
    # "2023-02-09T17:41:46.000Z"
    date_and_timestamp = filename_no_dirs.replace(phone_number+"_", "").split(".")[0] # gives us 2023-02-09_17-41-46
    formatted_datestamp = date_and_timestamp.split("_")[0] # gives us 2023-02-09
    formatted_timestamp = date_and_timestamp.split("_")[1].replace("-", ":") + ".000Z" # gives us 17-41-46
    formatted_date_and_timestamp = formatted_datestamp + "T" + formatted_timestamp
    print("formatted date and timestamp is ", formatted_date_and_timestamp)
    

    # get the conversation text
    with open(file_name, 'r') as f:
        conversation_text = f.read()

    # conversation_text = "\n".join(conversation_text)

    # put it all in a dict
    record = {
        "conversation_text": conversation_text,
        "started_at": formatted_date_and_timestamp,
        "Status": "Unreviewed"
    }
    
    # push it to airtable
    post_airtable_record(record)

def post_airtable_record(record, table_id=None):
    # get the airtable api key from the environment
    api_key = (open_file('secret/keys/airtable_api_key.txt') or os.getenv('AIRTABLE_API_KEY'))
    
    # get the airtable base id from the environment
    base_id = (open_file('secret/keys/airtable_base_id.txt') or os.getenv('AIRTABLE_BASE_ID'))
    
    # get the airtable table name from the environment
    table_id = (table_id or open_file('secret/keys/airtable_chats_table_id.txt') or os.getenv('AIRTABLE_TABLE_NAME'))
    
    # build the url for the request
    url = f'https://api.airtable.com/v0/{base_id}/{table_id}'
    
    # build the headers for the request
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # build the data for the request
    data = json.dumps({"fields": record})
    
    # make the request
    response = requests.post(url, headers=headers, data=data)

    # print the response
    print(response)
    print(response.text.encode('utf8'))

# normal python boilerplate for main 
if __name__ == "__main__":

    choice = input("What do you want to do? (1) Export all chats (2) Push chats to Airtable")
    if choice == "1":
        choice = input("1 (def) - all or 2 - since date?")
        # get all the chats
        conversations = dynamo.get_all_conversations()

        # make a new folder for today's chats

        today = dt.now().strftime("%Y-%m-%d")
        try:
            os.mkdir("exports/"+today)
        except:
            print("folder already exists")
            pass

        i = 0
        # loop through them and save them to that folder
        if choice == "2":
            since_date = input("What date do you want to start at? (YYYY-MM-DD)")
            since_date_dt = dt.strptime(since_date, "%Y-%m-%d")
        print("got this many conversations in total: ", len(conversations["Items"]))
        for conversation in conversations["Items"]:
            chat_log = conversation.get("conversation_text")
            username = conversation.get("username")
            started_at = conversation.get("started_at")
            # the started at will come back like this: 
            # 2023-02-09 16:37:02.512564+00:00
            # we want to make it like this:
            # 2023-02-09_16-37-02
            # if we have a since_date, we only want to save the chats that are after that date
            if choice == "2":
                started_at_dt = dt.strptime(started_at.split(" ")[0], "%Y-%m-%d")
                print("started at is ", started_at)
                print("since date is ", since_date)
                if started_at_dt < since_date_dt:
                    print("skipping this one")
                    continue
            started_at = started_at.replace(" ", "_").replace(":", "-").split(".")[0]
            try:
                with open(f"exports/{today}/{username}_{started_at}.txt", "w") as f:
                    for line in chat_log:
                        f.write(line + "\n")
                    f.close()
            except Exception as e:
                print("error writing file:")
                print(e)
            i += 1
    elif choice == "2":
        print("Supposed to push chats to Airtable")
        print("pushing ALL txt to airtable")
        folder = input("what folder?")
        # this folder will have files within it. Those files are what needs to be sent to airtable
        for file_name in glob.glob(folder + "/*.txt"):
            print("file name is ", file_name)
            push_to_airtable(file_name)
        print("done!")