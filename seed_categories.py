import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apps.common_utils.firebase_config import db

DEFAULT_CATEGORIES = [
    "Housing", "Utilities", "Groceries", "Transportation", "Debt Payments",
    "Healthcare", "Savings & Investments", "Entertainment & Dining",
    "Shopping & Personal Care", "Education & Self-Development", "Other"
]

def seed_categories():
    """Seeds the Firestore database with default categories."""
    print("Seeding default categories...")
    for category_name in DEFAULT_CATEGORIES:
        # Check if category already exists
        category_ref = db.collection('default_categories').where('name', '==', category_name)
        if not category_ref.get():
            db.collection('default_categories').add({'name': category_name})
            print(f"Added category: {category_name}")
        else:
            print(f"Category already exists: {category_name}")
    print("Seeding complete.")

if __name__ == "__main__":
    seed_categories()
