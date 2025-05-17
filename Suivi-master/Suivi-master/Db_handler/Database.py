import psycopg2
import logging
from psycopg2 import pool
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from Db_handler.data_encrypt import encrypt, decrypt, hash_email
from Db_handler.models import User

# Configure logging
logger = logging.getLogger(__name__)

class EmailDatabase:
    _instance = None
    _connection_pool = None

    def __new__(cls):
        """Ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super(EmailDatabase, cls).__new__(cls)
            cls._instance._initialize_connection_pool()
        return cls._instance

    def _initialize_connection_pool(self):
        """Initialize a connection pool."""
        if EmailDatabase._connection_pool is None:
            try:
                EmailDatabase._connection_pool = psycopg2.pool.ThreadedConnectionPool(
                    minconn=1,
                    maxconn=5,  # Reduced for development; adjust for production
                    dbname=settings.DATABASES['default']['NAME'],
                    user=settings.DATABASES['default']['USER'],
                    password=settings.DATABASES['default']['PASSWORD'],
                    host=settings.DATABASES['default']['HOST'],
                    port=settings.DATABASES['default']['PORT']
                )
                logger.info("Database connection pool initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize connection pool: {e}")
                EmailDatabase._connection_pool = None

    def _get_connection(self):
        """Retrieve a connection from the pool."""
        if EmailDatabase._connection_pool is None:
            self._initialize_connection_pool()
        if EmailDatabase._connection_pool is None:
            logger.error("No connection pool available.")
            return None
        try:
            conn = EmailDatabase._connection_pool.getconn()
            logger.debug("Retrieved connection from pool.")
            return conn
        except Exception as e:
            logger.error(f"Failed to get connection from pool: {e}")
            return None

    def _release_connection(self, conn):
        """Return a connection to the pool."""
        if conn and EmailDatabase._connection_pool:
            EmailDatabase._connection_pool.putconn(conn)
            logger.debug("Returned connection to pool.")

    def close(self):
        """Close the connection pool."""
        if EmailDatabase._connection_pool:
            EmailDatabase._connection_pool.closeall()
            logger.info("Database connection pool closed.")
            EmailDatabase._connection_pool = None

    def email_check(self, email, password):
        conn = self._get_connection()
        if conn is None:
            logger.error("No database connection. Cannot fetch data.")
            return False, None
        cur = conn.cursor()
        try:
            query = "SELECT user_id, email_user, user_role, name_user, last_name_user FROM user_inwi WHERE user_id = %s AND password = %s LIMIT 1"
            cur.execute(query, (hash_email(email), hash_email(password)))
            result = cur.fetchone()
            if result:
                user_id, email_user, user_role, name_user, last_name_user = result
                return True, User(user_id, name_user, last_name_user, email_user, user_role)
            return False, None
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return False, None
        finally:
            cur.close()
            self._release_connection(conn)

    def user_by_id(self, user_id):
        conn = self._get_connection()
        if conn is None:
            logger.error("No database connection. Cannot fetch data.")
            return None
        cur = conn.cursor()
        try:
            query = "SELECT user_id, email_user, user_role, name_user, last_name_user FROM user_inwi WHERE user_id = %s LIMIT 1"
            cur.execute(query, (user_id,))
            result = cur.fetchone()
            if result:
                user_id, email_user, user_role, name_user, last_name_user = result
                return {
                    "user_id": user_id,
                    "email_user": decrypt(email_user),
                    "user_role": user_role,
                    "name_user": name_user,
                    "last_name_user": last_name_user
                }
            return None
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return None
        finally:
            cur.close()
            self._release_connection(conn)

    def Update_User(self, name_user, last_name_user, email_user, user_role, user_id):
        conn = self._get_connection()
        if conn is None:
            logger.error("No database connection. Cannot fetch data.")
            return False
        cur = conn.cursor()
        try:
            query = """
            UPDATE user_inwi
            SET name_user = %s, last_name_user = %s, user_role = %s, email_user = %s
            WHERE user_id = %s
            """
            cur.execute(query, (name_user, last_name_user, user_role, hash_email(email_user), user_id))
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return False
        finally:
            cur.close()
            self._release_connection(conn)

    def get_all_mail_user(self, email_rec):
        conn = self._get_connection()
        if conn is None or email_rec is None:
            logger.error("No database connection or invalid email_rec.")
            return []
        cur = conn.cursor()
        try:
            query = """
            SELECT email_rec, date_rec, subject, body, body_env, date_env, status, id, conversation_id
            FROM email_lo WHERE email_rec = %s ORDER BY date_rec DESC
            """
            cur.execute(query, (email_rec,))
            res = cur.fetchall()
            if res:
                return [
                    {
                        "email_rec": decrypt(row[0]) if row[0] else "",
                        "date_rec": row[1],
                        "subject": row[2] if row[2] else "",
                        "body": decrypt(row[3]) if row[3] else "",
                        "body_env": decrypt(row[4]) if row[4] else "",
                        "date_env": row[5] if row[5] else "",
                        "status": row[6] if row[6] else "",
                        "id_mail": row[7],
                        "conversation_id": row[8] if row[8] else ""
                    }
                    for row in res
                ]
            return []
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return []
        finally:
            cur.close()
            self._release_connection(conn)

    def create_user(self, name_user, last_name_user, email_user, user_role):
        conn = self._get_connection()
        if conn is None:
            logger.error("No database connection. Cannot fetch data.")
            return False
        cur = conn.cursor()
        try:
            query = """
            INSERT INTO user_inwi (name_user, last_name_user, email_user, user_role, user_id)
            VALUES (%s, %s, %s, %s, %s)
            """
            cur.execute(query, (name_user, last_name_user, encrypt(email_user), user_role, hash_email(email_user)))
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return False
        finally:
            cur.close()
            self._release_connection(conn)

    def all_roles(self):
        conn = self._get_connection()
        if conn is None:
            logger.error("No database connection. Cannot fetch data.")
            return []
        cur = conn.cursor()
        try:
            query = "SELECT user_role FROM user_role"
            cur.execute(query)
            res = cur.fetchall()
            return [row[0] for row in res]
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return []
        finally:
            cur.close()
            self._release_connection(conn)

    def get_alls_users(self):
        conn = self._get_connection()
        if conn is None:
            logger.error("No database connection. Cannot fetch data.")
            return []
        cur = conn.cursor()
        try:
            query = """
            SELECT name_user, last_name_user, email_user, user_role, email_user, user_id
            FROM user_inwi
            """
            cur.execute(query)
            res = cur.fetchall()
            return [
                {
                    "name": row[0] if row[0] else "",
                    "last_name": row[1] if row[1] else "",
                    "email": decrypt(row[2]) if row[2] else "",
                    "user_role": row[3] if row[3] else "",
                    "email_user": row[4] if row[4] else "",
                    "user_id": row[5] if row[5] else ""
                }
                for row in res
            ]
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return []
        finally:
            cur.close()
            self._release_connection(conn)

    def get_all_mails(self):
        conn = self._get_connection()
        if conn is None:
            logger.error("No database connection. Cannot fetch data.")
            return []
        cur = conn.cursor()
        try:
            query = """
            SELECT email_rec, date_rec, subject, body, body_env, date_env, status, id, conversation_id
            FROM email_lo ORDER BY date_rec DESC
            """
            cur.execute(query)
            res = cur.fetchall()
            return [
                {
                    "email_rec": decrypt(row[0]) if row[0] else "",
                    "date_rec": row[1],
                    "subject": row[2] if row[2] else "",
                    "body": decrypt(row[3]) if row[3] else "",
                    "body_env": decrypt(row[4]) if row[4] else "",
                    "date_env": row[5] if row[5] else "",
                    "status": row[6] if row[6] else "",
                    "id_mail": row[7],
                    "conversation_id": row[8] if row[8] else ""
                }
                for row in res
            ]
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return []
        finally:
            cur.close()
            self._release_connection(conn)

    def get_all_mails_attente(self):
        conn = self._get_connection()
        if conn is None:
            logger.error("No database connection. Cannot fetch data.")
            return []
        cur = conn.cursor()
        try:
            query = """
            SELECT email_rec, date_rec, subject, body, body_env, date_env, status, id
            FROM email_lo WHERE status = 'En attente' ORDER BY date_rec DESC
            """
            cur.execute(query)
            res = cur.fetchall()
            return [
                {
                    "email_rec": decrypt(row[0]) if row[0] else "",
                    "date_rec": row[1],
                    "subject": row[2] if row[2] else "",
                    "body": decrypt(row[3]) if row[3] else "",
                    "body_env": decrypt(row[4]) if row[4] else "",
                    "date_env": row[5] if row[5] else "",
                    "status": row[6] if row[6] else "",
                    "id_mail": row[7],
                    "diff_time": get_diff(row[1])
                }
                for row in res
            ]
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return []
        finally:
            cur.close()
            self._release_connection(conn)

    def get_all_mails_echous(self):
        conn = self._get_connection()
        if conn is None:
            logger.error("No database connection. Cannot fetch data.")
            return []
        cur = conn.cursor()
        try:
            query = """
            SELECT email_rec, date_rec, subject, body, body_env, date_env, status, id
            FROM email_lo WHERE status = 'Failed' ORDER BY date_rec DESC
            """
            cur.execute(query)
            res = cur.fetchall()
            return [
                {
                    "email_rec": decrypt(row[0]) if row[0] else "",
                    "date_rec": row[1],
                    "subject": row[2] if row[2] else "",
                    "body": decrypt(row[3]) if row[3] else "",
                    "body_env": decrypt(row[4]) if row[4] else "",
                    "date_env": row[5] if row[5] else "",
                    "status": row[6] if row[6] else "",
                    "id_mail": row[7]
                }
                for row in res
            ]
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return []
        finally:
            cur.close()
            self._release_connection(conn)

    def get_mail_by_id(self, id_mail):
        conn = self._get_connection()
        if conn is None:
            logger.error("No database connection. Cannot fetch data.")
            return None
        cur = conn.cursor()
        try:
            query = """
            SELECT email_rec, date_rec, subject, body, body_env, date_env, status, id, cate_msg, conversation_id
            FROM email_lo WHERE id = %s
            """
            cur.execute(query, (id_mail,))
            res = cur.fetchone()
            if res:
                return {
                    "email_rec": decrypt(res[0]) if res[0] else "",
                    "date_rec": res[1] if res[1] else "",
                    "subject": res[2] if res[2] else "",
                    "body": decrypt(res[3]) if res[3] else "",
                    "body_env": decrypt(res[4]) if res[4] else "",
                    "date_env": res[5] if res[5] else "",
                    "status": res[6] if res[6] else "",
                    "id_mail": res[7] if res[7] else "",
                    "cate_msg": res[8] if res[8] else "",
                    "conversation_id": res[9] if res[9] else ""
                }
            return None
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return None
        finally:
            cur.close()
            self._release_connection(conn)

    def get_all_conversation(self):
        conn = self._get_connection()
        if conn is None:
            logger.error("No database connection. Cannot fetch data.")
            return []
        cur = conn.cursor()
        try:
            query = """
            SELECT e.email_rec, e.date_rec, e.subject, e.body, e.body_env, e.date_env, e.status, e.id, e.cate_msg, e.conversation_id
            FROM email_lo e
            INNER JOIN (
                SELECT conversation_id, MIN(date_rec) AS latest_date
                FROM email_lo
                GROUP BY conversation_id
            ) latest ON e.conversation_id = latest.conversation_id AND e.date_rec = latest.latest_date
            """
            cur.execute(query)
            res = cur.fetchall()
            return [
                {
                    "email_rec": decrypt(row[0]) if row[0] else "",
                    "date_rec": row[1],
                    "subject": row[2] if row[2] else "",
                    "body": decrypt(row[3]) if row[3] else "",
                    "body_env": decrypt(row[4]) if row[4] else "",
                    "date_env": row[5],
                    "status": row[6],
                    "id": row[7],
                    "cate_msg": row[8] if row[8] else "",
                    "conversation_id": row[9]
                }
                for row in res
            ]
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return []
        finally:
            cur.close()
            self._release_connection(conn)

    def get_all_mail_by_conversation(self, conversation_id):
        conn = self._get_connection()
        if conn is None:
            logger.error("No database connection. Cannot fetch data.")
            return [], ""
        cur = conn.cursor()
        try:
            query = """
            SELECT email_rec, date_rec, subject, body, body_env, date_env, status, id, cate_msg, conversation_id
            FROM email_lo WHERE conversation_id = %s ORDER BY date_rec
            """
            cur.execute(query, (conversation_id,))
            res = cur.fetchall()
            if res:
                first = res[0]
                subject = first[2] if first[2] else ""
                result = [
                    {
                        "email_rec": decrypt(row[0]) if row[0] else "",
                        "date_rec": row[1],
                        "subject": row[2] if row[2] else "",
                        "body": decrypt(row[3]) if row[3] else "",
                        "body_env": decrypt(row[4]) if row[4] else "",
                        "date_env": row[5] if row[5] else "",
                        "status": row[6],
                        "id": row[7],
                        "cate_msg": row[8] if row[8] else "",
                        "conversation_id": row[9]
                    }
                    for row in res
                ]
                return result, subject
            return [], ""
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return [], ""
        finally:
            cur.close()
            self._release_connection(conn)

    def delete_user(self, id_user):
        conn = self._get_connection()
        if conn is None:
            logger.error("No database connection. Cannot fetch data.")
            return False
        cur = conn.cursor()
        try:
            query = "DELETE FROM user_inwi WHERE user_id = %s"
            cur.execute(query, (id_user,))
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return False
        finally:
            cur.close()
            self._release_connection(conn)

    def create_History(self, user_id, ip_addr, success, user_agent, date_l):
        conn = self._get_connection()
        if conn is None:
            logger.error("No database connection. Cannot fetch data.")
            return False
        cur = conn.cursor()
        try:
            query = """
            INSERT INTO login_history (user_id, ip_adress, success, user_agent, date_l)
            VALUES (%s, %s, %s, %s, %s)
            """
            cur.execute(query, (user_id, ip_addr, success, user_agent, date_l))
            conn.commit()
            logger.info("Login history inserted.")
            return cur.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return False
        finally:
            cur.close()
            self._release_connection(conn)

    def insert_chat(self, msg, date, user_id, id_conv):
        conn = self._get_connection()
        if conn is None:
            logger.error("No database connection. Cannot fetch data.")
            return None
        cur = conn.cursor()
        try:
            query = """
            INSERT INTO cht_bt (msg_user, dt_msg, conv_id, user_id)
            VALUES (%s, %s, %s, %s) RETURNING mes_id
            """
            cur.execute(query, (encrypt(msg), date, id_conv, user_id))
            row = cur.fetchone()
            conn.commit()
            logger.info(f"Chat message inserted with ID: {row[0]}")
            return str(row[0])
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return None
        finally:
            cur.close()
            self._release_connection(conn)

    def historique(self, user_id):
        conn = self._get_connection()
        if conn is None:
            logger.error("No database connection. Cannot fetch data.")
            return []
        cur = conn.cursor()
        try:
            query = """
            SELECT conv_id, msg_user, dt_msg
            FROM cht_bt
            WHERE (conv_id, dt_msg) IN (
                SELECT conv_id, MIN(dt_msg)
                FROM cht_bt
                GROUP BY conv_id
            ) AND user_id = %s
            ORDER BY dt_msg
            """
            cur.execute(query, (user_id,))
            res = cur.fetchall()
            return [
                {
                    "conv_id": row[0] if row[0] else "",
                    "subject": decrypt(row[1]) if row[1] else "",
                    "date_u": row[2] if row[2] else ""
                }
                for row in res
            ]
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return []
        finally:
            cur.close()
            self._release_connection(conn)

    def insert_res_msg(self, msg_r, dt_r, id_msg, sql_r, ct_msg):
        conn = self._get_connection()
        if conn is None:
            logger.error("No database connection. Cannot fetch data.")
            return False
        cur = conn.cursor()
        try:
            query = """
            UPDATE cht_bt SET res_user = %s, dt_res_user = %s, req_sql = %s , ct_msg = %s WHERE mes_id = %s 
            """
            cur.execute(query, (encrypt(msg_r), dt_r, encrypt(sql_r) if sql_r else None, ct_msg, id_msg))
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return False
        finally:
            cur.close()
            self._release_connection(conn)

    def gey_name_user(self, user_id):
        conn = self._get_connection()
        if conn is None:
            logger.error("No database connection. Cannot fetch data.")
            return None, None
        cur = conn.cursor()
        try:
            query = "SELECT name_user, last_name_user, email_user FROM user_inwi WHERE email_user = %s LIMIT 1"
            cur.execute(query, (user_id,))
            res = cur.fetchone()
            if res and res[0] and res[1]:
                full_name = f"{res[0]} {res[1]}"
                return full_name, decrypt(res[2]) if res[2] else ""
            return "None", "None"
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return None, None
        finally:
            cur.close()
            self._release_connection(conn)

    def get_all_msg_con(self, conv_id, user_id):
        conn = self._get_connection()
        if conn is None:
            logger.error("No database connection. Cannot fetch data.")
            return []
        cur = conn.cursor()
        try:
            query = "SELECT * FROM cht_bt WHERE conv_id = %s AND user_id = %s ORDER BY dt_msg"
            cur.execute(query, (conv_id, user_id))
            res = cur.fetchall()
            return [
                {
                    "msg_id": row[0] if row[0] else "",
                    "msg_user": decrypt(row[1]) if row[1] else "",
                    "req_sql": decrypt(row[2]) if row[2] else "",
                    "res_user": decrypt(row[3]) if row[3] else "",
                    "ct_ms": row[4] if row[4] else "",
                    "user_id": row[5] if row[5] else "",
                    "date_rec": row[6].strftime("%H:%M") if row[6] else "",
                    "date_env": row[7].strftime("%H:%M") if row[7] else "",
                    "conv_id": row[8] if row[8] else ""
                }
                for row in res
            ]
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return []
        finally:
            cur.close()
            self._release_connection(conn)

def get_diff(date_tm):
    current_date = datetime.now()
    date_diff = current_date - date_tm
    hours = date_diff.days * 24 + date_diff.seconds // 3600
    minutes = (date_diff.seconds % 3600) // 60
    return f"{hours}h:{minutes}m"