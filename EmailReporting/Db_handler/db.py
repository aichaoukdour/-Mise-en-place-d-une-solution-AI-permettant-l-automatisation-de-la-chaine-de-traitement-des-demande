from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from django.conf import settings
from EmailReporting.Db_handler.model import *
from Db_handler.data_encrypt import *
from Db_handler.models import User


Base = declarative_base()

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None  # ajouter ceci
        self._connect()
        self._create_tables()

    def _connect(self):
        try:
            db_settings = settings.DATABASES['default']
            self.connection_string = (
                f"postgresql+psycopg2://{db_settings['USER']}:{db_settings['PASSWORD']}"
                f"@{db_settings['HOST']}:{db_settings['PORT']}/{db_settings['NAME']}"
            )
            self.engine = create_engine(self.connection_string)
            self.SessionLocal = sessionmaker(bind=self.engine)  # session liée au moteur
            print("Database connection established.")
        except SQLAlchemyError as e:
            print(f"Error connecting to the database: {e}")
            self.engine = None
        except KeyError as e:
            print(f"Missing database configuration key: {e}")
            self.engine = None
    def _create_tables(self):
        if self.engine is None:
            print("Engine is not initialized. Connection failed.")
            return
        try:
            Base.metadata.create_all(self.engine)
            print("Tables created successfully.")
        except SQLAlchemyError as e:
            print(f"Error creating tables: {e}")
    def Session(self):
        if self.SessionLocal is None:
            raise Exception("SessionLocal is not initialized. Database connection failed.")
        return self.SessionLocal()
    def email_check(self, email, password):
        session = self.Session()
        try:
            print(f"Reçu email: {email}, password: {password}")

            hashed_email = hash_email(email)
            hashed_password = hash_email(password)
            print(f"Hashed email: {hashed_email}, Hashed password: {hashed_password}")
            user = session.query(UserInwi).filter_by(user_id=hashed_email, password=hashed_password).first()
            print(f"User: {user}")

            if user:
                user_object = User(
                    user_id=user.user_id,
                    name_user=user.name_user,
                    last_name_user=user.last_name_user,
                    email_user=user.email_user,
                    user_role=user.user_role,
                )
                print(f"User object: {user_object}")
                return True, user_object
            
            return False, None

            
        except Exception as e:
            print(f"Failed to fetch data: {e}")
            return False, None
        finally:
            session.close()
    def user_by_id(self, user_id):
        session = self.Session()
        try:
            user = session.query(UserInwi).filter_by(user_id=user_id).first()
            if user:
                return {
                    "user_id": user.user_id,
                    "email_user": decrypt(user.email_user),
                    "user_role": user.user_role,
                    "name_user": user.name_user,
                    "last_name_user": user.last_name_user
                }
            return None
        except Exception as e:
            print(f"Failed to fetch data: {e}")
            return None
        finally:
            session.close()
    def update_user(self, name_user, last_name_user, email_user, user_role, user_id):
        session = self.Session()
        try:
            user = session.query(UserInwi).filter_by(user_id=user_id).first()
            if user:
                user.name_user = name_user
                user.last_name_user = last_name_user
                user.user_role = user_role
                user.email_user = hash_email(email_user)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Failed to update data: {e}")
            return False
        finally:
            session.close()
    def get_all_mail_user(self, email_rec):
        session = self.Session()
        try:
            emails = session.query(EmailLo).filter_by(email_rec=email_rec).order_by(EmailLo.date_rec.desc()).all()
            return [
                {
                    "email_rec": decrypt(email.email_rec),
                    "date_rec": email.date_rec,
                    "subject": email.subject,
                    "body": decrypt(email.body),
                    "body_env": decrypt(email.body_env),
                    "date_env": email.date_env,
                    "status": email.status,
                    "id_mail": email.id,
                    "conversation_id": email.conversation_id
                }
                for email in emails
            ]
        except Exception as e:
            print(f"Failed to fetch data: {e}")
            return []
        finally:
            session.close()
    def create_user(self, name_user, last_name_user, email_user, user_role, password):
        session = self.Session()
        try:
            user = UserInwi(
                name_user=name_user,
                last_name_user=last_name_user,
                email_user=encrypt(email_user),
                user_role=user_role,
                user_id=hash_email(email_user),
                password=hash_email(password)
            )
            session.add(user)
            session.commit()
            return True
        except Exception as e:
            print(f"Failed to create user: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    def all_roles(self):
        session = self.Session()
        try:
            roles = session.query(UserRole).all()
            return [role.user_role for role in roles]
        except Exception as e:
            print(f"Failed to fetch roles: {e}")
            return []
        finally:
            session.close()       
    def get_alls_users(self):
        session = self.Session()
        try:
            users = session.query(UserInwi).filter(UserInwi.user_role != 'admin').all()
            return [
                {
                    "name": user.name_user or "",
                    "last_name": user.last_name_user or "",
                    "email": decrypt(user.email_user) if user.email_user else "",
                    "user_role": user.user_role or "",
                    "email_user": user.email_user or "",
                    "user_id": user.user_id or ""
                }
                for user in users
            ]
        except Exception as e:
            print(f"Failed to fetch data: {e}")
            return []
        finally:
            session.close()
    def get_all_mails(self):
        session = self.Session()
        try:
            mails = session.query(EmailLo).order_by(EmailLo.date_rec.desc()).all()
            return [
                {
                    "email_rec": decrypt(mail.email_rec) if mail.email_rec else "",
                    "date_rec": mail.date_rec,
                    "subject": mail.subject or "",
                    "body": decrypt(mail.body) if mail.body else "",
                    "body_env": decrypt(mail.body_env) if mail.body_env else "",
                    "date_env": mail.date_env,
                    "status": mail.status or "",
                    "id_mail": mail.id,
                    "conversation_id": mail.conversation_id or ""
                }
                for mail in mails
            ]
        except Exception as e:
                print(f"Failed to fetch data: {e}")
                return []
        finally:
                session.close()
    def get_all_mails_attente(self):
        session = self.Session()
        try:
            mails = session.query(EmailLo).filter(EmailLo.status == 'En attente').order_by(EmailLo.date_rec.desc()).all()
            return [
                {
                    "email_rec": decrypt(mail.email_rec) if mail.email_rec else "",
                    "date_rec": mail.date_rec,
                    "subject": mail.subject or "",
                    "body": decrypt(mail.body) if mail.body else "",
                    "body_env": decrypt(mail.body_env) if mail.body_env else "",
                    "date_env": mail.date_env,
                    "status": mail.status or "",
                    "id_mail": mail.id,
                    "diff_time": get_diff(mail.date_rec)  # Assuming get_diff is a utility function
                }
                for mail in mails
            ]
        except Exception as e:
            print(f"Failed to fetch data: {e}")
            return []
        finally:
            session.close()
    def get_all_mails_echous(self):
        session = self.Session()
        try:
            mails = session.query(EmailLo).filter(EmailLo.status == 'Failed').order_by(EmailLo.date_rec.desc()).all()
            return [
                {
                    "email_rec": decrypt(mail.email_rec) if mail.email_rec else "",
                    "date_rec": mail.date_rec,
                    "subject": mail.subject or "",
                    "body": decrypt(mail.body) if mail.body else "",
                    "body_env": decrypt(mail.body_env) if mail.body_env else "",
                    "date_env": mail.date_env,
                    "status": mail.status or "",
                    "id_mail": mail.id
                }
                for mail in mails
            ]
        except Exception as e:
            print(f"Failed to fetch data: {e}")
            return []
        finally:
            session.close()
    def get_mail_by_id(self, id_mail):
        session = self.Session()
        try:
            mail = session.query(EmailLo).filter_by(id=id_mail).first()
            if mail:
                return {
                    "email_rec": decrypt(mail.email_rec) if mail.email_rec else "",
                    "date_rec": mail.date_rec,
                    "subject": mail.subject or "",
                    "body": decrypt(mail.body) if mail.body else "",
                    "body_env": decrypt(mail.body_env) if mail.body_env else "",
                    "date_env": mail.date_env,
                    "status": mail.status or "",
                    "id_mail": mail.id,
                    "cate_msg": mail.cate_msg or "",
                    "conversation_id": mail.conversation_id or ""
                }
            return None
        except Exception as e:
            print(f"Failed to fetch data: {e}")
            return None
        finally:
            session.close()
    def get_all_conversation(self):
        session = self.Session()
        try:
            subquery = session.query(EmailLo.conversation_id, func.min(EmailLo.date_rec).label('latest_date')).group_by(EmailLo.conversation_id).subquery()
            mails = session.query(EmailLo).join(subquery, (EmailLo.conversation_id == subquery.c.conversation_id) & (EmailLo.date_rec == subquery.c.latest_date)).all()
            
            return [
                {
                    "email_rec": decrypt(mail.email_rec) if mail.email_rec else "",
                    "date_rec": mail.date_rec,
                    "subject": mail.subject or "",
                    "body": decrypt(mail.body) if mail.body else "",
                    "body_env": decrypt(mail.body_env) if mail.body_env else "",
                    "date_env": mail.date_env,
                    "status": mail.status or "",
                    "id": mail.id,
                    "cate_msg": mail.cate_msg or "",
                    "conversation_id": mail.conversation_id
                }
                for mail in mails
            ]
        except Exception as e:
            print(f"Failed to fetch data: {e}")
            return []
        finally:
            session.close()
    def get_all_mail_by_conversation(self, conversation_id):
        session = self.Session()
        try:
            mails = session.query(EmailLo).filter(EmailLo.conversation_id == conversation_id).order_by(EmailLo.date_rec).all()
            if mails:
                subject = mails[0].subject if mails[0].subject else ""
                result = [
                    {
                        "email_rec": decrypt(mail.email_rec) if mail.email_rec else "",
                        "date_rec": mail.date_rec,
                        "subject": mail.subject or "",
                        "body": decrypt(mail.body) if mail.body else "",
                        "body_env": decrypt(mail.body_env) if mail.body_env else "",
                        "date_env": mail.date_env,
                        "status": mail.status or "",
                        "id": mail.id,
                        "cate_msg": mail.cate_msg or "",
                        "conversation_id": mail.conversation_id
                    }
                    for mail in mails
                ]
                return result, subject
            return [], ""
        except Exception as e:
            print(f"Failed to fetch data: {e}")
            return [], ""
        finally:
            session.close()
    def delete_user(self, id_user):
        session = self.Session()
        try:
            user = session.query(UserInwi).filter_by(user_id=id_user).first()
            if user:
                session.delete(user)
                session.commit()
                return True
            return False
        except Exception as e:
            print(f"Failed to fetch data: {e}")
            return False
        finally:
            session.close()
    def create_History(self, user_id, ip_addr, success, user_agent, date_l):
        session = self.Session()
        try:
            history = LoginHistory(user_id=user_id, ip_adress=ip_addr, success=success, user_agent=user_agent, date_l=date_l)
            session.add(history)
            session.commit()
            print("Login history inserted.")
            return True
        except Exception as e:
            print(f"Failed to insert login history: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    def get_name_user(self, user_id):
        session = self.Session()
        try:
            user = session.query(UserInwi).filter(UserInwi.email_user == user_id).first()
            if user:
                full_name = f"{user.name_user} {user.last_name_user}"
                return full_name, decrypt(user.email_user) if user.email_user else ""
            return "None", "None"
        except Exception as e:
            print(f"Failed to fetch data: {e}")
            return None, None
        finally:
            session.close()
    
def get_diff(date_tm):
    current_date = datetime.now()
    date_diff = current_date - date_tm
    hours = date_diff.days * 24 + date_diff.seconds // 3600
    minutes = (date_diff.seconds % 3600) // 60
    return f"{hours}h:{minutes}m"           
            