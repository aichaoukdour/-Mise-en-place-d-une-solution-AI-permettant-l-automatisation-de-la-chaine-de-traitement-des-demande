from typing import Optional

class User:
    def __init__(self, user_id, name_user, last_name_user, email_user, user_role):
        self.user_id = user_id
        self.name_user = name_user
        self.last_name_user = last_name_user
        self.email_user = email_user
        self.user_role = user_role

    @property
    def id(self):
        return self.user_id  # Use user_id as the id for JWT