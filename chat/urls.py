from django.urls import path
from .views import chat
from .views import chat, get_chat_history

urlpatterns = [
    path('chat/', chat, name='chat'),
    path('chat/history/<int:user_id>/', get_chat_history, name='get_chat_history'),
]