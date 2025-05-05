# Auth Views

from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render

from rest_framework_simplejwt.tokens import RefreshToken

from Db_handler.Database import EmailDatabase
EmailDatabase_instance = EmailDatabase()

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
        
        
   
