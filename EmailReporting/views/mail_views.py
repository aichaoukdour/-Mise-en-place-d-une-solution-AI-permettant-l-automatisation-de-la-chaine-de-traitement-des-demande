# Mail Views

from email.message import EmailMessage
from django.http import JsonResponse
from django.shortcuts import render
from Db_handler.Database import EmailDatabase

EmailDatabase_instance = EmailDatabase()

def request_status(request, id):
    print(id)
    mail_detail = EmailDatabase_instance.get_mail_by_id(id)
    
    return render(request, "SuiviDemande/status.html", {"request": mail_detail})


def list_requests(request):
    requests_list = EmailMessage.objects.select_related("status").order_by("-date_recp_message")
    paginator = paginator(requests_list, 10)  # Afficher 10 demandes par page
    page_number = request.GET.get("page")
    requests = paginator.get_page(page_number)

    return render(request, "Admin/list_requests.html", {"requests": requests})


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
    
    
def get_all_mails_by_user(request):
    
    email_user = request.session.get("email_user")  
    
    
    if email_user:
       
        try:
            
            data = EmailDatabase_instance.get_all_mail_user(email_rec=email_user)
            all_mails_count = len(data) if data else 0
            all_mails_count_encours = sum(1 for mail in data if mail.get("status") == "En attente") if data else 0
            all_mail_count_env = sum(1 for mail in data if mail.get("status") == "Envoyé") if data else 0
            all_mail_count_fail = sum(1 for mail in data if mail.get("status") == "failed") if  data else 0

            
            return render(request, "SuiviDemande/suiviv1.html", {"demandes": data,
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

