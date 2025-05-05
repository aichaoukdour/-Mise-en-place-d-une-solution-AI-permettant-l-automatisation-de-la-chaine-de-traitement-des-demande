# User Views

from pyexpat.errors import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from Db_handler.Database import EmailDatabase
EmailDatabase_instance = EmailDatabase()


def create_user(request):
    user_role = EmailDatabase_instance.all_roles()
    return render(request, 'Admin/CreateUser.html',{"user_role":user_role})


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
        
        
        
def UserList(request):
    user_list = EmailDatabase_instance.get_alls_users()
    user_role = EmailDatabase_instance.all_roles()
   
    return render(request, "Admin/UsersList.html",{
        "user_list" :user_list,
        "user_role":user_role
    })
