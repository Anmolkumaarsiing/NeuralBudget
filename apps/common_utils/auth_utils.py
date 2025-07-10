def is_authenticated(request):
    return request.session.get('id_token') is not None

from django.core.exceptions import ValidationError
from firebase_admin import auth

def validate_input(data):
    if not data.get("username"):
        raise ValidationError("Username is required.")
    if not data.get("email"):
        raise ValidationError("Email is required.")
    if not data.get("idToken"):
        raise ValidationError("Firebase ID token is required.")

def get_user_id(request):
    return request.session.get('user_id')

def get_email(request):
    return request.session.get('email')