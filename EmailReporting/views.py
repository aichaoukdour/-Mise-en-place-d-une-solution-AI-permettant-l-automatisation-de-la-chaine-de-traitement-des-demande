import base64
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib import messages
from rest_framework_simplejwt.tokens import RefreshToken


from datetime import datetime


from Db_handler.Database import EmailDatabase
from .models import EmailMessage
EmailDatabase_instance = EmailDatabase()
def request_status(request, id):
    print(id)
    mail_detail = EmailDatabase_instance.get_mail_by_id(id)
    
    return render(request, "SuiviDemande/status.html", {"request": mail_detail})

def list_requests(request):
    requests_list = EmailMessage.objects.select_related("status").order_by("-date_recp_message")
    paginator = Paginator(requests_list, 10)  # Afficher 10 demandes par page
    page_number = request.GET.get("page")
    requests = paginator.get_page(page_number)

    return render(request, "Admin/list_requests.html", {"requests": requests})

def chat(request):
    return render(request, "ChatBot/chat.html")

def suivi(request):
    return render(request, "SuiviDemande/suiviv1.html")


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
def conversation_user(request,id):
    coversation_detail,subject = EmailDatabase_instance.get_all_mail_by_conversation(conversation_id=id)
    return render(request, "SuiviDemande/status.html",{
        "conversation": coversation_detail,
        "subject":subject
    })       

def admin(request):
    user_role = EmailDatabase_instance.all_roles()
    all_mails = EmailDatabase_instance.get_all_mails()
    all_users = EmailDatabase_instance.get_alls_users()
    all_mail_pending = EmailDatabase_instance.get_all_mails_attente()
    l_all_mails = len(all_mails)
    l_all_users = len(all_users)
    l_all_mails_pending = len(all_mail_pending)
    return render(request, "Admin/admin.html",{
        "all_mails" :all_mails,
        "all_users" :all_users,
        "all_mails_p" : all_mail_pending,
        "l_all_mails":l_all_mails,
        "l_all_users" :l_all_users,
        "l_all_p":l_all_mails_pending,
        "user_role":user_role
        
        
        })

def admindash(request):

    return render(request, "Admin/admindash.html")

def allrequests(request):
    mails = EmailDatabase_instance.get_all_mails()
    return render(request, "Admin/all_requestes.html",{
        "emails":mails
    })

def listrequests(request):
    return render(request, "Admin/list_requests.html")

def UserList(request):
    user_list = EmailDatabase_instance.get_alls_users()
    user_role = EmailDatabase_instance.all_roles()
   
    return render(request, "Admin/UsersList.html",{
        "user_list" :user_list,
        "user_role":user_role
    })

def PendingRequests(request):
    mails_pending= EmailDatabase_instance.get_all_mails_attente()
    
    return render(request, "Admin/PendingRequests.html" , {
        "emails" : mails_pending
    })

def OverdueRequests(request):
    return render(request, "Admin/OverdueRequests.html")

def create_user(request):
    user_role = EmailDatabase_instance.all_roles()
    return render(request, 'Admin/CreateUser.html',{"user_role":user_role})

def role_management(request):
    # Implement role management logic
    return render(request, 'Admin/RoleManagement.html')

def blacklist(request):
    # Implement blacklist management logic
    return render(request, 'Admin/Blacklist.html')

def conversation(request,id):
    Email_convers,subject= EmailDatabase_instance.get_all_mail_by_conversation(conversation_id=id)
    
    return render(request, 'Admin/conversation.html',{
        "conversation":Email_convers,
        "subject" :subject
    })

   
   
  
   
    
def accueil(request):
    request.session.clear()  # supprime les clés sans recréer une session
    print(request.session.get('user_role'))
    response = render(request, "accueil.html")
    response['Cache-Control'] = 'no-store'
    return response


    user_role = request.session.get('user_role')
    if user_role:
            del request.session['user_role']
    request.session['user_role'] = None        
    print(user_role)        
    return redirect('/')        
    
def check_email_view(request):


    email = request.GET.get('email', '')
    password = request.GET.get('password', '')
    
    exists, user = EmailDatabase_instance.email_check(email,password)
    ip_address = request.META.get('REMOTE_ADDR')  # IP address of the client
    user_agent = request.META.get('HTTP_USER_AGENT') 
    current_time = datetime.now()
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")# User's browser details
   
    if exists :
        refresh = RefreshToken.for_user(user)  # Now user is a valid User object
        access_token = str(refresh.access_token)  # Get the access token as a string
        print(user.user_role)
        request.session['email_user'] = user.email_user
        request.session['user_role'] = user.user_role
        print(user.user_role)
        print(f"User: {user.email_user}, IP: {ip_address}, User Agent: {user_agent}, Time: {current_time_str}")
        EmailDatabase_instance.create_History(user.user_id ,ip_address,True, user_agent,current_time_str)
       
        # Return the response with the tokens
        return JsonResponse({
            "user_role": user.user_role,
            "exists": exists,
            "authenticated": True,
            "email_user": user.email_user,
            "access_token": access_token,
            "refresh_token": str(refresh)  # Return the refresh token as a string
        })
    else :
        
   
        EmailDatabase_instance.create_History(email,  ip_address,False, user_agent,current_time_str)

        return JsonResponse({
        "exists": exists,
        "authenticated": False,
        "message": "Invalid email or password"
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
    
def user_create(request) :
        if request.method == 'POST':
                name = request.POST.get('first_name', '')
                last_name = request.POST.get('last_name', '')
                email = request.POST.get('email', '')
                role = request.POST.get('role_agt', '')
                
                            
                

                try:
                    is_add = EmailDatabase_instance.create_user(name, last_name, email, role)
                    print(is_add)
                    messages.success(request, "Utilisateur créé avec succès !")
                    return redirect('/Admin/UserList')
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=500)
            
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


def delete_user(request):
   if request.method == "POST":
        user_id = request.POST.get('user_id')
        print(user_id)
        deleted = EmailDatabase_instance.delete_user(user_id)
        if deleted :
             return redirect('/Admin/UserList')
        else :
            print("Error de Modification")
            return redirect('/Admin/UserList')   
        
def update_user(request):
    if request.method == "POST" :
         
            name = request.POST.get('first_name_u', '')
            last_name = request.POST.get('last_name_u', '')
            email = request.POST.get('email_u', '')
            role = request.POST.get('role_agt', '')
            user_id = request.POST.get('user_id_u','')
            
       
            
            
            try:
                    is_add = EmailDatabase_instance.Update_User(name, last_name, email, role,user_id)
                    print(is_add)
                    messages.success(request, "Utilisateur Modifier avec succès !")
                    return redirect('/Admin/UserList')
            except Exception as e:
                    return JsonResponse({'error': str(e)}, status=500)
            
def user_f(request,id) :
    if id :
        
        try:
            user = EmailDatabase_instance.user_by_id(id)
         
            return JsonResponse(user)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
            
            
        
    