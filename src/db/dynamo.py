import boto3
import os
from boto3.dynamodb.conditions import Key
from datetime import datetime as dt

# DynamoDB setup
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
client = boto3.resource('dynamodb')
chatsTable = client.Table("ejchats")
usersTable = client.Table("ejusers")

# DynamoDB helpers
def put_user_object(user):
    usersTable.put_item(Item= {'username': user.username, 'first_name': user.first_name, 'location':user.location, 'created_at':user.created_at, 'last_updated_at':dt.now().strftime("%Y-%m-%d %H:%M:%S")}) 

def put_conversation_object(conversation):
    if(conversation.chat_status == "BRANDNEW"):
        chatsTable.put_item(Item= {'username': conversation.username, 'conversation_text':  conversation.chat, 'started_at': conversation.started_at})
    elif(conversation.chat_status == "ONGOING"):
        chatsTable.update_item(
                Key= {'username': conversation.username, 'started_at': conversation.started_at},
                UpdateExpression="set conversation_text=:conversation_text",
                ExpressionAttributeValues={':conversation_text': conversation.chat},
                ReturnValues="UPDATED_NEW"
            )
    elif(conversation.chat_status == "NEWFORUSER"):
        chatsTable.put_item(Item= {'username': conversation.username, 'conversation_text':  conversation.chat, 'started_at': conversation.started_at})
    elif(conversation.chat_status == "COMPLETED"):
        chatsTable.put_item(Item= {'username': conversation.username, 'conversation_text':  conversation.chat, 'started_at': conversation.started_at, 'completed_at': conversation.completed_at})        
    else:
        print("unknown chat status, FATAL ERROR!")

def get_user(username):
    # this returns the latest. Note you have to use False isntead of True like the original SO post says (see comments)
    # https://stackoverflow.com/questions/12809295/nosql-getting-the-latest-values-from-tables-dynamodb-azure-table-storage
    return usersTable.query(KeyConditionExpression=Key('username').eq(username), ScanIndexForward=False, Limit=1)
    
def get_users():
    return usersTable.scan()

def get_conversation(username):
    # this returns the latest. Note you have to use False isntead of True like the original SO post says (see comments)
    # https://stackoverflow.com/questions/12809295/nosql-getting-the-latest-values-from-tables-dynamodb-azure-table-storage
    return chatsTable.query(KeyConditionExpression=Key('username').eq(username), ScanIndexForward=False, Limit=1)

def get_all_conversations():
    return chatsTable.scan()
    
def get_conversations(username):
    return chatsTable.query(KeyConditionExpression=Key('username').eq(username), ScanIndexForward=False)

def get_conversations_since_date(username, date):
    return chatsTable.query(KeyConditionExpression=Key('username').eq(username) & Key('started_at').gt(date), ScanIndexForward=False)

def get_users_raw():
    return usersTable.scan()

def delete_conversation(username, started_at):
    chatsTable.delete_item(Key={'username': username, 'started_at': started_at})

def delete_conversations(username):
    conversations = get_conversations(username)
    for conversation in conversations['Items']:
        delete_conversation(username, conversation['started_at'])