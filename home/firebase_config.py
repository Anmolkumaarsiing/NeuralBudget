import os
import firebase_admin
from firebase_admin import credentials
from neural_budget.settings import BASE_DIR
from dotenv import load_dotenv
load_dotenv()

FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(BASE_DIR, "firebase_key.json")
try :
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)
    print("Firebase initialized")
except Exception as e:
    print(f"Firebase initialization error: {str(e)}")
