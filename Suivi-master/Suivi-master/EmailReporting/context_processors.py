# auth_views.py
from Db_handler import EmailDatabase

EmailDatabase_instance = EmailDatabase()

def user_info(request):
    email_user = request.session.get('email_user')
    name_user = ''
    email_user_db = ''
    
    if email_user:
        name_user, email_user_db = EmailDatabase_instance.gey_name_user(email_user)

    return {
        'name_user': name_user,
        'email_user': email_user_db,
    }