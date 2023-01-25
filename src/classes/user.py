from datetime import datetime as dt
import random
import ast
import src.db.dynamo as dynamo

class User:
    def __init__(self, username, bot_name, first_name, habits, nudge_hour, nudge_message, time_zone, chat_id=None, created_at=None, last_updated_at=None, gmt_offset=None, about=None, location=None, last_weekly_review_at=None, pause_nudge_until=None, weekly_review_day=None ):
        self.username = username
        self.bot_name = bot_name
        self.first_name = first_name
        self.habits = habits
        self.nudge_hour = nudge_hour
        self.nudge_message = nudge_message
        self.time_zone = time_zone
        self.chat_id = chat_id
        self.created_at = created_at
        self.last_updated_at = last_updated_at
        self.gmt_offset = gmt_offset
        self.about = about
        self.location = location
        self.last_weekly_review_at = last_weekly_review_at
        self.pause_nudge_until = pause_nudge_until
        self.weekly_review_day = weekly_review_day

    def __init__(self):
        self.username = ''
        self.bot_name = ''
        self.first_name = ''
        self.habits = []
        self.nudge_hour = ''
        self.nudge_message = ''
        self.time_zone = ''
        self.chat_id = ''
        self.created_at = ''
        self.last_updated_at = ''
        self.gmt_offset = ''
        self.about = ''
        self.location = ''
        self.last_weekly_review_at = ''
        self.pause_nudge_until = ''
        self.weekly_review_day = ''
    
    def __str__(self):
        return f"""
        Username: {self.username}
        Bot Name: {self.bot_name}
        First Name: {self.first_name}
        Habits: {self.habits}
        Nudge Hour: {self.nudge_hour}
        Nudge Message: {self.nudge_message}
        Time Zone: {self.time_zone}
        Chat ID: {self.chat_id}
        Created At: {self.created_at}
        Last Updated At: {self.last_updated_at}
        GMT Offset: {self.gmt_offset}
        About: {self.about}
        Location: {self.location}
        Last Weekly Review At: {self.last_weekly_review_at}
        Pause Nudge Until: {self.pause_nudge_until}
        Weekly Review Day: {self.weekly_review_day}
        """

    @classmethod
    def from_username(cls, username):
        dynamo_db_item = dynamo.get_user(str(username))
        user = User()
        
        user.username = username
        try:
            user.bot_name = dynamo_db_item["Items"][0]["bot_name"]
            if user.bot_name in ("", " ",[],[str()]) or len(user.bot_name) < 2:
                user.bot_name = "Habit Coach AI"
        except:
            user.bot_name = "Habit Coach AI"
        try:
            user.first_name = dynamo_db_item["Items"][0]["first_name"]
            if user.first_name in ("", " ",[],[str()]) or len(user.first_name) < 2:
                user.first_name = "User"
        except:
            user.first_name = 'User'
        try:
            user.habits = dynamo_db_item["Items"][0]["habits"]
        except:
            user.habits = ''
        try:
            user.nudge_hour = dynamo_db_item["Items"][0]["nudge_hour"]
        except:
            user.nudge_hour = ''
        try:
            user.nudge_message = dynamo_db_item["Items"][0]["nudge_message"]
        except:
            user.nudge_message = ''
        try:
            user.time_zone = dynamo_db_item["Items"][0]["time_zone"]
        except:
            user.time_zone = ''
        try:
            user.chat_id = dynamo_db_item["Items"][0]["chat_id"]
        except:
            user.chat_id = ''
        try:
            user.created_at = dynamo_db_item["Items"][0]["created_at"]
        except:
            user.created_at = ''
        try:
            user.last_updated_at = dynamo_db_item["Items"][0]["last_updated_at"]
        except:
            user.last_updated_at = ''
        try:
            user.about = dynamo_db_item["Items"][0]["about"]
        except:
            user.about = ''
        try:
            user.location = dynamo_db_item["Items"][0]["location"]
        except:
            user.location = ''
        try:
            user.gmt_offset = dynamo_db_item["Items"][0]["gmt_offset"]
        except:
            user.gmt_offset = ''
        try:
            user.last_weekly_review_at = dynamo_db_item["Items"][0]["last_weekly_review_at"]
        except:
            user.last_weekly_review_at = ''    
        try:
            user.pause_nudge_until = dynamo_db_item["Items"][0]["pause_nudge_until"]
        except:
            user.pause_nudge_until = ''
        try:
            user.weekly_review_day = dynamo_db_item["Items"][0]["weekly_review_day"]
        except:
            user.weekly_review_day = ''
        return user


    def add_habit(self, new_habit):
        # do some cool stuff where we save a new habit to dynamo using literal_eval 
        habits_list = ast.literal_eval(str(self.habits))
        random.shuffle(habits_list)
        habits_list.append(new_habit)
        self.habits = habits_list
        dynamo.put_user_object(self)

    def remove_habit(self, habit):
        habit_to_remove = habit.lower()
        # parse from string in Dynamo back into python list
        # then lowercase everything so it works more reliably:
        habits_list = ast.literal_eval(str(self.habits))
        habits_list = [s.lower() for s in habits_list]
        # remove from the list
        if habit_to_remove in habits_list:
            habits_list.remove(habit_to_remove)
        self.habits = habits_list
        dynamo.put_user_object(self)
        print("saved updated habits list")
    
    # handle a new intent called "change_habit" by checking if the "old_habit" key is in the list of habits, and replacing it with "new_habit" if so
    def change_habit(self, old_habit, new_habit):
        old_habit = old_habit.lower()
        new_habit = new_habit.lower()
        
        habits_list = ast.literal_eval(str(self.habits))
        habits_list = [s.lower() for s in habits_list] 
        if old_habit in habits_list:
            habits_list.remove(old_habit)
        habits_list.append(new_habit)
        self.habits = habits_list
        dynamo.put_user_object(self)

    def get_bot_name_to_use(user):
        if user.bot_name not in ("", " ",[],[str()]):
            bot_name_to_use = user.bot_name 
        else:
            bot_name_to_use = "Habit Coach AI"
        return bot_name_to_use

    def change_nudge_hour(self, new_nudge_hour):
        self.nudge_hour = new_nudge_hour
        dynamo.put_user_object(self)

    def change_nudge_message(self, new_nudge_message):
        self.nudge_message = new_nudge_message
        dynamo.put_user_object(self)

    def change_bot_name(self, new_bot_name):
        self.bot_name = new_bot_name
        dynamo.put_user_object(self)

    def change_first_name(self, new_first_name):
        self.first_name = new_first_name
        dynamo.put_user_object(self)
        
    def change_time_zone(self, new_time_zone):
        self.time_zone = new_time_zone
        dynamo.put_user_object(self)
        
    def change_chat_id(self, new_chat_id):
        self.chat_id = new_chat_id
        dynamo.put_user_object(self)

    def get_habits(self):
        habits_list = ast.literal_eval(str(self.habits))
        return habits_list

    def get_nudge_hour(self):
        return self.nudge_hour

    def get_nudge_message(self):
        return self.nudge_message

    def get_bot_name(self):
        return self.bot_name

    def get_first_name(self):
        return self.first_name

    def get_time_zone(self):
        return self.time_zone

    def get_chat_id(self):
        return self.chat_id

    def get_last_weekly_review_at(self):
        return self.last_weekly_review_at