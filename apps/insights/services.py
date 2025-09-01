
import json
from datetime import datetime, timedelta
import statistics
import google.generativeai as genai
from django.conf import settings
from apps.common_utils.firebase_service import get_transactions


def generate_predictive_analysis(user_id):
    """
    Fetches user expenses and uses Gemini to generate a smarter spending forecast.
    - Prioritizes the last 6 months (180 days) of data for trend detection.
    - Falls back to all-time data if recent transactions are insufficient.
    - Prepares structured aggregates (monthly + category) before passing to Gemini.
    """

    # 1. Fetch transactions
    all_expenses = get_transactions(user_id, 'expenses')
    if not all_expenses:
        return {"error": "No transaction data found to generate an analysis."}

    six_months_ago = datetime.now() - timedelta(days=180)
    recent_expenses = [
        tx for tx in all_expenses
        if isinstance(tx.get('date'), datetime) and tx['date'].replace(tzinfo=None) > six_months_ago
    ]

    # 3. Fallback to all data if too few recent transactions
    if len(recent_expenses) < 30:  # less than 30 transactions in 6 months = too sparse
        print("Recent data is insufficient. Falling back to all available data.")
        analysis_data_source = all_expenses
    else:
        analysis_data_source = recent_expenses

    # 4. Preprocess transactions
    monthly_totals = {}
    category_totals = {}
    cleaned_transactions = []

    for tx in analysis_data_source:
        amount = float(tx.get("amount", 0))
        date_obj = tx.get("date")

        if isinstance(date_obj, datetime):
            tx["date"] = date_obj.isoformat()
            month_key = date_obj.strftime("%Y-%m")
        else:
            month_key = "unknown"

        # Monthly aggregation
        monthly_totals[month_key] = monthly_totals.get(month_key, 0) + amount

        # Category aggregation
        category = tx.get("category", "Uncategorized")
        category_totals[category] = category_totals.get(category, 0) + amount

        cleaned_transactions.append(tx)

    # Compute average + recent trend for prompt guidance
    monthly_values = list(monthly_totals.values())
    avg_monthly_spend = round(statistics.mean(monthly_values), 2) if monthly_values else 0
    last_month_spend = round(monthly_values[-1], 2) if monthly_values else 0
    spend_trend = "increasing" if last_month_spend > avg_monthly_spend else "decreasing"

    # 5. Construct enriched prompt
    prompt = f"""
    You are a financial data analyst for "Neural Budget AI".
    Analyze the user's spending patterns and provide a predictive analysis.

    Your output must be a single, valid JSON object with two keys: "forecast_chart" and "category_chart".

    1. "forecast_chart":
       - Predict the spending for the next 30 days using trends from the last 6 months.
       - Base your forecast on patterns in monthly totals and recent spending.
       - Provide:
         {{
           "labels": ["Average Monthly Spend", "Last Month Spend", "Next 30 Days (Forecast)"],
           "values": [<number>, <number>, <number>]
         }}

       Context:
       - Average Monthly Spend = {avg_monthly_spend}
       - Last Month Spend = {last_month_spend}
       - Trend direction = {spend_trend}

    2. "category_chart":
       - Group transactions by category and provide the total spend per category.
       - Provide:
         {{
           "labels": [<category1>, <category2>, ...],
           "values": [<amount1>, <amount2>, ...]
         }}

    Transaction Data (for deeper insights):
    {json.dumps(cleaned_transactions, indent=2)}

    Monthly Aggregates:
    {json.dumps(monthly_totals, indent=2)}

    Category Aggregates:
    {json.dumps(category_totals, indent=2)}
    """

    # 6. Call Gemini API
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(prompt)

        result_text = response.text.strip().replace("```json", "").replace("```", "")
        analysis_data = json.loads(result_text)

        return analysis_data
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return {"error": "The AI could not generate your analysis. Please try again later."}


