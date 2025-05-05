# Dashboard Views
from email.message import EmailMessage
from django.shortcuts import render
from Db_handler.Database import EmailDatabase
EmailDatabase_instance = EmailDatabase()


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

    

def PendingRequests(request):
    mails_pending= EmailDatabase_instance.get_all_mails_attente()
    
    return render(request, "Admin/PendingRequests.html" , {
        "emails" : mails_pending
    })

def OverdueRequests(request):
    return render(request, "Admin/OverdueRequests.html")

    
