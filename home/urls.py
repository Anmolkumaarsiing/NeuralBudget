from django.urls import path
from . import views
from .views import login_view, signup_view, logout_view, dashboard_view, add_transaction, income_tracker

urlpatterns =[
    path('', views.home, name='home'),
    path("login/", login_view, name="login"),
    path("signup/", signup_view, name="signup"),
    path("logout/", logout_view, name="logout"),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('add_transaction/', add_transaction, name='add_transaction'),  # Added this line
    path('income_tracker/', income_tracker, name='income_tracker'),  # New route
]
