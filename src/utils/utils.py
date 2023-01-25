import json
from datetime import datetime as dt
import ast

def get_success_object(event):
    return {
            "statusCode": 200,
            "isBase64Encoded": False,
            "headers": None,
            "body": event['body']
        }
    
def extract_json(message):
    return message[message.index("{"):message.rindex("}")+1]

def strip_json(message):
    json_string = message[message.index("{"):message.rindex("}")+1]
    return message.replace(json_string, "")

def open_file(filepath): 
    try:
        with open(filepath, 'r', encoding='utf-8') as infile:
            return infile.read()
    except:
        return False
    
def get_key_from_json(json_string, key):
    raw_json = r"{}".format(json_string)
    json_object = fix_and_load_json(raw_json)
    try:
        return json_object[key]
    except:
        return None

def fix_and_load_json(jsonStr):
    jsonStr = jsonStr.replace("{'", '{"')
    jsonStr = jsonStr.replace("{I", '{"I')
    jsonStr = jsonStr.replace("':", '":')
    jsonStr = jsonStr.replace(" '", ' "')
    jsonStr = jsonStr.replace("' ", '" ')
    jsonStr = jsonStr.replace("',", '",')
    jsonStr = jsonStr.replace(",'", ',"')
    jsonStr = jsonStr.replace("']", '"]')
    # jsonStr = jsonStr.replace('""', '"')
    print("jsonStr: ", jsonStr)
    return json.loads(jsonStr, strict=False)