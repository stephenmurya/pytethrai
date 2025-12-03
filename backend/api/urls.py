from django.urls import path
from . import views

urlpatterns = [
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/me/', views.user_view, name='me'),
    path('auth/register/', views.register_view, name='register'),
    path('chat/send/', views.chat_send, name='chat_send'),
    path('chat/history/', views.chat_history, name='chat_history'),
    path('chat/<uuid:chat_id>/', views.get_chat, name='get_chat'),
    path('models/', views.get_models, name='get_models'),
]
