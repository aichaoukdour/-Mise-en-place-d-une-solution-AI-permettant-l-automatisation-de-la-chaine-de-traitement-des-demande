from django.urls import path
from ChatBot.views.chatbot import *



from .views import *



from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    
    path('chat/', index, name='index'),
    path('all_conversations/', all_conversations, name='all_conversations'),
    path('all_msg_by_conv/<str:conv_id>/', all_msg_by_conv, name='all_msg_by_conv'),
    path('create_conversation/', create_conversation, name='create_conversation'),
    path('update_conversation/<str:msg_user>/<uuid:id_msg>/', update_conversation, name='update_conversation'),
    path('new_excel/<uuid:id_msg>/', download_excel_view, name='new_excel'),
]

    