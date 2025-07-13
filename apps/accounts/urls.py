from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns =[
    path("login/", views.login_view, name="login"),
    path("signup/", views.register_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path('refresh_token/', views.refresh_token_view, name='refresh_token'),
    path('profile/', views.profile_view, name='profile'),
    path('update_profile/', views.update_profile_view, name='update_profile'),
    path('upload_profile_picture/', views.upload_profile_picture_view, name='upload_profile_picture'),
    path('send_password_reset_email/', views.send_password_reset_email_view, name='send_password_reset_email'),
]
