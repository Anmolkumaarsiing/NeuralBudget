from django.urls import path
from . import views
app_name = 'home'
urlpatterns = [
    path('', views.home, name='home'),
    path("login/", views.login_view, name="login"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("signup/", views.register_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
]
