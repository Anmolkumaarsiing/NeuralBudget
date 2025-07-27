from google.cloud.firestore_v1.base_query import FieldFilter
from apps.common_utils.firebase_config import db
from firebase_admin import auth, exceptions as firebase_exceptions, firestore
import requests
from apps.common_utils.firebase_config import FIREBASE_API_KEY
from django.conf import settings
import os

FIREBASE_SIGN_IN_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
DEFAULT_PROFILE_PIC_URL = os.path.join(settings.MEDIA_URL, 'profile_photos', 'default_profile.jpg') # Assuming .jpeg

def get_user_categories(user_id):
    """Fetch categories for a specific user."""
    categories_ref = db.collection("categories").where(filter=FieldFilter("userId", "==", user_id))
    docs = categories_ref.stream()
    return [doc.to_dict()["name"] for doc in docs]

def copy_default_categories_to_user(user_id):
    """Copies default categories to a new user."""
    default_categories_ref = db.collection('default_categories').stream()
    for category in default_categories_ref:
        category_data = category.to_dict()
        db.collection('categories').add({
            'name': category_data['name'],
            'userId': user_id
        })

def add_category(user_id, category_name):
    """Adds a new category for a user."""
    db.collection('categories').add({
        'name': category_name,
        'userId': user_id
    })

def add_transaction(user_id, transaction_data,collection):
    """Add a transaction to Firestore."""
    # print(typ)
    transactions_ref = db.collection(collection)
    transactions_ref.add({
        "userId": user_id,
        **transaction_data
    })

def create_user_profile(uid, email, display_name):
    """Creates an initial user profile document in Firestore."""
    user_profile_ref = db.collection('user_profiles').document(uid)
    user_profile_ref.set({
        'email': email,
        'display_name': display_name,
        'created_at': firestore.SERVER_TIMESTAMP,
        'photo_url': DEFAULT_PROFILE_PIC_URL # Set default profile picture
    })

def get_user_profile(uid):
    """Retrieves a user profile document from Firestore."""
    user_profile_ref = db.collection('user_profiles').document(uid)
    doc = user_profile_ref.get()
    if doc.exists:
        profile_data = doc.to_dict()
        # Ensure photo_url exists, default if not
        if 'photo_url' not in profile_data or not profile_data['photo_url']:
            profile_data['photo_url'] = DEFAULT_PROFILE_PIC_URL
        return profile_data
    return None

def update_user_profile(uid, data):
    """Updates a user profile document in Firestore."""
    user_profile_ref = db.collection('user_profiles').document(uid)
    user_profile_ref.update(data)

def update_user_profile_picture(uid, photo_url):
    """Updates only the profile picture URL in a user's profile."""
    user_profile_ref = db.collection('user_profiles').document(uid)
    user_profile_ref.update({'photo_url': photo_url})

def get_transactions(user_id,collection,limit=10, start_after_doc_id=None):

    try:
        transactions_ref = db.collection(collection)
    except Exception as e:
        print(e)
        return []
    # copy_default_categories_to_user(user_id)
    query = transactions_ref.where(filter=FieldFilter("userId", "==", user_id))
    
    if start_after_doc_id:
        start_after_doc = transactions_ref.document(start_after_doc_id).get()
        if not start_after_doc.exists:
            return [] # No more documents to fetch
        query = query.start_after(start_after_doc)

    query = query.limit(limit).get()
    
    transactions = []
    for doc in query:
        transaction = doc.to_dict()
        transaction["id"] = doc.id
        transactions.append(transaction)
    return transactions

def add_category(category_name):
    """Add a category to Firestore."""
    categories_ref = db.collection("categories")
    categories_ref.add({
        "name": category_name
    })

def delete_transaction(transaction_id, collection):
    """Delete a transaction from Firestore."""
    db.collection(collection).document(transaction_id).delete()

def firebase_login(email, password):
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    headers = {
        "Content-Type": "application/json"
    }
    params = {"key": FIREBASE_API_KEY}
    try:
        response = requests.post(FIREBASE_SIGN_IN_URL, json=payload, params=params, headers=headers)
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
