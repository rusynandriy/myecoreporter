from datetime import datetime as dt
import random
import ast
import src.db.dynamo as dynamo

class User:
    # used to instantiate a new User object with blank data
    def __init__(self):
        self.username = ''
        self.first_name = ''
        self.created_at = ''
        self.last_updated_at = ''
    
    # simple print method    
    def __str__(self):
        return f"""
        username: {self.username}
        first_name: {self.first_name}
        created_at: {self.created_at}
        last_updated_at: {self.last_updated_at}
        """

    # creates or returns a user given a username (phone numbers in this case). 
    @classmethod
    def from_username(cls, username):
        dynamo_db_item = dynamo.get_user(str(username))
        user = User()
        
        user.username = username
        try:
            user.first_name = dynamo_db_item["Items"][0]["first_name"]
            if user.first_name in ("", " ",[],[str()]) or len(user.first_name) < 2:
                user.first_name = "User"
        except:
            user.first_name = 'User'

        try:
            user.created_at = dynamo_db_item["Items"][0]["created_at"]
        except:
            user.created_at = ''
        try:
            user.last_updated_at = dynamo_db_item["Items"][0]["last_updated_at"]
        except:
            user.last_updated_at = ''
        return user