def generate_smart_categorization(user_id):
    """
    Fetches expenses and uses Gemini to generate a hierarchical spending analysis.
    """
    all_expenses = get_transactions(user_id, 'expenses')
    if not all_expenses:
        return {"error": "No transactions found to analyze."}

    for transaction in all_expenses:
        if 'date' in transaction and isinstance(transaction['date'], datetime):
            transaction['date'] = transaction['date'].isoformat()

    prompt = f"""
    You are an expert financial analyst for "Neural Budget AI".
    Perform a detailed, hierarchical analysis of the user's spending.

    For each transaction, determine:
    - A general category (e.g., "Food & Dining", "Subscriptions & OTT")
    - Specific merchants or sub-types (e.g., "Netflix", "Zomato")

    Output a valid JSON object:
    {{
      "analysis_results": [
        {{
          "category": "<Main Category>",
          "icon": "<FontAwesome Icon>",
          "breakdown": [
            {{
              "sub_category": "<Merchant/Sub-Type>",
              "transaction_count": <int>,
              "amount": <float>
            }},
            ...
          ]
        }},
        ...
      ]
    }}

    Here is the user's transaction data:
    {json.dumps(all_expenses, indent=2)}
    """
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(prompt)
        result_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(result_text)
    except Exception as e:
        return {"error": f"AI analysis failed: {e}"}


def update_user_salary(user_id, salary):
    """Saves or updates the monthly salary in the user's Firestore profile."""
    # Ensure salary is a number before saving
    try:
        salary_float = float(salary)
    except (ValueError, TypeError):
        raise ValueError("Invalid salary format. Please provide a number.")
        
    user_profile_ref = db.collection('user_profiles').document(user_id)
    user_profile_ref.set({'monthly_salary': salary_float}, merge=True)

def generate_investment_guide(user_id, location, salary):
    """
    Analyzes user's savings and location to generate investment tips via Gemini API.
    """
    print("--- 1. Starting Investment Guide Generation ---")
    
    thirty_days_ago = datetime.now() - timedelta(days=30)
    all_expenses = get_transactions(user_id, 'expenses', limit=1000)
    
    recent_expenses = [
        t for t in all_expenses
        if isinstance(t.get('date'), datetime) and t['date'].replace(tzinfo=None) > thirty_days_ago
    ]
    
    total_monthly_expenses = sum(t.get('amount', 0) for t in recent_expenses)
    print(f"--- 2. Calculated last 30 days expenses: ₹{total_monthly_expenses:.2f} ---")

    monthly_savings = float(salary) - total_monthly_expenses
    print(f"--- 3. Calculated monthly savings: ₹{monthly_savings:.2f} (Salary: ₹{salary}) ---")

    if monthly_savings <= 100:
        return {"error": "Your monthly savings are too low to generate investment tips. Focus on budgeting first."}

    prompt = f"""
     You are "SAVI", an expert financial advisor for the "Neural Budget AI" app, specializing in investment advice for beginners in India.
    Your task is to create a personalized investment guide for a user. The advice must be practical, easy to understand, and relevant to their location.
    **User's Financial Profile:**
    - Location: {location}, India
    - Calculated Monthly Savings: ₹{monthly_savings:.2f}
    **Your Output:**
    Generate a valid JSON object with a single key: "investment_tips".
    The value must be an array of 3 to 4 objects, each with the keys: "title", "icon", "description", "action_step", and "risk_level".
    The tips should be suitable for a beginner with the calculated monthly savings. Prioritize safer, long-term options.
    """


    # 4. Call the Gemini API and return the response
    try:
        print("--- 4. Sending prompt to Gemini API... ---")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(prompt)
        
        print("--- 5. Received response from Gemini. Parsing JSON... ---")
        result_text = response.text.strip().replace("```json", "").replace("```", "")
        parsed_response = json.loads(result_text)
        print("--- 6. JSON parsed successfully. Sending tips to user. ---")
        return parsed_response

    except Exception as e:
        print(f"--- CRITICAL ERROR during Gemini API call: {e} ---")
        return {"error": f"The AI could not generate investment tips. Details: {e}"}
import requests

def get_city_from_coordinates(lat, lon):
    """
    Fetch city/town/village/state from OpenStreetMap Nominatim API.
    Falls back to state if city is unavailable.
    """
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "format": "json",
        "lat": lat,
        "lon": lon
    }
    headers = {
        "User-Agent": "NeuralBudgetAI/1.0 (anmolkumaarsiingh2@gmail.com)"  # Required by OSM
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        address = data.get("address", {})
        
        # Try city, town, village, then state
        return (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("state")
            or "Unknown"
        )
    except Exception:
        return "Unknown"
