from datetime import datetime as dt
import random
import ast
import src.db.dynamo as dynamo

class User:
    def __init__(self, username, first_name, last_updated_at=None, created_at=None, location=None):
        self.username = username
        self.first_name = first_name
        self.created_at = created_at
        self.last_updated_at = last_updated_at
        self.location = location

    def __init__(self):
        self.username = ''
        self.first_name = ''
        self.created_at = ''
        self.last_updated_at = ''
        self.location = ''
    
    def __str__(self):
        return f"""
        username: {self.username}
        first_name: {self.first_name}
        created_at: {self.created_at}
        last_updated_at: {self.last_updated_at}
        location: {self.location}
        """

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
        
        try:
            user.location = dynamo_db_item["Items"][0]["location"]
        except:
            user.location = ''
        return user
