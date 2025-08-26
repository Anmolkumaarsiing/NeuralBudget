# in apps/budgets/services.py

import json,logging
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
    Generate a warm, budget-aware 'Smart Saver' plan using Gemini, JSON output ONLY.
    Impossible goals are rejected with a helpful message, and Gemini JSON is fully validated.
    """
    logger = logging.getLogger("savi.plan")

    # --- INPUT VALIDATION ---
    try:
        income = float(data.get('income', 0))
        expenses = float(data.get('expenses', 0))
        goal_amount = float(data.get('goal_amount', 0))
        timeframe = int(data.get('timeframe', 0))
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid numeric input: {e}")
        return {"title": "Invalid Input ❌",
                "summary": "Income, expenses, goal amount, and timeframe must be numbers.",
                "monthly_savings_target": 0,
                "plan_steps": [],
                "chart_data": {"labels": [], "values": []}
        }

    # Extra edge case guards
    if any(n < 0 for n in [income, expenses, goal_amount, timeframe]) or timeframe == 0 or income == 0:
        logger.warning("Zero or negative value in inputs")
        return {"title": "Invalid Input ❌",
                "summary": "All numbers must be positive and timeframe cannot be zero. Please correct and try again.",
                "monthly_savings_target": 0,
                "plan_steps": [],
                "chart_data": {"labels": [], "values": []}
        }

    possible_monthly_saving = max(0, income - expenses)
    total_possible_saving = possible_monthly_saving * timeframe

    if possible_monthly_saving <= 0 or total_possible_saving < goal_amount:
        alt_timeframe = (goal_amount // possible_monthly_saving + 1) if possible_monthly_saving > 0 else None
        alt_msg = (f"To reach ₹{goal_amount}, try a plan of about {int(alt_timeframe)} months." if alt_timeframe else "")
        summary = (f"Your income is ₹{income} and expenses are ₹{expenses}. "
                   f"You can save only ₹{possible_monthly_saving} per month. "
                   f"In {timeframe} months, you can save ₹{total_possible_saving}, which is less than your goal (₹{goal_amount}). "
                   f"{alt_msg}")
        return {
            "title": "Goal Not Possible 😔",
            "summary": summary.strip(),
            "monthly_savings_target": possible_monthly_saving,
            "plan_steps": [],
            "chart_data": {
                "labels": [f"Month {i+1}" for i in range(timeframe)],
                "values": [possible_monthly_saving * (i+1) for i in range(timeframe)]
            }
        }

    # --- PROMPT ENGINEERING ---
    prompt = (
        f"You are 'SAVI', a financial wellness buddy for Indians. "
        f"Generate a clear, actionable savings plan for this user to reach '{data.get('goal_name')}'."
        "\nRULES:"
        f"\n- DO NOT EXCEED ₹{possible_monthly_saving} monthly savings."
        "\n- Give realistic, India-focused tips (no generic or western examples)."
        "\n- If you cannot suggest any realistic plan, return ONLY this: {{'error': 'Goal impossible'}}."
        "\n- Plan as JSON with keys: title, summary (<=2 sentences), monthly_savings_target, plan_steps, chart_data."
        f"\n- Goal: ₹{goal_amount} in {timeframe} months (Income: ₹{income}, Expenses: ₹{expenses}). Tailor tips to '{data.get('goal_name')}'."
        "\n- Each step: step_number, icon, title, description, potential_savings."
        f"\n- chart_data: {{'labels':['Month 1',...], 'values':[cumulative_savings]}} for {timeframe} months."
        "\n--- Begin JSON ---"
    )

    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(prompt)
        logger.info("GenAI called successfully for plan")

        plan_json_text = response.text.strip().lstrip("``````").strip()
        plan_data = json.loads(plan_json_text)

        # Output validation
        expected_keys = {"title", "summary", "monthly_savings_target", "plan_steps", "chart_data"}
        if not isinstance(plan_data, dict) or not expected_keys.issubset(plan_data.keys()):
            logger.warning("AI responded, but output is missing fields. Output: %s", plan_data)
            raise ValueError("Model output missing fields")

        return plan_data
    except Exception as err:
        logger.exception(f"Error from Gemini or output validation: {err}")
        return {
            "title": "Error 🛑",
            "summary": "Couldn't generate a savings plan due to an internal error. Please try again soon.",
            "monthly_savings_target": possible_monthly_saving,
            "plan_steps": [],
            "chart_data": {
                "labels": [f"Month {i+1}" for i in range(timeframe)],
                "values": [possible_monthly_saving * (i+1) for i in range(timeframe)]
            }
        }


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
