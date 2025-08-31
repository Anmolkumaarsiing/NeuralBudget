from apps.common_utils.firebase_service import refresh_firebase_token as refresh_firebase_token_service

def is_authenticated(request):
    id_token = request.session.get('id_token')
    # print(id_token)
    print(f"[DEBUG] is_authenticated called. id_token in session: {id_token is not None}")
    return id_token is not None

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

def get_user_full_name(user_profile):
    first_name = user_profile.get('first_name', '')
    last_name = user_profile.get('last_name', '')
    
    full_name = f"{first_name} {last_name}".strip()
    
    print(f"[DEBUG] get_user_full_name called. Full name: {full_name}")
    if not full_name:
        return user_profile.get('display_name', user_profile.get('email', 'User'))
    return full_name

def refresh_firebase_token(request):
    return refresh_firebase_token_service(request)
