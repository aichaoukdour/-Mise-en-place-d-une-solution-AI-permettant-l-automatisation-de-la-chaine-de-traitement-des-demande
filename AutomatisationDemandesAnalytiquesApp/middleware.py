from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages

class AdminRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        

    def __call__(self, request):
        user_role = request.session.get('user_role')
        if request.path in ['/favicon.ico', '/check-email/']:
            return self.get_response(request)

        print("user_role",user_role)

        if user_role == 'admin' and not request.path.lower().startswith("/admin") and request.path != "/":
              return redirect('/') 

       
        if user_role != 'admin' and request.path.lower().startswith("/admin"):
              return redirect('/') 
 
        
        if user_role == None and request.path != "/":
            return redirect('/')
        
            



        return self.get_response(request)
