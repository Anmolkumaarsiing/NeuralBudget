# in apps/budgets/services.py

import json
import google.generativeai as genai
from django.conf import settings
from apps.common_utils.firebase_service import get_user_categories, add_transaction, get_transactions

# --- Service functions for Budgeting ---

def get_categories(user_id):
    return get_user_categories(user_id)

def set_budget(user_id, category, budget):
    add_transaction(user_id, {"category": category, "budget": budget}, "budgets")

def get_budgets(user_id):
    return get_transactions(user_id, "budgets")

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


