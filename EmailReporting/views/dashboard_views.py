from email.message import EmailMessage
from django.shortcuts import render
from django.core.paginator import Paginator
from EmailReporting.Db_handler.db import DatabaseManager

EmailDatabase_instance = DatabaseManager()


def admin(request):
    user_role = EmailDatabase_instance.all_roles()
    
    # Get all data
    all_mails_list = EmailDatabase_instance.get_all_mails()
    all_users_list = EmailDatabase_instance.get_alls_users()
    all_mail_pending_list = EmailDatabase_instance.get_all_mails_attente()
    
    # Calculate counts for the dashboard stats
    l_all_mails = len(all_mails_list)
    l_all_users = len(all_users_list)
    l_all_mails_pending = len(all_mail_pending_list)
    
    # Set up pagination for emails - 5 items per page
    emails_paginator = Paginator(all_mails_list, 5)
    emails_page_number = request.GET.get('emails_page', 1)
    paginated_emails = emails_paginator.get_page(emails_page_number)
    
    # Set up pagination for users - 5 items per page
    users_paginator = Paginator(all_users_list, 5)
    users_page_number = request.GET.get('users_page', 1)
    paginated_users = users_paginator.get_page(users_page_number)
    
    # Set up pagination for pending emails - 5 items per page
    pending_paginator = Paginator(all_mail_pending_list, 5)
    pending_page_number = request.GET.get('pending_page', 1)
    paginated_pending = pending_paginator.get_page(pending_page_number)
    
    return render(request, "Admin/admin.html", {
        "all_mails": paginated_emails,
        "all_users": paginated_users,
        "all_mails_p": paginated_pending,
        "l_all_mails": l_all_mails,
        "l_all_users": l_all_users,
        "l_all_p": l_all_mails_pending,
        "user_role": user_role,
        # Add pagination context for template
        "emails_paginator": emails_paginator,
        "users_paginator": users_paginator,
        "pending_paginator": pending_paginator
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
    paginator = Paginator(emails_list, 3)  # Show 3 emails per page
    page_number = request.GET.get('page')
    emails = paginator.get_page(page_number)
    
    return render(request, "Admin/all_requestes.html", {
        "emails": emails,
        "paginator": paginator
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
    paginator = Paginator(emails_list, 3)  # Show 3 emails per page
    page_number = request.GET.get('page')
    mails_pending = paginator.get_page(page_number)
    
    return render(request, "Admin/PendingRequests.html", {
        "emails": mails_pending,
        "paginator": paginator
    })


def OverdueRequests(request):
    return render(request, "Admin/OverdueRequests.html")