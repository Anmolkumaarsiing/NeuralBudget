from google.cloud.firestore_v1.base_query import FieldFilter
from apps.common_utils.firebase_config import db
from firebase_admin import auth, exceptions as firebase_exceptions
import requests
from apps.common_utils.firebase_config import FIREBASE_API_KEY

FIREBASE_SIGN_IN_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"

def get_user_categories(user_id):
    """Fetch categories for a specific user."""
    print(f"[DEBUG] get_user_categories called for user_id: {user_id}")
    categories_ref = db.collection("categories").where(filter=FieldFilter("userId", "==", user_id))
    docs = categories_ref.stream()
    categories = [doc.to_dict()["name"] for doc in docs]
    print(f"[DEBUG] Fetched categories: {categories}")
    return categories

def copy_default_categories_to_user(user_id):
    """Copies default categories to a new user."""
    print(f"[DEBUG] Attempting to copy default categories for user: {user_id}")
    default_categories_ref = db.collection('default_categories').stream()
    categories_copied = 0
    for category in default_categories_ref:
        category_data = category.to_dict()
        db.collection('categories').add({
            'name': category_data['name'],
            'userId': user_id
        })
        print(f"[DEBUG] Added category '{category_data['name']}' to user {user_id}'s collection.")
        categories_copied += 1
    print(f"[DEBUG] Finished copying. Total categories copied: {categories_copied}")

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

def get_transactions(user_id,collection,limit=10, start_after_doc_id=None):
    print(f"get_transactions: user_id={user_id}, collection={collection}, limit={limit}, start_after_doc_id={start_after_doc_id}")
    try:
        transactions_ref = db.collection(collection)
    except Exception as e:
        print(e)
        return []
    # copy_default_categories_to_user(user_id)
    query = transactions_ref.where(filter=FieldFilter("userId", "==", user_id))
    
    if start_after_doc_id:
        start_after_doc = transactions_ref.document(start_after_doc_id).get()
        print(f"start_after_doc exists: {start_after_doc.exists}")
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
