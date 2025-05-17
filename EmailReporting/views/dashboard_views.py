# Dashboard Views
from email.message import EmailMessage
from django.shortcuts import render
from django.core.paginator import Paginator
#from Db_handler.Database import EmailDatabase
#EmailDatabase_instance = EmailDatabase()
from EmailReporting.Db_handler.db import DatabaseManager

EmailDatabase_instance = DatabaseManager()


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
    return render(request, "Admin/admin.html")


def allrequests(request):
    # Get all emails
    emails_list = EmailDatabase_instance.get_all_mails()
    
    # Get filter parameters from URL
    status_filter = request.GET.get('status')
    date_filter = request.GET.get('date')
    
    # Apply filters if provided
    if status_filter and status_filter != 'all':
        # Assuming your DatabaseManager has a filter method or you can filter the list
        emails_list = [email for email in emails_list if email.status == status_filter]
    
    if date_filter:
        # Filter by date - assuming date_rec is an attribute and can be compared as a string
        # You may need to adjust this depending on your actual data format
        emails_list = [email for email in emails_list if email.date_rec.strftime('%Y-%m-%d') == date_filter]
    
    # Set up pagination - 5 items per page
    paginator = Paginator(emails_list, 4)  # Show 5 emails per page
    page_number = request.GET.get('page')
    emails = paginator.get_page(page_number)
    
    return render(request, "Admin/all_requestes.html", {
        "emails": emails
    })
    

def listrequests(request):
    return render(request, "Admin/list_requests.html")


def PendingRequests(request):
    # Get all pending emails
    emails_list = EmailDatabase_instance.get_all_mails_attente()
    
    # Get filter parameters from URL
    date_filter = request.GET.get('date')
    
    # Apply date filter if provided
    if date_filter:
        # Filter by date (adjust based on your data structure)
        emails_list = [email for email in emails_list if email.date_rec.strftime('%Y-%m-%d') == date_filter]
    
    # Set up pagination - 5 items per page
    paginator = Paginator(emails_list, 4)  # Show 5 emails per page
    page_number = request.GET.get('page')
    mails_pending = paginator.get_page(page_number)
    
    return render(request, "Admin/PendingRequests.html", {
        "emails": mails_pending
    })


def OverdueRequests(request):
    return render(request, "Admin/OverdueRequests.html")