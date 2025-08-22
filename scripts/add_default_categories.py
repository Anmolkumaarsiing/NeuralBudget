import os
import sys
import django

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neural_budget.settings')
django.setup()

from apps.common_utils.firebase_service import copy_default_categories_to_user, delete_user_categories,get_user_categories

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_default_categories.py <user_id>")
        sys.exit(1)

    user_id = sys.argv[1]
    print(f"Attempting to add default categories for user ID: {user_id}")

    try:
        # delete_user_categories(user_id)  # Clear existing categories to avoid duplicates
        copy_default_categories_to_user(user_id)
        print(get_user_categories(user_id))
        print(f"Successfully added default categories for user ID: {user_id}")
    except Exception as e:
        print(f"Error adding default categories for user ID {user_id}: {e}")
        sys.exit(1)
