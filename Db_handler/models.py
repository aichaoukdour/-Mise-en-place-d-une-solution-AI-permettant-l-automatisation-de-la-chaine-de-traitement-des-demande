from typing import Optional

class User:
    def __init__(self, user_id: str, name_user: str, last_name_user: str, email_user: str, user_role: str, user_id_field: Optional[int] = None):
        self.user_id = user_id
        self.name_user = name_user
        self.last_name_user = last_name_user
        self.email_user = email_user
        self.user_role = user_role
        self.id = user_id_field 