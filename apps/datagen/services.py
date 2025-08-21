import json
import google.generativeai as genai
from django.conf import settings
from datetime import datetime
from apps.common_utils.firebase_service import add_transaction

def generate_transaction_batch(num_transactions: int):
    """
    Generates a batch of realistic transaction data using the Gemini API.
    """
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    
    prompt = f"""
    You are an AI data generator for "Neural Budget AI", creating realistic financial data for a user in Vadodara, India.

    **User Profile:**
    - Monthly Salary: ₹30,000
    - Monthly Expenses: Approx. ₹25,000

    **Task:**
    Generate a JSON array of exactly {num_transactions} unique and hyper-realistic transactions.

    **Instructions:**
    1.  **Hyper-Realism:** Do NOT use generic names. Be specific (e.g., "D-Mart: Amul Gold Milk (1L)", "Uber ride to Alkapuri").
    2.  **Local Context:** Use merchants and places relevant to Vadodara, India.
    3.  **Accurate Categories:** Assign a correct category to each transaction.
    4.  **Financial Sense:** The spending should reflect the user's budget.

    **Schema:** `name`, `category`, `amount`, `date` (YYYY-MM-DD), `status` ("Completed").
    The output must be a single, valid JSON array.
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
    transactions = generate_transaction_batch(num_transactions)
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