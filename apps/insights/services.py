
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
    all_expenses = get_transactions(user_id, 'expenses', limit=2000)
    if not all_expenses:
        return {"error": "No transaction data found to generate an analysis."}

    # 2. Filter for last 6 months
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
    all_expenses = get_transactions(user_id, 'expenses', limit=500)
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



def generate_spending_insights(user_id):
    """
    Fetches expenses for the current month and uses the Gemini API to generate
    a day-wise breakdown and a summary of the top 5 spending categories.
    """
    # 1. Fetch all expense transactions from Firestore for the user
    all_expenses = get_transactions(user_id, 'expenses', limit=1000)
    if not all_expenses:
        return {"error": "No transaction data found to generate insights."}

    # 2. Filter for transactions in the current month
    now = datetime.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    current_month_expenses = [
        t for t in all_expenses
        if isinstance(t.get('date'), datetime) and t['date'].replace(tzinfo=None) >= start_of_month
    ]

    if not current_month_expenses:
        return {"error": "No transactions found for the current month."}

    # 3. Pre-process data for the prompt
    for transaction in current_month_expenses:
        if 'date' in transaction and isinstance(transaction['date'], datetime):
            transaction['date'] = transaction['date'].isoformat()

    # 4. Construct a detailed prompt for the Gemini API
    prompt = f"""
    You are "SAVI", an insightful financial analyst for the "Neural Budget AI" app. Your task is to analyze a user's spending for the current month.

    Your final output must be a single, valid JSON object with two keys: "daily_breakdown" and "top_categories".

    1.  For "daily_breakdown":
        - Group all transactions by their date.
        - For each date, provide a summary, the total amount spent, and a relevant Font Awesome icon.
        - The value should be an array of objects, sorted from most recent date to oldest. Each object must have the keys: "date" (YYYY-MM-DD), "day_summary" (e.g., "Mainly spent on food delivery"), "total_spent", and "icon" (e.g., "fas fa-utensils").

    2.  For "top_categories":
        - Identify the top 5 spending categories for the month.
        - The value should be an object with two keys: "labels" (an array of the top 5 category names) and "values" (an array of the total spending for each of those categories).

    Here is the user's transaction data for the current month:
    {json.dumps(current_month_expenses, indent=2)}
    """

    # 5. Call the Gemini API and parse the response
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(prompt)
        
        result_text = response.text.strip().replace("```json", "").replace("```", "")
        insights_data = json.loads(result_text)
        
        return insights_data
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return {"error": "The AI could not generate your insights. Please try again later."}
