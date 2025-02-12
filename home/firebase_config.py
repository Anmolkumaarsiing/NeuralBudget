# import os
# import firebase_admin
# from firebase_admin import credentials

# BASE_DIR =os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# FIREBASE_CREDENTIALS_PATH = os.path.join(BASE_DIR, 'firebase_auth_key.json')

# cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
# print("cred",cred)
# firebase_admin.initialize_app(cred)

import os
import firebase_admin
from firebase_admin import credentials
from neural_budget.settings import BASE_DIR

FIREBASE_SIGN_IN_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
FIREBASE_API_KEY = "AIzaSyAODPU-ly_r-9ZcT2xbFM5vA2a9jt1c4UQ"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(BASE_DIR, "firebase_auth_key.json")
print(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
try :
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)
    print("Firebase initialized")
except Exception as e:
    print(f"Firebase initialization error: {str(e)}")
