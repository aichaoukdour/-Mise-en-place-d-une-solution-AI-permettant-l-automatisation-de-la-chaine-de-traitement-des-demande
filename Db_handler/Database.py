
import psycopg2
from django.conf import settings
from django.utils import timezone
from datetime import datetime


from Db_handler.data_encrypt import encrypt,decrypt,hash_email
from Db_handler.models import User


class EmailDatabase:
    def __init__(self):
        self.conn = self._connect()

    def _connect(self):
        try:
            conn = psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
            )
            print("Database connection successful.")
            return conn
        except Exception as e:
            print(f"Failed to connect to the database: {e}")
            return None

    def email_check(self,email,password):
        if self.conn == None :
            print("No database connection. Cannot fetch data.")
            return []
        try:
            cur = self.conn.cursor()
            query = "SELECT user_id,email_user,user_role,name_user,last_name_user FROM user_inwi  WHERE user_id = %s   and password = %s LIMIT 1"
            cur.execute(query, (hash_email(email),hash_email(password)))
            result = cur.fetchone()
            if result:  
                exist = True
                user_id, email_user, user_role, name_user, last_name_user = result  
                user = User(user_id, name_user, last_name_user, email_user, user_role)
                return exist, user
            else:
                exist = False
                return exist, None  


        except Exception as e:
            print(f"Failed to fetch data: {e}")
            return False, None


    def user_by_id(self,user_id):
        if self.conn == None :
            print("No database connection. Cannot fetch data.")
            return []
        try:
            cur = self.conn.cursor()
            query = "SELECT user_id,email_user,user_role,name_user,last_name_user FROM user_inwi  WHERE user_id = %s   LIMIT 1"
            cur.execute(query,(user_id,))
            result = cur.fetchone()
            if result:  
                
                user_id, email_user, user_role, name_user, last_name_user = result  
                user = {
                    "user_id":user_id,
                    "email_user" : decrypt(email_user),
                    "user_role":user_role,
                    "name_user":name_user,
                    "last_name_user":last_name_user
                    
                }
                return user
            else:
                
                return None  


        except Exception as e:
            print(f"Failed to fetch data: {e}")
            return  None
        
    def Update_User(self, name_user,last_name_user,email_user,user_role,user_id):
        
        if self.conn == None :
            print("No database connection. Cannot fetch data.")
            return []
        try:
            cur = self.conn.cursor()
            query = """
         UPDATE user_inwi
        SET name_user = %s,
            last_name_user = %s,
            user_role = %s,
            user_id = %s
        WHERE user_id = %s
            """
           
            
            cur.execute(query,(name_user,last_name_user,user_role,hash_email(email_user),user_id))
            
            self.conn.commit()
            if cur.rowcount >0:  
               
            
                return True
            else:
                
                return False  


        except Exception as e:
            print(f"Failed to fetch data: {e}")
            return  None
        
        
    def get_all_mail_user(self,email_rec):
            if self.conn == None :
               print("No database connection. Cannot fetch data.")
               return []
            if email_rec is None:
                  print("Invalid email_rec: None")
                  return []
            try :
                cur = self.conn.cursor()
                query ="""
                SELECT email_rec , date_rec ,subject,body,body_env,date_env,status,id ,conversation_id from email_lo WHERE email_rec = %s ORDER BY date_rec DESC
                """
                cur.execute(query,(email_rec,))
                res = cur.fetchall()
                if cur.rowcount :
                    
                    email_rec_list = [decrypt(row[0]) for row in res]
                    date_rec_list = [row[1] for row in res]
                    subject_list = [row[2] if row[2] else "" for row in res]
                    body_list = [decrypt(row[3]) if row[3] else "" for row in res]
                    body_env_list = [decrypt(row[4]) if row[4] else "" for row in res]
                    date_env_list = [row[5] if row[5] else "" for row in res]
                    status_list = [row[6] if row[6] else "" for row in res]
                    id_mail = [row[7] if row[7] else "" for row in res]
                    conversation_id = [row[8] if row[8] else "" for row in res]
                    return [
                    {
                        "email_rec": email_rec_list[i],
                        "date_rec": date_rec_list[i],
                        "subject": subject_list[i],
                        "body": body_list[i],
                        "body_env": body_env_list[i],
                        "date_env": date_env_list[i],
                        "status": status_list[i],
                        "id_mail" : id_mail[i],
                        "conversation_id" : conversation_id[i]
                    }
                    for i in range(len(res))
                ]
               
    
            except Exception as e:
              print(f"Failed to fetch data: {e}")
              return None


    def create_user(self,name_user,last_name_user,email_user,user_role) :
         if self.conn == None :
               print("No database connection. Cannot fetch data.")
               return []
           
         try :
            cur = self.conn.cursor()
            query ="""
            Insert into user_inwi Values(%s,%s,%s,%s,%s)
            
            """
            cur.execute(query,(name_user,last_name_user,encrypt(email_user),user_role,hash_email(email_user)))
            self.conn.commit()
            if cur.rowcount()>0 :
                return True
            else :
                return False
         except Exception as e:
              print(f"Failed to fetch data: {e}")
              return None    
    def all_roles(self) :
         if self.conn == None :
               print("No database connection. Cannot fetch data.")
               return []
           
         try :
             cur = self.conn.cursor()
             query = """
             SELECT user_role From user_role
             """  
             cur.execute(query)
             res = cur.fetchall()
             user_role =[row[0] for row in res]
             return user_role
         except Exception as e:
              print(f"Failed to fetch data: {e}")
              return None    
                
    def get_alls_users(self) :
        if self.conn == None :
               print("No database connection. Cannot fetch data.")
               return []
           
        try :   
            cur = self.conn.cursor()
            query ="""
            SELECT name_user,last_name_user,email_user,user_role,email_user,user_id FROM user_inwi
            """   
            cur.execute(query)
            res = cur.fetchall()
            name = [row[0] if row[0] else "" for row in res]
            last_name = [row[1] if row[1] else "" for row in res]
            email =[decrypt(row[2]) if row[2] else "" for row in res]
            user_role =[row[3] if row[3] else "" for row in res]
            email_user =[row[4] if row[4] else "" for row in res]
            user_id =[row[5] if row[5] else "" for row in res]
            return [
                {
                    "name": name[i],
                    "last_name": last_name[i],
                    "email": email[i],
                    "user_role": user_role[i],
                    "email_user" :email_user[i],
                    "user_id" :user_id[i]
                  
                }
                for i in range(len(res))
            ]
            
        except Exception as e:
              print(f"Failed to fetch data: {e}")
              return None
            
    def get_all_mails(self) :
        if self.conn == None :
               print("No database connection. Cannot fetch data.")
               return []
      
        try :
                cur = self.conn.cursor()
                query ="""
                SELECT email_rec , date_rec ,subject,body,body_env,date_env,status,id,conversation_id from email_lo ORDER BY date_rec DESC
                """
                cur.execute(query)
                res = cur.fetchall()
                email_rec_list = [decrypt(row[0]) for row in res]
                date_rec_list = [row[1] for row in res]
                subject_list = [row[2] if row[2] else "" for row in res]
                body_list = [decrypt(row[3]) if row[3] else "" for row in res]
                body_env_list = [decrypt(row[4]) if row[4] else "" for row in res]
                date_env_list = [row[5] if row[5] else "" for row in res]
                status_list = [row[6] if row[6] else "" for row in res]
                id_mail = [row[7] for row in res]
                conversation_id = [row[8] for row in res]
                return [
                {
                    "email_rec": email_rec_list[i],
                    "date_rec": date_rec_list[i],
                    "subject": subject_list[i],
                    "body": body_list[i],
                    "body_env": body_env_list[i],
                    "date_env": date_env_list[i],
                    "status": status_list[i],
                    "id_mail":id_mail[i],
                    "conversation_id":conversation_id[i]
                }
                for i in range(len(res))
            ]
               
    
        except Exception as e:
              print(f"Failed to fetch data: {e}")
              return None
        
                   
    def get_all_mails_attente(self) :        
     if self.conn == None :
               print("No database connection. Cannot fetch data.")
               return []
      
     try :
                cur = self.conn.cursor()
                query ="""
                SELECT email_rec , date_rec ,subject,body,body_env,date_env,status,id from email_lo where status = 'En attente' ORDER BY date_rec DESC
                """
                cur.execute(query)
                res = cur.fetchall()
                email_rec_list = [decrypt(row[0]) for row in res]
                date_rec_list = [row[1] for row in res]
                subject_list = [row[2] if row[2] else "" for row in res]
                body_list = [decrypt(row[3]) if row[3] else "" for row in res]
                body_env_list = [decrypt(row[4]) if row[4] else "" for row in res]
                date_env_list = [row[5] if row[5] else "" for row in res]
                status_list = [row[6] if row[6] else "" for row in res]
                id_mail = [row[7] for row in res]
                
                return [
                {
                    "email_rec": email_rec_list[i],
                    "date_rec": date_rec_list[i],
                    "subject": subject_list[i],
                    "body": body_list[i],
                    "body_env": body_env_list[i],
                    "date_env": date_env_list[i],
                    "status": status_list[i],
                    "id_mail":id_mail[i],
                    "diff_time": get_diff(date_rec_list[i])
                }
                for i in range(len(res))
            ]
               
    
     except Exception as e:
              print(f"Failed to fetch data: {e}")
              return None
    def get_all_mails_echous(self):
     if self.conn == None :
               print("No database connection. Cannot fetch data.")
               return []
      
     try :
                cur = self.conn.cursor()
                query ="""
                SELECT email_rec , date_rec ,subject,body,body_env,date_env,status,id from email_lo  WHERE status = 'Failed' ORDER BY date_rec DESC
                """
                cur.execute(query)
                res = cur.fetchall()
                email_rec_list = [decrypt(row[0]) for row in res]
                date_rec_list = [row[1] for row in res]
                subject_list = [row[2] if row[2] else "" for row in res]
                body_list = [decrypt(row[3]) if row[3] else "" for row in res]
                body_env_list = [decrypt(row[4]) if row[4] else "" for row in res]
                date_env_list = [row[5] if row[5] else "" for row in res]
                status_list = [row[6] if row[6] else "" for row in res]
                id_mail = [row[7] for row in res]
                
                
                return [
                {
                    "email_rec": email_rec_list[i],
                    "date_rec": date_rec_list[i],
                    "subject": subject_list[i],
                    "body": body_list[i],
                    "body_env": body_env_list[i],
                    "date_env": date_env_list[i],
                    "status": status_list[i],
                    "id_mail":id_mail[i]
                   
                }
                for i in range(len(res))
            ]

     except Exception as e:
              print(f"Failed to fetch data: {e}")
              return None
    def get_mail_by_id(self,id_mail) :   
        if self.conn == None :
               print("No database connection. Cannot fetch data.")
               return []
        try :
            cur = self.conn.cursor()
            query ="""
                SELECT email_rec , date_rec ,subject,body,body_env,date_env,status,id,cate_msg,conversation_id from email_lo  WHERE id = %s 
                """
            cur.execute(query,(id_mail,))
            
            res = cur.fetchone()
            email_rec_list = decrypt(res[0]) if res[0] else ""
            
            date_rec_list = res[1] if res[1] else ""
            subject_list = res[2] if res[2] else ""
            body_list = decrypt(res[3]) if res[3] else ""
            
            body_env_list = decrypt(res[4]) if res[4] else ""
            date_env_list = res[5] if res[5] else ""
            status_list = res[6] if res[6] else ""
            id_mail = res[7] if res[7] else ""
            cate_msg = res[8] if res[8] else ""
            conversation_id = res[9] if res[9] else ""
            
            return {
                "email_rec": email_rec_list,
                "date_rec": date_rec_list,
                "subject": subject_list,
                "body": body_list,
                "body_env": body_env_list,
                "date_env": date_env_list,
                "status": status_list,
                "id_mail": id_mail,
                "cate_msg": cate_msg,
                "conversation_id": conversation_id
            }
            
        
            
        except Exception as e:
              print(f"Failed to fetch data: {e}")
              return None 
        finally:
          cur.close() 
          
    def get_all_conversation(self):
        if self.conn == None :
               print("No database connection. Cannot fetch data.")
               return []
        try :
            cur = self.conn.cursor()
            query = """
            SELECT e.email_rec,
    e.date_rec,
    e.subject,
    e.body,
    e.body_env,
    e.date_env,
    e.status,
    e.id,
    e.cate_msg,
    e.conversation_id
FROM email_lo e
INNER JOIN (
    SELECT conversation_id, MIN(date_rec) AS latest_date
    FROM email_lo
    GROUP BY conversation_id
) latest ON e.conversation_id = latest.conversation_id AND e.date_rec = latest.latest_date 

            """
            
            cur.execute(query)
            res = cur.fetchall()
            result = []
            for res in res:
                result.append({
                    "email_rec": decrypt(res[0]) if res[0] else "",
                    "date_rec": res[1],
                    "subject": res[2] if res[2] else "",
                    "body": decrypt(res[3]) if res[3] else "",
                    "body_env": decrypt(res[4]) if res[4] else "",
                    "date_env": res[5],
                    "status": res[6],
                    "id": res[7],
                    "cate_msg": res[8] if res[8] else "",
                    "conversation_id": res[9]
                })
            return result

        except Exception as e:
              print(f"Failed to fetch data: {e}")
              return None     
            
    def get_all_mail_by_conversation(self,conversation_id):   
        if self.conn == None :
               print("No database connection. Cannot fetch data.")
               return []
        try :
            cur = self.conn.cursor()
            query ="""
                SELECT email_rec , date_rec ,subject,body,body_env,date_env,status,id,cate_msg,conversation_id from email_lo  WHERE conversation_id = %s  ORDER BY date_rec 
                """
            cur.execute(query,(conversation_id,))
            res = cur.fetchall()
            first = res[0] 
            subject = first[2] if first[2] else "",
            
            result = []
            for res in res:
                result.append({
                    "email_rec": decrypt(res[0]) if res[0] else "",
                    "date_rec": res[1],
                    "subject": res[2] if res[2] else "",
                    "body": decrypt(res[3]) if res[3] else "",
                    "body_env": decrypt(res[4]) if res[4] else "",
                    "date_env": res[5] if res[5] else "",
                    "status": res[6],
                    "id": res[7],
                    "cate_msg": res[8] if res[8] else "",
                    "conversation_id": res[9]
                })
            return result,subject
        
            
        except Exception as e:
              print(f"Failed to fetch data: {e}")
              return None 
        finally:
          cur.close()              
               
    def delete_user(self,id_user):
        if self.conn == None :
               print("No database connection. Cannot fetch data.")
               return []
        try :
            cur = self.conn.cursor()
            query = """
            DELETE FROM user_inwi WHERE user_id = %s
            """   
            cur.execute(query,(id_user,))
            self.conn.commit()
            if cur.rowcount > 0:  
                 return True
            else:
                 return False
        except Exception as e:
              print(f"Failed to fetch data: {e}")
              return None     
           
    def create_History(self,user_id,ip_adrr,success,user_agt,date_l) :
        if self.conn == None :
               print("No database connection. Cannot fetch data.")
               return []
        try :
            cur = self.conn.cursor()
            query = """
            INSERT INTO public.login_history(
	user_id, "Ip_adress", success, user_agent, date_l)
	VALUES (%s, %s, %s, %s, %s);
            """
            cur.execute(query,(user_id,ip_adrr,success,user_agt,date_l))
            if cur.rowcount > 0:
                print("Loggin Inserted")
                self.conn.commit()
        
        except Exception as e:
              print(f"Failed to fetch data: {e}")
              return None      
        

    def insert_chat(self,msg,date,user_id,id_conv):
        if self.conn == None :
            print("No database connection. Cannot fetch data.")
            return [] 
        try :
            cursor = self.conn.cursor()
            query = """
            INSERT INTO Cht_bt(msg_user,dt_msg,conv_id,user_id) VALUES(%s, %s, %s,%s) RETURNING *;
            """
            cursor.execute(query, (encrypt(msg),date,id_conv,user_id ))
            row = cursor.fetchone()
            print("La ligne insérée est : ",row[0])
            self.conn.commit()
            cursor.close()
            return str(row[0])
        except Exception as e:
            print(f"Failed to connect to the database: {e}")
            return []
    def historique(self):
        if self.conn == None :
            print("No database connection. Cannot fetch data.")
            return [] 
        try :
            cursor = self.conn.cursor()
            query = """
SELECT conv_id, msg_user, dt_msg 
FROM cht_bt
WHERE (conv_id, dt_msg) IN (
    SELECT conv_id, MIN(dt_msg)
    FROM cht_bt
    GROUP BY conv_id
)
ORDER BY dt_msg;     
     """
            cursor.execute(query)
            result = cursor.fetchall()
            
            if result :
                s =[]
                for row in result :
                    s.append({
                        "conv_id":row[0] if row[0] else " ",
                        "subject":decrypt(row[1]) if row[1] else "",
                        "date_u":row[2] if row[2] else " "
                  })
                print(s)
                    
                
                
                return s
                
            return None

            
        except Exception as e:
            print(f"Failed to connect to the database: {e}")
            return []
    def insert_res_msg(self,msg_r,dt_r,id_msg,sql_r):
        if self.conn == None :
            print("No database connection. Cannot fetch data.")
            return [] 
        try :
            cursor = self.conn.cursor()
            query = """
            UPDATE cht_bt SET res_user = %s, dt_res_user = %s, req_sql = %s WHERE mes_id = %s
            """
            cursor.execute(query, (encrypt(msg_r),dt_r,encrypt(sql_r) if sql_r else None,id_msg))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Failed to connect to the database: {e}")
            return False
    def get_all_msg_con(self,conv_id):
        if self.conn == None :
            print("No database connection. Cannot fetch data.")
            return [] 
        try :
            cursor = self.conn.cursor()
            query = """
             SELECT * FROM cht_bt WHERE conv_id = %s ORDER BY dt_msg
            """
            cursor.execute(query, (conv_id,))
            result = cursor.fetchall()
            res = [] 
            for row in result :
                res.append({
                    "msg_id":row[0] if row[0] else " ",
                    "msg_user":decrypt(row[1]) if row[1] else "",
                    "req_sql":decrypt(row[2]) if row[2] else " ",
                    "res_user":decrypt(row[3]) if row[3] else " ",
                    "ct_ms":row[4] if row[4] else "",
                    "user_id":row[5] if row[5] else " ",
                    "date_rec":row[6].strftime("%H:%M") if row[6] else " ",
                    "date_env":row[7].strftime("%H:%M") if row[7] else "",
                    "conv_id":row[8] if row[8] else " ",
                })
            cursor.close()
            return res
        except Exception as e:
            print(f"Failed to connect to the database: {e}")
            return []

def get_diff(date_tm):
    current_date  =  datetime.now()
    date_diff =  current_date -date_tm
    hours = date_diff.days * 24 + date_diff.seconds // 3600
    minutes = (date_diff.seconds % 3600) // 60   
    return f"{hours}h:{minutes}m"       
