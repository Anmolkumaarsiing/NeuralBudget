from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns =[
    path("login/", views.login_view, name="login"),
    path("signup/", views.register_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path('refresh_token/', views.refresh_token_view, name='refresh_token'),
]
