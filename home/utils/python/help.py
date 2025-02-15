from django.core.exceptions import ValidationError
from firebase_admin import auth

def validate_input(data):
    if not data.get("username"):
        raise ValidationError("Username is required.")
    if not data.get("email"):
        raise ValidationError("Email is required.")
    if not data.get("idToken"):
        raise ValidationError("Firebase ID token is required.")

def verify_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token,clock_skew_seconds=5)
        return decoded_token
    except Exception as e:
        print("In verify_token")
        print(f"Token verification error: {str(e)}")
        raise