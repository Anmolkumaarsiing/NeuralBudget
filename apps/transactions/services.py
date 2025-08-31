from django.http import JsonResponse
from apps.common_utils.firebase_service import (
    add_transaction,
    get_transactions,
    delete_transaction,
    add_category as add_category_to_firebase
)
from apps.transactions.schemas import IncomeSchema, ExpenseSchema
import json
from datetime import datetime
from dateutil import parser
import logging
from django.utils.timezone import make_naive
import pytz

# Constants
INCOME_COLLECTION = 'incomes'
EXPENSE_COLLECTION = 'expenses'
MAX_ITEMS_PER_REQUEST = 100
DEFAULT_ITEMS_PER_REQUEST = 10

logger = logging.getLogger(__name__)

def _validate_transaction_data(transaction_data):
    """Validate common transaction fields."""
    if not transaction_data:
        return False, "Invalid transaction data"
    if 'amount' not in transaction_data:
        return False, "Amount is required"
    try:
        amount = float(transaction_data['amount'])
        if amount <= 0:
            return False, "Amount must be positive"
    except (ValueError, TypeError):
        return False, "Invalid amount format"
    return True, ""

def submit_transaction_util(request):
    """Handle transaction submission with improved validation."""
    try:
        data = json.loads(request.body)
        user_id = data.get("id") or request.session.get("user_id")
        transaction_data = data.get("transaction")

        if not user_id:
            return JsonResponse({"error": "User not authenticated"}, status=401)
        
        valid, message = _validate_transaction_data(transaction_data)
        if not valid:
            return JsonResponse({"error": message}, status=400)

        try:
            if 'source' in transaction_data:  # Income
                income = IncomeSchema(
                    source=transaction_data['source'],
                    amount=float(transaction_data['amount']),
                    date=parser.parse(transaction_data['date']),
                    status=transaction_data.get('status', 'pending')
                )
                add_transaction(user_id, income.to_dict(), INCOME_COLLECTION)
            elif 'name' in transaction_data and 'category' in transaction_data:  # Expense
                expense = ExpenseSchema(
                    name=transaction_data['name'],
                    category=transaction_data['category'],
                    amount=float(transaction_data['amount']),
                    date=parser.parse(transaction_data['date']),
                    status=transaction_data.get('status', 'pending')
                )
                add_transaction(user_id, expense.to_dict(), EXPENSE_COLLECTION)
            else:
                return JsonResponse({"error": "Invalid transaction type"}, status=400)

            logger.info(f"Transaction added for user {user_id}")
            return JsonResponse({"message": "Transaction submitted successfully"})

        except Exception as e:
            logger.error(f"Transaction submission failed: {str(e)}")
            return JsonResponse({"error": "Invalid transaction data"}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in submit_transaction: {str(e)}")
        return JsonResponse({"error": "Internal server error"}, status=500)

def delete_transaction_util(request):
    """Handle transaction deletion with validation."""
    try:
        transaction_id = request.GET.get("transaction_id")
        collection_name = request.GET.get("collection")
        user_id = request.session.get("user_id")

        if not all([transaction_id, collection_name, user_id]):
            return JsonResponse(
                {"error": "Transaction ID, collection and user ID are required"},
                status=400
            )

        if collection_name not in [INCOME_COLLECTION, EXPENSE_COLLECTION]:
            return JsonResponse({"error": "Invalid collection name"}, status=400)

        delete_transaction(transaction_id, collection_name, user_id)
        logger.info(f"Transaction {transaction_id} deleted from {collection_name}")
        return JsonResponse({"message": "Transaction deleted successfully"})

    except Exception as e:
        logger.error(f"Transaction deletion failed: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

def get_transactions_history_util(request):
    """Retrieve, filter, and sort transactions with pagination."""
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({"error": "User not authenticated"}, status=401)

        item_count = min(
            int(request.GET.get("itemCount", DEFAULT_ITEMS_PER_REQUEST)),
            MAX_ITEMS_PER_REQUEST
        )
        page = int(request.GET.get("page", 1))
        sort_by = request.GET.get("sortBy", "date")
        sort_order = request.GET.get("sortOrder", "desc")
        category_filter = request.GET.get("category")

        incomes = get_transactions(user_id, INCOME_COLLECTION) or []
        expenses = get_transactions(user_id, EXPENSE_COLLECTION) or []

        if category_filter and category_filter != "all":
            expenses = [t for t in expenses if t.get("category") == category_filter]
            incomes = [] # Do not show income when filtering by expense category

        for transaction in incomes + expenses:
            transaction['type'] = 'Income' if 'source' in transaction else 'Expense'
            date_value = transaction.get('date')
            
            if isinstance(date_value, datetime):
                if date_value.tzinfo is not None:
                    transaction['date_for_sort'] = make_naive(date_value, pytz.UTC)
                else:
                    transaction['date_for_sort'] = date_value
            else:
                transaction['date_for_sort'] = datetime.min

        reverse_order = sort_order == "desc"
        
        def sort_key(x):
            if sort_by == 'amount':
                return x.get('amount', 0)
            return x.get('date_for_sort', datetime.min)

        all_transactions = sorted(incomes + expenses, key=sort_key, reverse=reverse_order)

        start_index = (page - 1) * item_count
        end_index = start_index + item_count
        paginated_transactions = all_transactions[start_index:end_index]

        return JsonResponse({"transactions": paginated_transactions}, safe=False)

    except Exception as e:
        logger.error(f"Failed to get transactions: {str(e)}")
        return JsonResponse({"error": "Failed to retrieve transactions"}, status=500)

def add_category_util(request):
    """Handle category addition with validation."""
    try:
        data = json.loads(request.body)
        user_id = data.get("id") or request.session.get("user_id")
        category_name = data.get("category_name")

        if not user_id:
            return JsonResponse({"error": "User not authenticated"}, status=401)
        if not category_name or not isinstance(category_name, str):
            return JsonResponse({"error": "Invalid category name"}, status=400)

        add_category_to_firebase(user_id, category_name.strip())
        logger.info(f"Category {category_name} added for user {user_id}")
        return JsonResponse({"message": "Category added successfully"})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        logger.error(f"Category addition failed: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)