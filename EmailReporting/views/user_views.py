# User Views

from datetime import datetime
import json
import os
from django.conf import settings
from django.contrib import messages

from django.http import FileResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
import requests
#from Db_handler.Database import EmailDatabase
#EmailDatabase_instance = EmailDatabase()
from EmailReporting.Db_handler.db import DatabaseManager
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from io import BytesIO

EmailDatabase_instance = DatabaseManager()

import os
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from django.conf import settings


def download_excel_view(file_path):
    print("file_path", file_path)
    if os.path.exists(file_path):
        file_handle = open(file_path, 'rb')
        return FileResponse(file_handle, as_attachment=True, filename=file_path)
    else:
        print("Fichier non trouvé.")
        return HttpResponseNotFound("Fichier non trouvé.")

def create_pdf(first_name, last_name, email, role, password):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Titre
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2, height - 50, "Informations Utilisateur")

    # Logo ou initiales
    logo_margin_top = 30  # espace entre le texte et le logo
    logo_width = 200
    logo_height = 60

    # Calcul de la position du logo
    logo_x = (width - logo_width) / 2
    logo_y = height - 50 - logo_margin_top - logo_height

    # Chemin du logo
    logo_path = os.path.join(settings.BASE_DIR, "static/logo/inwi_logo.jpeg")

    # Dessiner le logo s'il existe
    if os.path.exists(logo_path):
        p.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height)
    else:
        print("⚠️ Logo non trouvé :", logo_path)


    # Informations personnelles
    y = logo_y - 40
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Informations Personnelles")
    y -= 10
    p.setStrokeColor(colors.purple)
    p.line(50, y, width - 50, y)
    y -= 30

    data_personal = [["Nom", "Prénom", "Email", "Rôle"],
                     [last_name, first_name, email, role]]
    table = Table(data_personal, colWidths=[100, 100, 200, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    table.wrapOn(p, width, height)
    table.drawOn(p, 50, y - 40)
    y -= 90

    # Authentification
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Informations d'Authentification")
    y -= 10
    p.line(50, y, width - 50, y)
    y -= 30

    data_auth = [["Email", "Mot de Passe"], [email, password]]
    table2 = Table(data_auth, colWidths=[200, 200])
    table2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    table2.wrapOn(p, width, height)
    table2.drawOn(p, 50, y - 40)

    # Footer
    now = datetime.now()
    date_str = now.strftime("Document créé le %d/%m/%Y à %H:%M")
    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2, 30, date_str)

    # Finalisation
    p.showPage()
    p.save()
    buffer.seek(0)

    # Enregistrement dans le dossier media/pdfs/
    filename = f'utilisateur_{last_name}_{first_name}_{password[:5]}.pdf'
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, filename)

    with open(pdf_path, 'wb') as f:
        f.write(buffer.read())

    return pdf_path  # ou retourner l'URL relative si tu préfères

def send_email_user(mail, password, pdf_path):
    url = "http://127.0.0.1:8083/send/"  

    # Paramètres de la requête
    data = {
        "mail": mail.strip(),
        "body": password.strip(),          
        "file_attachement": pdf_path  
    }

    # Envoi de la requête
    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json=data
    )

   
    print("Statut HTTP:", response.status_code)
    try:
        print("Réponse:", response.json())
    except json.JSONDecodeError:
        print("Réponse non JSON :", response.text)

def create_user(request):
    user_role = EmailDatabase_instance.all_roles()
    return render(request, 'Admin/CreateUser.html',{"user_role":user_role})


def user_create(request) :
        if request.method == 'POST':
                name = request.POST.get('first_name', '')
                last_name = request.POST.get('last_name', '')
                email = request.POST.get('email', '')
                role = request.POST.get('role_agt', '')
                password = request.POST.get('mdp', '')
                print(name, last_name, email, role, password)
                print("--------------------------------")
                print(password)
                pdf_path = create_pdf(name, last_name, email, role, password)
                print(pdf_path)
                send_email_user(email, password, pdf_path)
                
                            
                

                try:
                    is_add = EmailDatabase_instance.create_user(name, last_name, email, role, password)
                    print(is_add)
                    messages.success(request, "Utilisateur créé avec succès !")
                    return redirect('/Admin/UserList')
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=500)
            

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
                    is_add = EmailDatabase_instance.update_user(name, last_name, email, role,user_id)
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
        
        
        
def UserList(request):
    user_list = EmailDatabase_instance.get_alls_users()
    user_role = EmailDatabase_instance.all_roles()
   
    return render(request, "Admin/UsersList.html",{
        "user_list" :user_list,
        "user_role":user_role
    })