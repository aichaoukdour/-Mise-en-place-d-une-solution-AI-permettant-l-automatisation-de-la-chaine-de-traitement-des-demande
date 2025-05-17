# Auth Views

from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import redirect
import json

from rest_framework_simplejwt.tokens import RefreshToken

# auth_views.py
from Db_handler import EmailDatabase
from EmailReporting.Db_handler.db import DatabaseManager

EmailDatabase_instance = DatabaseManager()

def user_info(request):
    email_user = request.session.get('email_user')
    name_user = ''
    
    if email_user:
        name_user, email_user_db = EmailDatabase_instance.gey_name_user(email_user)

    return {
        'name_user': name_user,
        'email_user': email_user_db,
    }

def accueil(request):
    # Don't clear session data here
    print(request.session.get('user_role'))  # This will show the current user role from the session
    response = render(request, "login.html")
    response['Cache-Control'] = 'no-store'
    return response

  
def accueil_inwi(request):
    return render(request, 'accueil.html', {})


@require_POST
@csrf_exempt  # Retire ça si tu as déjà le token CSRF dans le frontend
def check_email_view(request):
    try:
        data = json.loads(request.body)

        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not email or not password:
            return JsonResponse({"authenticated": False, "message": "Email et mot de passe requis."}, status=400)

        exists, user = EmailDatabase_instance.email_check(email, password)

        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', 'Inconnu')
        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if exists:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            request.session['email_user'] = user.email_user
            request.session['user_role'] = user.user_role


            print(f"[✔] Connexion: {user.email_user}, IP: {ip_address}, Agent: {user_agent}, Time: {current_time_str}")

            EmailDatabase_instance.create_History(user.user_id, ip_address, True, user_agent, current_time_str)

            return JsonResponse({
                "authenticated": True,
                "exists": True,
                "email_user": user.email_user,
                "user_role": user.user_role,
                "access_token": access_token,
                "refresh_token": str(refresh)
            })
        else:
            print(f"[✘] Échec de connexion: {email}, IP: {ip_address}, Agent: {user_agent}, Time: {current_time_str}")
            EmailDatabase_instance.create_History(email, ip_address, False, user_agent, current_time_str)

            return JsonResponse({
                "authenticated": False,
                "exists": False,
                "message": "Email ou mot de passe invalide"
            }, status=401)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Requête JSON invalide."}, status=400)
    except Exception as e:
        print(f"[Erreur] check_email_view: {str(e)}")
        return JsonResponse({"error": "Erreur interne du serveur."}, status=500)
        
def logout_view(request):
    request.session.flush()
    return redirect('home')
