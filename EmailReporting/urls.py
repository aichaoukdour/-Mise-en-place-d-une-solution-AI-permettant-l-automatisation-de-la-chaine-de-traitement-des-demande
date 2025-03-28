from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("suivi/<str:message_id>/", request_status, name="request_status"),  # Suivi d'une demande spécifique
    path("hhh", list_requests, name="list_requests"),
    path("chat", chat, name="chatbot"),
    path("suivi", suivi, name="suivi"),
    path("infosuivi", suiviinfo, name="infosuivi"),
    path("administration", admin, name="administrationinfo"),
    path("admindash", admindash, name="admindash"),
    path("OverdueRequests", OverdueRequests, name="OverdueRequests"),
    path("PendingRequests", PendingRequests, name="PendingRequests"),
    path("listrequests", listrequests, name="listrequests"),
    path("UserList", UserList, name="UserList"),
    path("allrequests", allrequests, name="allrequests"),
    path("create_user", create_user, name="create_user"),
    path("role_management", role_management, name="role_management"),
    path("blacklist", blacklist, name="blacklist"),
    path("", accueil, name="home"),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
