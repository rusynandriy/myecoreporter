import src.db.dynamo as dynamo
from datetime import datetime as dt, timedelta
import pytz

class Conversation:
    def __init__(self, username, chat, chat_status, started_at, completed_at):
        self.username = username
        self.chat = chat
        self.chat_status = chat_status # BRANDNEW/NEWFORUSER/ONGOING/COMPLETED
        self.started_at = started_at
        self.completed_at = completed_at

    def __init__(self):
        self.username = ""
        self.chat = list()
        self.chat_status = ""
        self.started_at = ""
        self.completed_at = ""

    @classmethod
    def from_username(cls, username):
        dynamo_db_item = dynamo.get_conversation(str(username))
        convo = Conversation()
        convo.username = username

        try:
            convo.chat = list(dynamo_db_item["Items"][0]["conversation_text"])
            if(len(convo.chat))>=0 or convo.rating == "RESET":
                try:
                    # if it has a completed_at value, it's already done, so we'll start a new one
                    convo.completed_at = dynamo_db_item["Items"][0]["completed_at"]
                    convo.chat = list()
                    convo.chat_status = "NEWFORUSER"
                    convo.started_at = str(dt.now(pytz.timezone("UTC")))
                except:
                    # if there's no completed_at key, it's an ongoing convo and we need the started_at time for later since it's our Sort Key
                    try:
                        convo.started_at = dynamo_db_item["Items"][0]["started_at"]
                    except:
                        print("Fatal error, how is there no started_at for an existing convo??!?!") 
                    convo.chat_status = "ONGOING"

        except:
            # first time user's first ever convo
            convo.conversation = list()
            convo.started_at = str(dt.now(pytz.timezone("UTC")))
            convo.chat_status = "BRANDNEW"
        return convo

    def add_message(self, message, sender_name, with_timestamp=True, gmt_offset=""):
        if with_timestamp:
            hours_mins_now = dt.now().strftime("%H:%M")
            # if gmt_offset is not blank, use the value to calculate the time
            if gmt_offset != "":
                hours_mins_now = str((int(hours_mins_now.split(":")[0]) + int(gmt_offset.split(":")[0])) % 24) + ":" + hours_mins_now.split(":")[1]
                # pad with a 0 if it's a single digit
                if len(hours_mins_now.split(":")[0]) == 1:
                    hours_mins_now = "0" + hours_mins_now
            message = f'({hours_mins_now}) {sender_name}: {message}'
        else:
            message = f'{sender_name}: {message}'
        self.chat.append(message)

    def complete(self, rating=""):
        completed_at = str(dt.now())
        if rating != "":
            self.rating = rating
        self.chat_status = "COMPLETED"
        self.completed_at = completed_at
        
    def reset(self):
        completed_at = str(dt.now())
        self.rating = "RESET"
        self.chat_status = "COMPLETED"
        self.completed_at = completed_at
        