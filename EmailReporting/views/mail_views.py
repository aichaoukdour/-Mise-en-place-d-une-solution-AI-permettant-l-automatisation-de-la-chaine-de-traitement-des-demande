# Mail Views

from datetime import timezone
from email.message import EmailMessage
from django.http import JsonResponse
from django.shortcuts import render
from Db_handler.Database import EmailDatabase
from django.core.paginator import Paginator
from datetime import timedelta
from django.utils import timezone

EmailDatabase_instance = EmailDatabase()

def request_status(request, id):
    print(id)
    mail_detail = EmailDatabase_instance.get_mail_by_id(id)
    
    return render(request, "SuiviDemande/status.html", {"request": mail_detail})


def list_requests(request):
    # Get filter parameters from GET request
    status_filter = request.GET.get("status", "all")
    period_filter = request.GET.get("period", "all")
    search_value = request.GET.get("search", "").lower()
    
    # Retrieve all email messages
    now = timezone.now()
    requests_list = EmailMessage.objects.all()
    
    # Apply filters based on status, period, and search value
    if status_filter != "all":
        requests_list = requests_list.filter(status=status_filter)

    if period_filter == "week":
        requests_list = requests_list.filter(date_recp_message__gte=now - timedelta(days=7))
    elif period_filter == "month":
        requests_list = requests_list.filter(date_recp_message__gte=now - timedelta(days=30))
    elif period_filter == "year":
        requests_list = requests_list.filter(date_recp_message__gte=now - timedelta(days=365))

    if search_value:
        requests_list = requests_list.filter(subject__icontains=search_value)

    # Pagination
    paginator = Paginator(requests_list, 10)  # 10 requests per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Render the template with requests data
    return render(request, "Admin/list_requests.html", {"requests": page_obj})

def conversation_user(request,id):
    coversation_detail,subject = EmailDatabase_instance.get_all_mail_by_conversation(conversation_id=id)
    return render(request, "SuiviDemande/status.html",{
        "conversation": coversation_detail,
        "subject":subject
    })     
    
def conversation(request,id):
    Email_convers,subject= EmailDatabase_instance.get_all_mail_by_conversation(conversation_id=id)
    
    return render(request, 'Admin/conversation.html',{
        "conversation":Email_convers,
        "subject" :subject
    })
  


def suivi(request):
    return render(request, "SuiviDemande/suivi.html")


def suiviinfo(request,id):
    mail_detail = EmailDatabase_instance.get_mail_by_id(id_mail=id)
    return render(request, "Admin/info_suivi.html",{
        "request": mail_detail
    })
    
    
def suiviinfo_user(request,id):
    mail_detail = EmailDatabase_instance.get_mail_by_id(id_mail=id)
    return render(request, "SuiviDemande/suiviinfo.html",{
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
            return render(request, "SuiviDemande/suiviv1.html", {
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

