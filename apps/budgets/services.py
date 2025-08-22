# in apps/budgets/services.py

import json
import google.generativeai as genai
from django.conf import settings
from apps.common_utils.firebase_service import get_user_categories, add_transaction, get_transactions, set_document
from google.cloud.firestore_v1.base_query import FieldFilter
from apps.common_utils.firebase_config import db # Import db
from datetime import datetime # Import the datetime module

# --- Service functions for Budgeting ---

def get_categories(user_id):
    return get_user_categories(user_id)

def set_budget(user_id, category, budget, period):
    budgets_ref = db.collection("budgets")
    
    # Query for an existing budget for this user and category
    query = budgets_ref.where(filter=FieldFilter("userId", "==", user_id)).where(filter=FieldFilter("category", "==", category)).limit(1)
    docs = query.get()

    doc_id = None
    for doc in docs:
        doc_id = doc.id
        break # Should only be one, due to limit(1)

    budget_data = {
        "userId": user_id,
        "category": category,
        "budget": budget,
        "period": period
    }

    if doc_id:
        # Update existing budget
        set_document("budgets", doc_id, budget_data)
    else:
        # Create new budget (Firestore will auto-generate ID)
        add_transaction(user_id, budget_data, "budgets") # Re-using add_transaction for new entries

def get_budgets(user_id):
    all_budgets = get_transactions(user_id, "budgets")
    latest_budgets = {}

    for budget_doc in all_budgets:
        category = budget_doc.get('category')
        doc_id = budget_doc.get('id') # Assuming 'id' field is added by get_transactions

        if category:
            if category not in latest_budgets or (doc_id and doc_id > latest_budgets[category].get('id', '')):
                latest_budgets[category] = budget_doc
    
    return list(latest_budgets.values())

# --- Service functions for Smart Saver (Stateless) ---

def create_smart_saver_plan(data):
    """
    Calls Gemini to generate a warm, friendly 'Smart Saver' plan
    WITHOUT saving anything to the database — now budget-aware and realistic.
    Refuses impossible savings targets.
    """

    # Convert values to numbers safely
    try:
        income = float(data.get('income', 0))
        expenses = float(data.get('expenses', 0))
        goal_amount = float(data.get('goal_amount', 0))
        timeframe = int(data.get('timeframe', 0))
    except ValueError:
        return {
            "title": "Invalid Input ❌",
            "summary": "Income, expenses, goal amount, and timeframe must be numbers.",
            "monthly_savings_target": 0,
            "plan_steps": [],
            "chart_data": {"labels": [], "values": []}
        }

    possible_monthly_saving = max(0, income - expenses)
    total_possible_saving = possible_monthly_saving * timeframe

    # Reject if goal is not possible
    if possible_monthly_saving <= 0 or total_possible_saving < goal_amount:
        return {
            "title": "Goal Not Possible 😔",
            "summary": (
                f"Your monthly income is ₹{income} and your expenses are ₹{expenses}. "
                f"This means you can save only ₹{possible_monthly_saving} per month. "
                f"In {timeframe} months, the maximum you can save is ₹{total_possible_saving}, "
                f"which is less than your goal of ₹{goal_amount}. "
                "Try reducing your goal amount or increasing your saving period."
            ),
            "monthly_savings_target": possible_monthly_saving,
            "plan_steps": [],
            "chart_data": {
                "labels": [f"Month {i+1}" for i in range(timeframe)],
                "values": [possible_monthly_saving * (i+1) for i in range(timeframe)]
            }
        }

    # If possible, ask Gemini for a plan
    prompt = f"""
        You are 'SAVI', the friendly money buddy in the Neural Budget AI app.
        Use warm, practical, and encouraging language.

        RULES:
        - Do not exceed ₹{possible_monthly_saving} in total monthly savings.
        - Each tip must be realistic for India.
        - Total savings from tips should be close to ₹{possible_monthly_saving}.
        - Tailor suggestions for the goal: "{data.get('goal_name')}".
        - Provide chart data for {timeframe} months (cumulative savings).

        USER DATA:
        - Monthly Income: ₹{income}
        - Monthly Expenses: ₹{expenses}
        - Goal Name: {data.get('goal_name')}
        - Goal Amount: ₹{goal_amount}
        - Timeframe: {timeframe} months
        - Risk Profile: {data.get('risk')}
        - Saving Style: {data.get('saving_style')}

        Output valid JSON only:
        {{
            "title": string,
            "summary": string,
            "monthly_savings_target": {possible_monthly_saving},
            "plan_steps": [
                {{
                    "step_number": int,
                    "icon": string,
                    "title": string,
                    "description": string,
                    "potential_savings": "₹amount/month"
                }}
            ],
            "chart_data": {{
                "labels": ["Month 1", "Month 2", ...],
                "values": [numbers]
            }}
        }}
    """

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    response = model.generate_content(prompt)

    plan_json_text = response.text.strip().replace("```json", "").replace("```", "")
    plan_data = json.loads(plan_json_text)

    return plan_data


# Smart Categorization

def generate_smart_categorization(user_id):
    """
    Fetches all user expenses and uses the Gemini API to generate a
    hierarchical spending analysis.
    """
    # 1. Fetch all expense transactions from Firestore
    all_expenses = get_transactions(user_id, 'expenses', limit=500)

    if not all_expenses:
        return {"error": "No transactions found to analyze."}

    # --- THIS IS THE FIX ---
    # 2. Convert any datetime objects into JSON-serializable strings
    for transaction in all_expenses:
        if 'date' in transaction and isinstance(transaction['date'], datetime):
            # Convert the datetime object to a standard ISO 8601 string format
            transaction['date'] = transaction['date'].isoformat()
    # --- END OF FIX ---

    # 3. Construct a detailed prompt for the Gemini API
    prompt = f"""
    You are an expert financial analyst for the "Neural Budget AI" app. Your task is to perform a detailed, hierarchical analysis of a user's spending.

    Analyze the following list of transactions. For each transaction, first determine a general spending category (e.g., "Food & Dining", "Subscriptions & OTT", "Shopping", "Transport"). Then, within each category, identify specific merchants or sub-types (e.g., "Netflix", "Zomato", "Uber") by looking at the transaction name.

    Your final output must be a single, valid JSON object with one key: "analysis_results".
    The value of "analysis_results" should be an array of objects, where each object represents a main category.

    Each main category object must have these keys:
    - "category_name": The general category name (e.g., "Subscriptions & OTT").
    - "icon": A relevant Font Awesome icon class (e.g., "fas fa-rss-square").
    - "total_spend": The sum of all spending in this category.
    - "breakdown": An array of sub-category objects.

    Each sub-category object in the "breakdown" array must have these keys:
    - "name": The specific merchant or sub-type (e.g., "Netflix").
    - "transaction_count": The number of transactions for this specific merchant.
    - "amount": The total amount spent on this specific merchant.

    Here is the user's transaction data:
    {json.dumps(all_expenses, indent=2)}
    """

    # 4. Call the Gemini API and parse the response
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(prompt)
        
        result_text = response.text.strip().replace("```json", "").replace("```", "")
        analysis_data = json.loads(result_text)
        
        return analysis_data
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return {"error": "The AI is currently busy and could not analyze your spending. Please try again later."}
