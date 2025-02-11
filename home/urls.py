from django.urls import path
from . import views
from .views import login_view, signup_view, logout_view, dashboard_view

urlpatterns = [
    path('', views.home, name='home'),
    path("login/", login_view, name="login"),
    path("signup/", signup_view, name="signup"),
    path("logout/", logout_view, name="logout"),
    path('dashboard/', dashboard_view, name='dashboard'),
]