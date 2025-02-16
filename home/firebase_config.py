import os
import firebase_admin
from firebase_admin import credentials, firestore
from neural_budget.settings import BASE_DIR
from dotenv import load_dotenv
load_dotenv()

FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')

path = os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(BASE_DIR, "firebase_key.json")
if not firebase_admin._apps:
    cred = credentials.Certificate(path)
    firebase_admin.initialize_app(cred)
    print("Firebase initialized, app created")
    db = firestore.client()
else:
    print("Firebase already initialized")

