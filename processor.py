import src.db.dynamo as dynamo
from datetime import datetime as dt
import os

# normal python boilerplate for main 
if __name__ == "__main__":
    # get all the chats
    conversations = dynamo.get_all_conversations()
    print("conversations", conversations)

    # make a new folder for today's chats
    today = dt.now().strftime("%Y-%m-%d")
    os.mkdir(today)

    # loop through them and save them to that folder
    for conversation in conversations["Items"]:
        print("conversation", conversation)
        chat_log = conversation.get("conversation_text")
        print(chat_log)
        username = conversation.get("username")
        print(username)
        started_at = conversation.get("started_at")
        print("started at", started_at)
        with open(f"{today}/{username}_{started_at}.txt", "w") as f:
            for line in chat_log:
                f.write(line + "\n")