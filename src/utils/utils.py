import json

# used to return a "hey, everything went OK" response to Twilio.
def get_success_object(event):
    return {
            "statusCode": 200,
            "isBase64Encoded": False,
            "headers": None,
            "body": event['body']
        }
    
# extracts the entire JSON string and returns it
def extract_json(message):
    return message[message.index("{"):message.rindex("}")+1]

# clears out the JSON string in a message
def strip_json(message):
    json_string = message[message.index("{"):message.rindex("}")+1]
    return message.replace(json_string, "")

# opens a file (primarily used for loading secrets)
def open_file(filepath): 
    try:
        with open(filepath, 'r', encoding='utf-8') as infile:
            return infile.read()
    except:
        return False
    
# takes a string with JSON, fixes it, and returns the value of a given key.
def get_key_from_json(json_string, key):
    raw_json = r"{}".format(json_string)
    json_object = fix_and_load_json(raw_json)
    try:
        return json_object[key]
    except:
        return None

# fixes common errors in GPT-generated JSON. Things like double quotes, etc can throw off json.loads, so we replace those before returning a working JSON dictionary.
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