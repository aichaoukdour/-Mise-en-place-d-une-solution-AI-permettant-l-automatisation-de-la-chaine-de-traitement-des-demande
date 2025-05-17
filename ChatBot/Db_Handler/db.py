from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from django.conf import settings
from sqlalchemy.orm import Session
from ChatBot.model import ChtBt 
from datetime import datetime
import uuid
from sqlalchemy import func, and_, select
from sqlalchemy.orm import sessionmaker


from Db_handler.data_encrypt import *

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
    def get_session(self):
        if self.SessionLocal is None:
            raise Exception("SessionLocal is not initialized. Database connection failed.")
        return self.SessionLocal()

    def insert_chat(self, msg, date, user_id, id_conv):
        session = self.get_session()
        try:
            new_msg = ChtBt(
                msg_user=encrypt(msg),
                dt_msg=date,
                conv_id=id_conv,
                user_id=user_id
            )
            session.add(new_msg)
            session.commit()
            print(f"Chat message inserted with ID: {new_msg.mes_id}")
            return str(new_msg.mes_id)
        except Exception as e:
            session.rollback()
            print(f"Failed to insert chat message: {e}")
            return None
        finally:
            session.close()

    def historique(self, user_id):
        session = self.get_session()
        try:
            # Subquery to get earliest message per conv_id
            subquery = (
                session.query(
                    ChtBt.conv_id,
                    func.min(ChtBt.dt_msg).label("min_dt")
                )
                .group_by(ChtBt.conv_id)
                .subquery()
            )

            # Join with main table to get message content
            result = (
                session.query(ChtBt)
                .join(subquery, and_(
                    ChtBt.conv_id == subquery.c.conv_id,
                    ChtBt.dt_msg == subquery.c.min_dt
                ))
                .filter(ChtBt.user_id == user_id)
                .order_by(ChtBt.dt_msg.asc())
                .all()
            )

            return [
                {
                    "conv_id": row.conv_id or "",
                    "subject": decrypt(row.msg_user) if row.msg_user else "",
                    "date_u": row.dt_msg or ""
                }
                for row in result
            ]
        except Exception as e:
            print(f"Failed to fetch history: {e}")
            return []
        finally:
            session.close()
    def insert_res_msg(self, msg_r, dt_r, id_msg, sql_r, ct_msg):
        session = self.get_session()
        try:
            msg_obj = session.query(ChtBt).filter_by(mes_id=id_msg).first()
            if not msg_obj:
                print("Message not found.")
                return False

            msg_obj.res_user = encrypt(msg_r)
            msg_obj.dt_res_user = dt_r
            msg_obj.req_sql = encrypt(sql_r) if sql_r else None
            msg_obj.ct_msg = ct_msg

            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Failed to update message: {e}")
            return False
        finally:
            session.close()
    def get_all_msg_con(self, conv_id, user_id):
        session = self.get_session()
        try:
            messages = (
                session.query(ChtBt)
                .filter(ChtBt.conv_id == conv_id, ChtBt.user_id == user_id)
                .order_by(ChtBt.dt_msg)
                .all()
            )

            return [
                {
                    "msg_id": str(msg.mes_id) if msg.mes_id else "",
                    "msg_user": decrypt(msg.msg_user) if msg.msg_user else "",
                    "req_sql": decrypt(msg.req_sql) if msg.req_sql else "",
                    "res_user": decrypt(msg.res_user) if msg.res_user else "",
                    "ct_ms": msg.ct_msg if msg.ct_msg else "",
                    "user_id": msg.user_id if msg.user_id else "",
                    "date_rec": msg.dt_res_user.strftime("%H:%M") if msg.dt_res_user else "",
                    "date_env": msg.dt_msg.strftime("%H:%M") if msg.dt_msg else "",
                    "conv_id": msg.conv_id if msg.conv_id else ""
                }
                for msg in messages
            ]
        except Exception as e:
            print(f"Failed to fetch chat messages: {e}")
            return []
        finally:
            session.close()


    def close(self):
        if self.engine:
            self.engine.dispose()