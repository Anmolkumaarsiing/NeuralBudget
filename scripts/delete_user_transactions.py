import os
import sys
import django

# Add project root to path and setup Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neural_budget.settings')
django.setup()

from firebase_admin import credentials, initialize_app, auth, firestore

# Import the correctly defined delete_transaction function and the db instance
from apps.common_utils.firebase_service import delete_transaction
from apps.common_utils.firebase_config import db

collection = 'expenses'

def delete_all_user_transactions(email: str):
    """
    Fetches a user by email, finds all their transactions in the 'transactions'
    collection, and deletes them one by one.
    """
    try:
        # Get user by email using the Firebase Admin SDK
        user = auth.get_user_by_email(email)
        user_id = user.uid
        print(f"Found user: {user_id} for email: {email}")

        # Fetch all transactions for the user
        transactions_ref = db.collection(collection).where('userId', '==', user_id)
        docs = list(transactions_ref.stream()) # Use list to get all docs at once

        if not docs:
            print(f"No transactions found for user: {email}")
            return

        print(f"Found {len(docs)} transactions. Proceeding with deletion...")

        # Iterate over the documents and delete them
        for doc in docs:
            transaction_id = doc.id
            print(f"Deleting transaction: {transaction_id}")
            # The correct function call is delete_transaction(transaction_id, collection_name)
            delete_transaction(transaction_id, collection)

        print(f"Successfully deleted all {len(docs)} transactions for user: {email}")

    except auth.UserNotFoundError:
        print(f"Error: No user found with the email: {email}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    # --- IMPORTANT ---
    # Set the email of the user whose transactions you want to delete.
    user_email_to_delete = "thuraheinsyh@gmail.com"  # <--- CHANGE THIS EMAIL

    print("Initializing Firebase...")
    # Ensure you have the firebase_key.json in the root of the project
    if not os.path.exists('firebase_key.json'):
        print("Error: firebase_key.json not found in the project root.")
        sys.exit(1)

    # Initialize Firebase Admin SDK
    # Check if the app is already initialized to prevent errors
    if not hasattr(django, 'firebase_app'):
        cred = credentials.Certificate('firebase_key.json')
        # django.firebase_app = initialize_app(cred)

    if not user_email_to_delete or user_email_to_delete == "user@example.com":
        print("Please edit the script and set the `user_email_to_delete` variable.")
    else:
        delete_all_user_transactions(user_email_to_delete)