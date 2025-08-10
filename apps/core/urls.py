from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('chatbot-api/', views.chatbot_api, name='chatbot_api'),
]
