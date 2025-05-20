from django.urls import path
from ChatBot.views.chatbot import *
from .views import *
from .views.auth_views import *  # Import all views from auth_views, including accueil
from .views.auth_views import change_password_view
from .views.mail_views import *
from .views.user_views import *
from .views.misc_views import *
from .views.dashboard_views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', accueil, name='home'),  # Root URL now works with proper import
    path('accueil', accueil_inwi, name='accueil_inwi'),
    path('check-email/', check_email_view, name='check_email'),
    path('change-password/', change_password_view, name='change_password'),
    path('change-password-page/', change_password_page, name='change_password_page'),
    path('get-user-role/', get_user_role, name='get_user_role'),
    path('skip-password-change/', skip_password_change, name='skip_password_change'),
    path('suivi', get_all_mails_by_user, name='suivi'),
    path('logout/', logout_view, name='logout'),
    path('download_excel/<str:id_msg>/', download_excel_view, name='download_excel_user'),
    path('Admin/download_excel/<str:id_msg>/', download_excel_view, name='download_excel'),
    path('suivi/<str:id>/', suiviinfo_user, name='request_status'),
    path('Admin/suivi/<str:id>/', suiviinfo_user, name='Admin_request_status'),
    path('get_conversation/<str:id>/', conversation_user, name='get_conversation'),
    path('chat', chat, name='chatbot'),
    path('Admin/infosuivi/<str:id>/', suiviinfo, name='infosuivi'),
    path('Admin/administration', admin, name='administrationinfo'),
    path('admindash', admindash, name='admindash'),
    path('Admin/OverdueRequests', OverdueRequests, name='OverdueRequests'),
    path('Admin/PendingRequests', PendingRequests, name='PendingRequests'),
    path('listrequests', listrequests, name='listrequests'),
    path('Admin/UserList', UserList, name='UserList'),
    path('Admin/allrequests', allrequests, name='allrequests'),
    path('Admin/create_user', create_user, name='create_user'),
    path('role_management', role_management, name='role_management'),
    path('Admin/blacklist', blacklist, name='blacklist'),
    path('Admin/get_all_user_mail/<str:id>/', get_all_mails_by_user_Admin, name='get_all_mails_by_user'),
    path('Admin/user_create', user_create, name='user_create'),
    path('Admin/get_conversation/<str:id>/', conversation, name='admin_conversation'),
    path('Admin/delete_user', delete_user, name='delete_user'),
    path('Admin/Update_User', update_user, name='update_user'),
    path('Admin/Update/<str:id>/', user_f, name='update'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)