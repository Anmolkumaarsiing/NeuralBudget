import os
import sys
import django

# Add project root to path and setup Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neural_budget.settings')
django.setup()

import argparse
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from firebase_admin import firestore, credentials, initialize_app,auth

# Load env first
load_dotenv()

# Import Firebase service
from apps.common_utils.firebase_service import  add_transaction

# === Category Logic ===
CATEGORY_KEYWORDS = {
    "Dining Out & Entertainment": ["restaurant", "cafe", "food", "zomato", "swiggy", "movie", "concert", "netflix", "spotify"],
    "Education & Self-Development": ["course", "udemy", "book", "training", "workshop", "education"],
    "Groceries & Essentials": ["grocery", "supermarket", "essentials", "milk", "vegetables"],
    "Healthcare & Insurance": ["hospital", "pharmacy", "medicine", "insurance", "doctor", "clinic"],
    "Housing": ["rent", "mortgage", "apartment", "housing", "property", "home"],
    "Transportation": ["uber", "ola", "flight", "train", "bus", "taxi", "fuel"],
    "Utilities": ["electricity", "water", "internet", "phone", "gas"],
    "Other": []
}

def generate_transaction_data(num_transactions: int):
    """Generates a list of meaningful transaction data using a generative AI."""
    llm = HuggingFaceEndpoint(
        repo_id="mistralai/Mistral-7B-Instruct-v0.3",
        task="text-generation",
        huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
        max_new_tokens=2000,  # Increased for more data
        temperature=0.8,
    )
    model = ChatHuggingFace(llm=llm)

    categories = list(CATEGORY_KEYWORDS.keys())

    prompt = f"""
    You are an AI assistant that generates realistic transaction data for a budgeting app.
    Your task is to generate a JSON array of exactly {num_transactions} unique and meaningful transactions.

    **Schema:**
    - `name`: A descriptive name for the transaction (e.g., "Weekly groceries", "Dinner with friends").
    - `category`: Must be one of the following: {categories}.
    - `amount`: A realistic float value.
    - `date`: A date in YYYY-MM-DD format.
    - `status`: Must be one of the following: ["Pending", "Completed", "Failed", "Cancelled"].

    **Instructions:**
    - Generate exactly {num_transactions} transactions.
    - Ensure the data is diverse and realistic.
    - The output must be a single, valid JSON array.

    **Example:**
    [
        {{
            "name": "Monthly rent payment",
            "category": "Housing",
            "amount": 15000.00,
            "date": "2025-07-01",
            "status": "Completed" 
        }}
    ]
    """

    response = model.invoke(prompt)
    response_text = response.content if hasattr(response, 'content') else str(response)

    try:
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0]
        
        transactions = json.loads(response_text.strip())
        return transactions
    except (json.JSONDecodeError, IndexError) as e:
        print(f"Error parsing LLM response: {e}")
        print(f"Raw response: {response_text}")
        return []

def add_generated_transactions(email: str, num_transactions: int):
    """Generates and adds meaningful transactions for a user."""
    user = auth.get_user_by_email(email)
    if not user:
        print(f"No user found with email: {email}")
        return

    user_id = user.uid
    print(f"Generating {num_transactions} transactions for user: {user_id} ({email})")

    transactions = generate_transaction_data(num_transactions)

    if not transactions:
        print("Failed to generate transaction data.")
        return

    for transaction in transactions:
        # transaction["timestamp"] = datetime.now().isoformat()
        # transaction["user_id"] = user_id
        add_transaction(user_id, transaction, 'expenses')
        print(f"Added transaction: {transaction['name']}")

    print(f"Successfully added {len(transactions)} transactions for user: {email}")

if __name__ == "__main__":

    # parser = argparse.ArgumentParser(description="Generate and add meaningful transaction data for a user.")
    # parser.add_argument("email", type=str, help="The email of the user.")
    # parser.add_argument("num_transactions", type=int, help="The number of transactions to generate.")
    # args = parser.parse_args()
    email = 'thuraheinsyh@gmail.com'
    num_transactions = 10
    # Initialize Firebase Admin SDK
    if not os.path.exists('firebase_key.json'):
        print("Error: firebase_key.json not found in the project root.")
        sys.exit(1)

    cred = credentials.Certificate('firebase_key.json')
    # initialize_app(cred)

    add_generated_transactions(email,num_transactions)
