# Mail Views

from datetime import timezone
from email.message import EmailMessage
import os
from django.http import FileResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import render
import pandas as pd
#from Db_handler.Database import EmailDatabase
from django.core.paginator import Paginator
from datetime import timedelta
from django.utils import timezone

    #EmailDatabase_instance = EmailDatabase()
from EmailReporting.Db_handler.db import DatabaseManager

EmailDatabase_instance = DatabaseManager()
def download_excel_view(request, id_msg):
    path_of_excel = "C:/Users/benme/OneDrive/Bureau/Bennani_test/excel_responses/response_"
    file_path = f"{path_of_excel}{id_msg[-30:]}.xlsx"
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=f"response_{id_msg[-30:]}.xlsx")
    return HttpResponseNotFound("Fichier non trouvé.")
def read_excel(id_msg):
    print("id_msg", id_msg)
    path_of_excel = "C:/Users/benme/OneDrive/Bureau/Bennani_test/excel_responses/response_"
    file_path = f"{path_of_excel}{id_msg}.xlsx"
    
    if os.path.exists(file_path):
        df = pd.read_excel(file_path, engine='openpyxl', index_col=None, skiprows=7)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df = df.dropna(axis=1, how='all')
        return df.head(10).to_dict(orient='records')
    else:
        print("File does not exist:", file_path)
        return None

def request_status(request, id):
    print(id)
    mail_detail = EmailDatabase_instance.get_mail_by_id(id)
    
    return render(request, "SuiviDemande/conversation.html", {"request": mail_detail})




def conversation_user(request,id):
    coversation_detail,subject = EmailDatabase_instance.get_all_mail_by_conversation(conversation_id=id)
    for mail in coversation_detail:
        if mail['body_env'].endswith(".xlsx"):
           mail['type_data'] = "list"
           mail['data'] = read_excel(id_msg=mail['id'][-30:])
        else:
           mail['type_data'] = "str"
           mail['data'] = mail['body_env']
    return render(request, "SuiviDemande/conversation.html",{
        "conversation": coversation_detail,
        "subject":subject
    })     
    
def conversation(request,id):
    Email_convers,subject= EmailDatabase_instance.get_all_mail_by_conversation(conversation_id=id)
    for mail in Email_convers:
       print(mail['id'])
       if mail['body_env'].endswith(".xlsx"):
           mail['type_data'] = "list"
           mail['data'] = read_excel(id_msg=mail['id'][-30:])
       else:
           mail['type_data'] = "str"
           mail['data'] = mail['body_env']
   
    
    return render(request, 'Admin/conversation.html',{
        "conversation":Email_convers,
        "subject" :subject
    })
  


def suivi(request):
    return render(request, "SuiviDemande/conversastion.html")


def suiviinfo(request,id):
    mail_detail = EmailDatabase_instance.get_mail_by_id(id_mail=id)
    if mail_detail['body_env'].endswith(".xlsx"):
        mail_detail['type_data'] = "list"
        mail_detail['data'] = read_excel(id_msg=id[-30:])
    else:
        if mail_detail['body_env'] == "":
            mail_detail['type_data'] = "str"     
            mail_detail['data'] = "Aucune réponse à ce message"
        else:
            mail_detail['type_data'] = "str"     
            mail_detail['data'] = mail_detail['body_env']
    return render(request, "Admin/info_suivi.html",{
        "request": mail_detail
    })

    
    
def suiviinfo_user(request,id):
    mail_detail = EmailDatabase_instance.get_mail_by_id(id_mail=id)
    if mail_detail['body_env'].endswith(".xlsx"):
        mail_detail['type_data'] = "list"
        mail_detail['data'] = read_excel(id_msg=id[-30:])
    else:
        mail_detail['type_data'] = "str"
        mail_detail['data'] = mail_detail['body_env']
    return render(request, "SuiviDemande/detail.html",{
        "request": mail_detail
    })    
    
    
import logging

# Configure logging to print to the console
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# StreamHandler to print logs to the console
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def get_all_mails_by_user(request):
    # Get email_user from session
    email_user = request.session.get("email_user")
    
    # Check if user is authenticated
    if email_user:
        try:
            logger.info(f"Fetching mails for user: {email_user}")
            
            # Fetch mails from the database
            data = EmailDatabase_instance.get_all_mail_user(email_rec=email_user)
            
            if not data:
                logger.warning(f"No mails found for user: {email_user}")
            
            # Count different statuses
            all_mails_count = len(data) if data else 0
            all_mails_count_encours = sum(1 for mail in data if mail.get("status") == "En attente") if data else 0
            all_mail_count_env = sum(1 for mail in data if mail.get("status") == "Envoyé") if data else 0
            all_mail_count_fail = sum(1 for mail in data if mail.get("status") == "failed") if data else 0

            # Log the counts
            logger.info(f"All mails count: {all_mails_count}")
            logger.info(f"En attente count: {all_mails_count_encours}")
            logger.info(f"Envoyé count: {all_mail_count_env}")
            logger.info(f"Failed count: {all_mail_count_fail}")
            
            # Return the rendered HTML with mail data
            return render(request, "SuiviDemande/suiviUser.html", {
                "demandes": data,
                "all_mails_count": all_mails_count,
                "all_mails_count_encours": all_mails_count_encours,
                "all_mail_count_env": all_mail_count_env,
                "all_mail_count_fail": all_mail_count_fail,
            })
        except Exception as e:
            # Log the error
            logger.error(f"Error in get_all_mail_user: {str(e)}")
            return JsonResponse({"error": f"Database error: {str(e)}"}, status=500)
    else:
        # Log and return error if user is not found in the session
        logger.warning("No email user found in session")
        return JsonResponse({"error": "Aucun utilisateur trouvé en session"}, status=400)
def get_all_mails_by_user_Admin(request,id):
        
    if id:
       
        try:
            
            data = EmailDatabase_instance.get_all_mail_user(email_rec=id)
        
            all_mails_count = len(data) if data else 0
            all_mails_count_encours = sum(1 for mail in data if mail.get("status") == "En attente") if data else 0
            all_mail_count_env = sum(1 for mail in data if mail.get("status") == "Envoyé") if data else 0
            all_mail_count_fail = sum(1 for mail in data if mail.get("status") == "failed") if data else 0

        
            return render(request, "Admin/Suivi.html", {"demandes": data,
                                                            "all_mails_count": all_mails_count,
                                                            "all_mails_count_encours":all_mails_count_encours ,
                                                            "all_mail_count_env" :all_mail_count_env,
                                                            "all_mail_count_fail":all_mail_count_fail,
                                                            
                                    
                                                            })
            
            
        except Exception as e:
            print(f"Error in get_all_mail_user: {str(e)}")
            return JsonResponse({"error": f"Database error: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Aucun utilisateur trouvé en session"}, status=400)       
