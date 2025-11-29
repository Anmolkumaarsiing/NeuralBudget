import os
import firebase_admin
from firebase_admin import credentials, firestore
from neural_budget.settings import BASE_DIR # To be updated
from dotenv import load_dotenv
load_dotenv()

FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')

firebase_key_path = os.path.join(BASE_DIR, "firebase_key.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = firebase_key_path
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_key_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
else:
    print("Firebase already initialized")
