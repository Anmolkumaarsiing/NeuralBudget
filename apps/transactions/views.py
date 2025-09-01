from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from apps.common_utils.auth_utils import get_user_id, get_email
from apps.transactions.services import submit_transaction_util, delete_transaction_util, get_transactions_history_util, add_category_util
from apps.common_utils.firebase_service import get_user_categories

# @csrf_exempt
def submit_transaction(request):
    if request.method == "GET":
        email = get_email(request)
        user_id = get_user_id(request)
        categories = get_user_categories(user_id)

        return render(request, 'transactions/add_transaction.html', {"email": email, "categories": categories})
    if request.method == "POST":
        return submit_transaction_util(request)

    return JsonResponse({"error": "Method not allowed"}, status=405)

# @csrf_exempt
def delete_transaction(request):
    if request.method == "DELETE":
        return delete_transaction_util(request)

    return JsonResponse({"error": "Method not allowed"}, status=405)

def transaction_history(request):
    email = get_email(request)
    user_id = get_user_id(request)
    categories = get_user_categories(user_id)
    return render(request, 'transactions/transaction_history.html', {"email": email, "categories": categories})


def get_transactions_history(request):
    return get_transactions_history_util(request)

def add_category(request):
    if request.method == "POST":
        user_id = get_user_id(request)
        data = json.loads(request.body)
        category_name = data.get("category_name")
        if not category_name:
            return JsonResponse({"error": "Category name is required"}, status=400)
        return add_category_util(user_id, category_name)
    return JsonResponse({"error": "Method not allowed"}, status=405)
