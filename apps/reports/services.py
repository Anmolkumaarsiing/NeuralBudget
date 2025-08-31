from django.http import JsonResponse
from apps.common_utils.firebase_service import get_transactions
from apps.common_utils.auth_utils import get_user_id
from apps.budgets.services import get_budgets
from datetime import datetime
from dateutil import parser

# Define collection names
EXPENSE_COLLECTION = 'expenses'
INCOME_COLLECTION = 'incomes'
BUDGET_COLLECTION = 'budgets'

def _parse_date(date_input):
    """Safely parse a date which can be a datetime object or a string, and make it naive."""
    if isinstance(date_input, datetime):
        # If the datetime object is timezone-aware, convert it to naive
        if date_input.tzinfo is not None:
            return date_input.replace(tzinfo=None)
        return date_input
    if isinstance(date_input, str):
        try:
            # dateutil.parser.parse might return an aware datetime
            dt = parser.parse(date_input)
            # If it's aware, make it naive
            if dt.tzinfo is not None:
                return dt.replace(tzinfo=None)
            return dt
        except (ValueError, TypeError):
            # Return a default old date if parsing fails
            return datetime.min
    # Return a default old date for other types or None
    return datetime.min

def get_dashboard_data(request):
    user_id = get_user_id(request)
    try:
        # Get current month and year
        now = datetime.now()
        current_month = now.month
        print("[DEBUG] Current Month:", current_month)  # Debugging line
        current_year = now.year

        # Fetch all expenses, incomes, and budgets for the user
        all_expenses = get_transactions(user_id, EXPENSE_COLLECTION)
        all_incomes = get_transactions(user_id, INCOME_COLLECTION)
        # print("[DEBUG] Fetched Expenses:", all_expenses)  # Debugging line


        expenses = [t for t in all_expenses if _parse_date(t.get('date')).month >= current_month-7 and _parse_date(t.get('date')).year == current_year]
        incomes = [t for t in all_incomes if _parse_date(t.get('date')).year == current_year]


        total_expenses = sum(float(transaction.get('amount', 0)) for transaction in expenses)
        total_income = sum(float(transaction.get('amount', 0)) for transaction in incomes)

        
        # Process expenses for category chart (only for current month expenses)
        expense_categories = {}
        for transaction in expenses:
            amount = float(transaction.get('amount', 0))
            category = transaction.get('category', 'Uncategorized')
            expense_categories[category] = expense_categories.get(category, 0) + amount

        # Combine transactions for 'Recent Transactions' list (only for current month transactions)
        all_transactions = []
        for t in expenses:
            t['type'] = 'expense'
            all_transactions.append(t)
            
        # Sort all transactions by parsed date
        all_transactions.sort(key=lambda x: _parse_date(x.get('date')), reverse=True)
        recent_transactions = all_transactions[:5]


        
        savings = total_income - total_expenses

        return {
            'total_expenses': total_expenses,
            'total_income': total_income,
            'savings': savings,
            'recent_transactions': recent_transactions,
        }
    except Exception as e:
        print(f"[ERROR] Error in get_dashboard_data: {e}")
        # Return default empty data on error to prevent redirect loop
        return {
            "total_expenses": 0,
            "total_income": 0,
            "savings": 0,
            "budget_left": 0,
            "recent_transactions": [],
            "expense_chart_data": {'labels': [], 'data': []}
        }

def generate_visualizations_data(user_id):
    # Corrected collection name and fetching both incomes and expenses for a complete picture
    expenses = get_transactions(user_id, EXPENSE_COLLECTION, 100)
    incomes = get_transactions(user_id, INCOME_COLLECTION, 100)
    
    # Note: preprocess_data and subsequent ML functions might need adjustments
    # to handle the combined or separate datasets. This is a starting point.
    df_expenses = preprocess_data(expenses)
    df_incomes = preprocess_data(incomes) # Assuming preprocess_data works for incomes
    
    future_income = predict_future_income(df_incomes)
    df_expenses = categorize_spending(df_expenses)
    
    # Assuming generate_visualizations can take multiple dataframes or needs to be adapted
    visualizations = generate_visualizations(df_expenses, future_income)
    return visualizations


def get_income_data(request):
    user_id = get_user_id(request)
    if not user_id:
        return JsonResponse({"error": "User not authenticated"}, status=401)

    try:
        # Fetch all income transactions for the user
        incomes = get_transactions(user_id, INCOME_COLLECTION, limit=1000)
        
        # Process data for chart
        income_sources = {}
        for income in incomes:
            source = income.get('source', 'Uncategorized')
            amount = float(income.get('amount', 0))
            income_sources[source] = income_sources.get(source, 0) + amount

        chart_data = {
            'labels': list(income_sources.keys()),
            'data': list(income_sources.values())
        }
        
        return JsonResponse(chart_data)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)