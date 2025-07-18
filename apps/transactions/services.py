from django.http import JsonResponse
from apps.common_utils.firebase_service import add_transaction, get_transactions, delete_transaction, add_category as add_category_to_firebase
from apps.transactions.schemas import IncomeSchema, TransactionSchema
import json
from datetime import datetime

collection = 'transactions'

def submit_transaction_util(request):
    try:
        data = json.loads(request.body)
        user_id = data.get("id")
        transaction_data = data.get("transaction")

        if not user_id:
            return JsonResponse({"error": "User not authenticated"}, status=401)
        
        if not transaction_data:
            return JsonResponse({"error": "Invalid transaction data"}, status=400)

        # Use the appropriate schema based on the transaction type
        if 'name' in transaction_data: # It's a transaction
            transaction = TransactionSchema(
                name=transaction_data['name'],
                category=transaction_data['category'],
                amount=float(transaction_data['amount']),
                date=datetime.strptime(transaction_data['date'], '%Y-%m-%d'),
                status=transaction_data['status'],
                user_id=user_id
            )
            add_transaction(user_id, transaction.to_dict(), collection)
        elif 'source' in transaction_data: # It's an income
            income = IncomeSchema(
                source=transaction_data['source'],
                amount=float(transaction_data['amount']),
                date=datetime.strptime(transaction_data['date'], '%Y-%m-%d'),
                status=transaction_data['status'],
                user_id=user_id
            )
            add_transaction(user_id, income.to_dict(), 'incomes') # Use a separate collection for incomes
        else:
            return JsonResponse({"error": "Invalid transaction data"}, status=400)

        return JsonResponse({"message": "Transaction submitted successfully"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def delete_income_util(request):
    try:
        income_id = request.GET.get("income_id")
        if not income_id:
            return JsonResponse({"error": "Income ID is required"}, status=400)
        delete_transaction(income_id, 'incomes') # Use the 'incomes' collection
        return JsonResponse({"message": "Income deleted successfully"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def get_incomes_util(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return JsonResponse({"error": "User ID is missing"}, status=400)
    item_count = int(request.GET.get("itemCount"))
    last_doc_id = request.GET.get("lastDocId")
    try:
        incomes = get_transactions(user_id, 'incomes', item_count, last_doc_id) # Use the 'incomes' collection
        return JsonResponse({"incomes": incomes}, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def add_category_util(user_id, category_name):
    try:
        add_category_to_firebase(user_id, category_name)
        return JsonResponse({"message": "Category added successfully"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
