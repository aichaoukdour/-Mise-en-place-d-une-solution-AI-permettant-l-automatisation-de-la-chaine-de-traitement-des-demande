from typing import Optional

class User:
    def __init__(self, user_id, name_user, last_name_user, email_user, user_role, is_first_login=True):
        self.user_id = user_id
        self.name_user = name_user
        self.last_name_user = last_name_user
        self.email_user = email_user
        self.user_role = user_role
        self.is_first_login = is_first_login

    @property
    def id(self):
        return self.user_id

    @property
    def is_authenticated(self):
        return True