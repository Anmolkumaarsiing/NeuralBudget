from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from firebase_admin import auth

def validate_input(data):
    if not data.get("username"):
        raise ValidationError("Username is required.")
    if not data.get("email"):
        raise ValidationError("Email is required.")
    if not data.get("idToken"):
        raise ValidationError("Firebase ID token is required.")

def verify_token(id_token):
    print("In verify_token")
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Token verification error: {str(e)}")
        return False

def get_user_id(id_token):
    print("In get_user_id")
    try:
        email = verify_token(id_token).get('email')
        return email
    except Exception as e:
        print(f"Error getting user ID: {str(e)}")