import os
from django.conf import settings
import firebase_admin
from firebase_admin import credentials

# Get the absolute path to your service account key file
cert_path = os.path.join(settings.BASE_DIR, 'firebase_auth_key.json')

# Initialize Firebase Admin with your service account credentials
cred = credentials.Certificate(cert_path)
default_app = firebase_admin.initialize_app(cred)