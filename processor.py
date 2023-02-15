import src.db.dynamo as dynamo
from datetime import datetime as dt
import os

# normal python boilerplate for main 
if __name__ == "__main__":
    # get all the chats
    conversations = dynamo.get_all_conversations()

    # make a new folder for today's chats

    today = dt.now().strftime("%Y-%m-%d")
    # try:
    os.mkdir("exports")
    os.mkdir("exports/"+today)
    # except:
    #     print("folder already exists")
    #     pass

    i = 0
    # loop through them and save them to that folder
    for conversation in conversations["Items"]:
        chat_log = conversation.get("conversation_text")
        username = conversation.get("username")
        started_at = conversation.get("started_at")
        # the started at will come back like this: 
        # 2023-02-09 16:37:02.512564+00:00
        # we want to make it like this:
        # 2023-02-09_16-37-02
        started_at = started_at.replace(" ", "_").replace(":", "-").split(".")[0]
        with open(f"exports/{today}/{username}_{started_at}.txt", "w") as f:
            for line in chat_log:
                f.write(line + "\n")
            f.close()
        i += 1