from django.urls import path

from ChatBot.views.chatbot import *



from .views import *



from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("suivi/<str:id>/", suiviinfo_user, name="request_status"), 
    path("get_conversation/<str:id>/", conversation_user, name="get_conversation"), 
    path("chat", chat, name="chatbot"),
    path("suivi", get_all_mails_by_user, name="suivi"),
    path("Admin/infosuivi/<str:id>/", suiviinfo, name="infosuivi"),
    path("Admin/administration", admin, name="administrationinfo"),
    path("admindash", admindash, name="admindash"),
    path("Admin/OverdueRequests", OverdueRequests, name="OverdueRequests"),
    path("Admin/PendingRequests", PendingRequests, name="PendingRequests"),
    path("listrequests", listrequests, name="listrequests"),
    path("Admin/UserList", UserList, name="UserList"),
    path("Admin/allrequests", allrequests, name="allrequests"),
    path("Admin/create_user", create_user, name="create_user"),
    path("role_management", role_management, name="role_management"),
    path("Admin/blacklist", blacklist, name="blacklist"),
    path("", accueil, name="home"),
    path('check-email/', check_email_view, name='check_email'),
    path('Admin/get_all_user_mail/<str:id>/', get_all_mails_by_user_Admin, name='get_all_mails_by_user'),
    path('Admin/user_create',user_create,name='user_create'),
    path('Admin/get_conversation/<str:id>/',conversation,name='admin_conversation'),
    path('Admin/delete_user',delete_user,name='delete_user'),
    path('Admin/Update_User',update_user,name='update_user'),
    path('Admin/Update/<str:id>/',user_f,name='update'),
    path('accueil', accueil_inwi, name='accueil_inwi'),

   


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
