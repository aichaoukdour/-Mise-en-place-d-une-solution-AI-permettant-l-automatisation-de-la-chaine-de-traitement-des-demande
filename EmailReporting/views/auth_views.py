from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from rest_framework_simplejwt.tokens import RefreshToken
from Db_handler.data_encrypt import hash_email
from EmailReporting.Db_handler.db import DatabaseManager, hash_email
from EmailReporting.Db_handler.model import UserInwi

EmailDatabase_instance = DatabaseManager()

def user_info(request):
    if request.user.is_authenticated:
        name_user = f"{request.user.name_user} {request.user.last_name_user}".strip()
        email_user = request.user.email_user  # Assuming email_user is decrypted in the model
    else:
        name_user = ''
        email_user = ''
    return {
        'name_user': name_user,
        'email_user': email_user,
    }

# auth_views.py
def accueil_inwi(request):
    user_data = user_info(request)
    return render(request, 'accueil.html', {
        'name_user': user_data['name_user'],
        'email_user': user_data['email_user'],
    })
def accueil(request):
    print(request.session.get('user_role'))
    response = render(request, "login.html")
    response['Cache-Control'] = 'no-store'
    return response
def accueil_inwi(request):
    return render(request, 'accueil.html', {})

@require_POST
@csrf_exempt
def check_email_view(request):
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not email or not password:
            return JsonResponse({"authenticated": False, "message": "Email et mot de passe requis."}, status=400)

        exists, user, login_count = EmailDatabase_instance.email_check(email, password)

        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', 'Inconnu')
        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if exists:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            request.session['email_user'] = email
            request.session['user_role'] = user.user_role
            request.session['login_count'] = login_count
            request.session['name_user'] = f"{user.name_user} {user.last_name_user}".strip()  # Add name to session
            request.session['is_first_login'] = user.is_first_login  # Add first login status

            print(f"[✔] Connexion: {email}, IP: {ip_address}, Agent: {user_agent}, Time: {current_time_str}")
            print(f"login_count: {login_count}, user_role: {user.user_role}")

            EmailDatabase_instance.create_History(user.user_id, ip_address, True, user_agent, current_time_str)

            return JsonResponse({
                "authenticated": True,
                "exists": True,
                "email_user": email,
                "user_role": user.user_role,
                "login_count": login_count,
                "access_token": access_token,
                "refresh_token": str(refresh),
                "name_user": f"{user.name_user} {user.last_name_user}".strip()
            })
        else:
            print(f"[✘] Échec de connexion: {email}, IP: {ip_address}, Agent: {user_agent}, Time: {current_time_str}")
            EmailDatabase_instance.create_History(hash_email(email), ip_address, False, user_agent, current_time_str)

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

@require_POST
@csrf_exempt
def change_password_view(request):
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        current_password = data.get('current_password', '').strip()
        new_password = data.get('new_password', '').strip()

        if not email or not current_password or not new_password:
            return JsonResponse({"success": False, "message": "Tous les champs sont requis."}, status=400)

        exists, user, login_count = EmailDatabase_instance.email_check(email, current_password)
        if exists:
            hashed_new_password = hash_email(new_password)
            session = EmailDatabase_instance.Session()
            try:
                db_user = session.query(UserInwi).filter_by(user_id=hash_email(email)).first()
                if db_user:
                    db_user.password = hashed_new_password
                    db_user.is_first_login = False
                    session.commit()
                    request.session['is_first_login'] = False
                    request.session['login_count'] = login_count + 1
                    print(f"Password updated for {email}, login_count: {login_count + 1}")
                    return JsonResponse({"success": True, "message": "Mot de passe mis à jour avec succès."})
                else:
                    return JsonResponse({"success": False, "message": "Utilisateur introuvable."}, status=404)
            except Exception as e:
                session.rollback()
                print(f"Failed to update password: {e}")
                return JsonResponse({"success": False, "message": "Erreur lors de la mise à jour."}, status=500)
            finally:
                session.close()
        else:
            return JsonResponse({"success": False, "message": "Mot de passe actuel incorrect."}, status=401)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Requête JSON invalide."}, status=400)
    except Exception as e:
        print(f"Error in change_password_view: {e}")
        return JsonResponse({"success": False, "message": "Erreur interne du serveur."}, status=500)

def change_password_page(request):
    if not request.session.get('email_user') or not request.session.get('is_first_login'):
        return redirect('home')
    return render(request, 'change_password.html')

def get_user_role(request):
    user_role = request.session.get('user_role', 'user')
    return JsonResponse({'user_role': user_role})

@require_POST
@csrf_exempt
def skip_password_change(request):
    try:
        email = request.session.get('email_user')
        if not email:
            return JsonResponse({"success": False, "message": "Utilisateur non connecté."}, status=401)

        session = EmailDatabase_instance.Session()
        try:
            db_user = session.query(UserInwi).filter_by(user_id=hash_email(email)).first()
            if db_user:
                db_user.is_first_login = False
                session.commit()
                request.session['is_first_login'] = False
                return JsonResponse({"success": True, "message": "Changement de mot de passe ignoré."})
            else:
                return JsonResponse({"success": False, "message": "Utilisateur introuvable."}, status=404)
        except Exception as e:
            session.rollback()
            print(f"Error skipping password change: {e}")
            return JsonResponse({"success": False, "message": "Erreur lors de l'opération."}, status=500)
        finally:
            session.close()
    except Exception as e:
        print(f"Error in skip_password_change: {e}")
        return JsonResponse({"success": False, "message": "Erreur interne du serveur."}, status=500)

def logout_view(request):
    request.session.flush()
    return redirect('home')