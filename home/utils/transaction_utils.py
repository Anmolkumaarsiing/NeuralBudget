from django.http import JsonResponse
from home.utils.firebase_service import add_transaction, get_transactions, delete_transaction
from django.shortcuts import render
import json

collection = 'transactions'

def submit_transaction_util(request):
    try:
        data = json.loads(request.body)
        user_id = data.get("id")
        if not user_id:
            return JsonResponse({"error": "User not authenticated"}, status=401)
        add_transaction(user_id, data, collection)
        return JsonResponse({"message": "Transaction added successfully"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def delete_income_util(request):
    try:
        income_id = request.GET.get("income_id")
        if not income_id:
            return JsonResponse({"error": "Income ID is required"}, status=400)
        delete_transaction(income_id, collection)
        return JsonResponse({"message": "Income deleted successfully"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def get_incomes_util(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return JsonResponse({"error": "User ID is missing"}, status=400)
    item_count = int(request.GET.get("itemCount"))
    last_doc_id = request.GET.get("lastDocId")
    print(f"get_incomes_util: itemCount={item_count}, lastDocId={last_doc_id}")
    try:
        incomes = get_transactions(user_id, collection, item_count, last_doc_id)
        return JsonResponse({"incomes": incomes}, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
