import os
import firebase_admin
from firebase_admin import credentials, firestore
# from neural_budget.settings import BASE_DIR # To be updated
from dotenv import load_dotenv
load_dotenv()

FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')

# path = os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(BASE_DIR, "firebase_key.json") # To be updated
path = os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join("D:/NeuralBudget", "firebase_key.json") # Placeholder
if not firebase_admin._apps:
    cred = credentials.Certificate(path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
else:
    print("Firebase already initialized")
