import json
import google.generativeai as genai
from django.conf import settings
from datetime import datetime
from apps.common_utils.firebase_service import add_transaction, get_user_categories

def generate_transaction_batch(num_transactions: int, user_categories: list):
    """
    Generates a batch of hyper-realistic transaction data using an optimized Gemini API prompt.
    """
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    
    categories_str = ", ".join([f'"{c}"' for c in user_categories])

    prompt = f"""
    You are an AI data generator creating hyper-realistic financial data for a user in Vadodara, Gujarat, India.

    **User Profile & Constraints:**
    - Monthly Salary: ₹30,000 (credited on the 1st of the month).
    - Total Monthly Expenses: Must be approximately ₹25,000.
    - Location: Vadodara, Gujarat, India.

    **Your Task:**
    Generate a JSON array of exactly {num_transactions} unique and hyper-realistic transactions for this user.

    **CRITICAL INSTRUCTIONS:**
    1.  **Hyper-Realism & Granularity:** DO NOT use generic names. Be extremely specific down to the item level.
        -   **Correct:** `D-Mart: Onion (500g)`, `PVR Cinemas: Shaitaan Movie Ticket`, `Hariyali Restaurant: Paneer Butter Masala`, `Netflix Premium Subscription`.
        -   **Incorrect:** `Grocery shopping`, `Movie`, `Restaurant bill`.
    2.  **Local Context (Vadodara):** Use real, existing merchants, restaurants, and places.
        -   **Good examples:** Canara Coffee House, Mandap Restaurant, Inorbit Mall, D-Mart, Ratri Bazaar, Uber, Zomato, Swiggy.
        -   **Bad examples:** "Sursagar Lake Restaurant" (this does not exist).
    3.  **Accurate Categories:** Assign the single most accurate category from this list: {categories_str}.
    4.  **Financial Realism:** The sum of all expenses should reflect the user's budget. Create a mix of small daily purchases (like "chai", "snacks") and larger, less frequent ones (like "utility bill", "rent").
    5.  **Salary:** You MUST include one salary credit of exactly ₹30,000 with the category "Income", dated on the first day of the month.

    **Schema for each JSON object:**
    - `name`: (String) The hyper-realistic transaction name including merchant and item.
    - `category`: (String) One of the provided categories.
    - `amount`: (Float) A realistic amount in INR for the specific item.
    - `date`: (String) A date in "YYYY-MM-DD" format,in the year 2025.
    - `status`: (String) Must always be "Completed".

    The final output must be a single, valid JSON array only.
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(response_text)
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        return []

def add_generated_data_to_user(user_id, num_transactions):
    """
    Generates data and adds it to the user's Firestore collections.
    """
    user_categories = get_user_categories(user_id)
    if not user_categories:
        # Handle case where user has no categories, or provide a default list
        user_categories = ["Housing", "Groceries & Essentials", "Dining Out & Entertainment", "Transportation", "Utilities", "Healthcare & Insurance", "Subscriptions & OTT", "Shopping", "Education & Self-Development", "Income", "Other"]

    transactions = generate_transaction_batch(num_transactions, user_categories)
    if not transactions:
        raise Exception("Failed to generate transaction data from the AI.")

    added_count = 0
    for txn in transactions:
        collection = 'incomes' if txn.get('category') == 'Income' else 'expenses'
        try:
            # Convert date string to datetime object for Firestore
            txn['date'] = datetime.strptime(txn['date'], '%Y-%m-%d')
            add_transaction(user_id, txn, collection)
            added_count += 1
        except (ValueError, KeyError) as e:
            print(f"Skipping invalid transaction record: {txn}. Error: {e}")
            continue
    
    return added_count


# Add this new function to your datagen/services.py file
from apps.common_utils.firebase_service import db
from google.cloud.firestore_v1.base_query import FieldFilter

def delete_all_user_transactions(user_id):
    """
    Finds and deletes all documents in 'expenses' and 'incomes' collections
    for a given user_id.
    """
    collections_to_delete = ['expenses', 'incomes']
    deleted_count = 0

    for collection_name in collections_to_delete:
        # Query for all documents belonging to the user in the collection
        docs = db.collection(collection_name).where(
            filter=FieldFilter("userId", "==", user_id)
        ).stream()

        for doc in docs:
            doc.reference.delete()
            deleted_count += 1
            print(f"Deleted {doc.id} from {collection_name}")

    return deleted_count

# in apps/datagen/services.py

from datetime import datetime, timedelta
from collections import Counter
from apps.common_utils.firebase_service import db

def get_admin_dashboard_analytics():
    """
    Fetches and calculates key metrics for the admin dashboard from Firestore.
    """
    # 1. Get User Metrics
    user_profiles_ref = db.collection('user_profiles')
    all_users = list(user_profiles_ref.stream())
    total_users = len(all_users)

    # 2. Calculate New Users in the Last 7 Days
    seven_days_ago = datetime.now() - timedelta(days=7)
    new_users_last_7_days = 0
    for user in all_users:
        user_data = user.to_dict()
        created_at = user_data.get('created_at')
        # Ensure created_at is a datetime object before comparing
        if isinstance(created_at, datetime) and created_at.replace(tzinfo=None) > seven_days_ago:
            new_users_last_7_days += 1

    # 3. Analyze Top 5 Spending Categories across ALL users
    expenses_ref = db.collection('expenses')
    all_expenses = expenses_ref.stream()
    
    category_counts = Counter()
    for expense in all_expenses:
        expense_data = expense.to_dict()
        category = expense_data.get('category')
        if category:
            # Ensure amount is a number before adding
            amount = expense_data.get('amount', 0)
            if isinstance(amount, (int, float)):
                category_counts[category] += amount

    # Get the top 5 most common categories by total spend
    top_5_categories = category_counts.most_common(5)
    
    # Format for Chart.js
    top_categories_chart_data = {
        'labels': [category for category, amount in top_5_categories],
        'values': [amount for category, amount in top_5_categories]
    }

    return {
        'total_users': total_users,
        'new_users_last_7_days': new_users_last_7_days,
        'top_categories_chart': top_categories_chart_data
    }

# Add this new function to your datagen/services.py file

def generate_historical_data(user_id, constraints):
    """
    Generates a batch of historical transaction data based on user constraints.
    """
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    
    # --- NEW OPTIMIZED PROMPT ---
    prompt = f"""
    You are an AI data generator for "Neural Budget AI". Your task is to create a JSON array of hyper-realistic historical transactions for a user.

    **User Profile & Constraints:**
    - Location for all expenses: {constraints.get('district', 'Vadodara')}, India.
    - Date Range: All transaction dates MUST be between {constraints.get('start_date')} and {constraints.get('end_date')}.
    - Amount Range: All transaction amounts MUST be between ₹{constraints.get('min_amount')} and ₹{constraints.get('max_amount')}.
    - Number of transactions to generate: {constraints.get('num_transactions')}

    **CRITICAL INSTRUCTIONS:**
    1.  **Hyper-Realism & Granularity:** Be extremely specific. Instead of "Groceries", generate "D-Mart: Onion (1kg)".
    2.  **Local Context:** Use real, existing merchants and places relevant to the specified district.
    3.  **Accurate Categories:** Assign the single most accurate category to each transaction.
    4.  **Financial Realism:** Ensure the amounts are realistic for the items described and fall within the specified range.

    **Schema for each JSON object:**
    - `name`: (String) The hyper-realistic transaction name.
    - `category`: (String) One of: "Groceries & Essentials", "Dining Out & Entertainment", "Transportation", "Utilities", "Shopping", "Other".
    - `amount`: (Float) A realistic amount in INR within the specified range.
    - `date`: (String) A date in "YYYY-MM-DD" format within the specified range.
    - `status`: (String) Must always be "Completed".

    The output must be a single, valid JSON array only.
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip().replace("```json", "").replace("```", "")
        transactions = json.loads(response_text)
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        return []

    # Add the generated data to the user's account
    added_count = 0
    for txn in transactions:
        try:
            txn['date'] = datetime.strptime(txn['date'], '%Y-%m-%d')
            add_transaction(user_id, txn, 'expenses')
            added_count += 1
        except (ValueError, KeyError) as e:
            print(f"Skipping invalid transaction record: {txn}. Error: {e}")
            continue
            
    return added_count
