from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages

class AdminRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        

    def __call__(self, request):
       
            return self.get_response(request)

       
        
            



    # middleware.py
class DatabaseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Remove: EmailDatabase_instance.engine.dispose()
        return response
    
    
    # middleware.py
import logging
logger = logging.getLogger(__name__)

# EmailReporting/middleware.py
import logging

logger = logging.getLogger(__name__)

class RedirectDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 302:
            logger.debug(f"Redirect from {request.path} to {response.get('Location', 'unknown')}")
        return response