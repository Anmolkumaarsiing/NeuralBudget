from firebase_admin import auth, exceptions as firebase_exceptions
from django.http import JsonResponse
import requests
from home.firebase_config import FIREBASE_API_KEY

FIREBASE_SIGN_IN_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"

def firebase_login(email, password):
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    params = {"key": FIREBASE_API_KEY}
    try:
        response = requests.post(FIREBASE_SIGN_IN_URL, json=payload, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        raise e

def verify_firebase_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token, clock_skew_seconds=30)
        return decoded_token
    except firebase_exceptions.FirebaseError as e:
        raise e

def is_authenticated(request):
    return request.session.get('id_token') is not None

