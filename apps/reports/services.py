from django.http import JsonResponse
from apps.common_utils.firebase_service import get_transactions
from apps.common_utils.auth_utils import get_user_id
from apps.ml_features.services import preprocess_data, predict_future_income, categorize_spending, generate_visualizations

collection_name = 'expense'

def get_dashboard_data(request):
    user_id = get_user_id(request)
    if not user_id:
        print("[DEBUG] get_dashboard_data: User ID is missing from session.")
        return {
            "total_expenses": 0,
            "savings": 0,
            "budget_left": 0,
            "recent_transactions": [],
            "expense_chart_data": {'labels': [], 'data': []}
        }

    try:
        # Fetch all transactions for the user (or a reasonable limit for dashboard)
        # Assuming 'transaction' collection holds all income/expense records
        transactions = get_transactions(user_id, collection_name, limit=1000)
        print(f"[DEBUG] Fetched {len(transactions)} transactions for user {user_id}")

        total_expenses = 0
        total_income = 0
        recent_transactions = []
        expense_categories = {}

        for transaction_doc in transactions:
            try:
                # Access the nested 'transaction' dictionary
                transaction = transaction_doc.get('transaction', {})

                amount = float(transaction.get('amount', 0))
                category = transaction.get('category', 'Uncategorized')
                name = transaction.get('name', 'N/A')
                date = transaction.get('date', 'N/A')

                # Infer transaction type based on category
                income_categories = ['Salary', 'Freelancing', 'Business', 'Investments']
                transaction_type = 'income' if category in income_categories else 'expense'



                if transaction_type.lower() == 'expense':
                    total_expenses += amount
                    expense_categories[category] = expense_categories.get(category, 0) + amount
                elif transaction_type.lower() == 'income':
                    total_income += amount
                
                # Collect recent transactions (e.g., last 5)
                recent_transactions.append({
                    'name': name,
                    'amount': amount,
                    'type': transaction_type,
                    'date': date
                })
            except ValueError as ve:
                print(f"[ERROR] Skipping transaction with invalid amount or data: {transaction_doc.id} - {ve}")
                continue
            except Exception as inner_e:
                print(f"[ERROR] Unexpected error processing transaction {transaction_doc.id}: {inner_e}")
                continue
        
        # Sort recent transactions by date (newest first)
        recent_transactions.sort(key=lambda x: x.get('date', ''), reverse=True)
        recent_transactions = recent_transactions[:5] # Get only the 5 most recent

        # Placeholder for budget data (needs to be implemented if budgets are stored)
        budget_set = 10000 # Example budget
        budget_left = budget_set - total_expenses # Simple calculation

        # Prepare data for chart
        chart_data = {
            'labels': list(expense_categories.keys()),
            'data': list(expense_categories.values())
        }
        print(f"[DEBUG] Dashboard Data: Total Expenses: {total_expenses}, Total Income: {total_income}, Savings: {total_income - total_expenses}, Budget Left: {budget_left}")

        return {
            'total_expenses': total_expenses,
            'total_income': total_income,
            'savings': total_income - total_expenses, # Simple savings calculation
            'budget_left': budget_left,
            'recent_transactions': recent_transactions,
            'expense_chart_data': chart_data
        }
    except Exception as e:
        print(f"[ERROR] Error in get_dashboard_data: {e}")
        # Return default empty data on error to prevent redirect loop
        return {
            "total_expenses": 0,
            "savings": 0,
            "budget_left": 0,
            "recent_transactions": [],
            "expense_chart_data": {'labels': [], 'data': []}
        }

def generate_visualizations_data(user_id):
    incomes = get_transactions(user_id, 'transaction', 100)
    df = preprocess_data(incomes)
    future_income = predict_future_income(df)
    df = categorize_spending(df)
    visualizations = generate_visualizations(df, future_income)
    return visualizations
