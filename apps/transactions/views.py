from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from apps.common_utils.auth_utils import get_user_id, get_email, is_authenticated
from apps.transactions.services import submit_transaction_util, delete_income_util, get_incomes_util, add_category_util
from apps.common_utils.firebase_service import get_user_categories

def submit_transaction(request):
    if not is_authenticated(request):
        return redirect('accounts:login')
    
    if request.method == "GET":
        email = get_email(request)
        user_id = get_user_id(request)
        categories = get_user_categories(user_id)
        print(f"[DEBUG] Categories passed to add_transaction.html: {categories}")
        return render(request, 'transactions/add_transaction.html', {"email": email, "categories": categories})
    if request.method == "POST":
        return submit_transaction_util(request)

    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def delete_income(request):
    if request.method == "DELETE":
        return delete_income_util(request)

    return JsonResponse({"error": "Method not allowed"}, status=405)


def income_tracker(request):
    if not is_authenticated(request):
        return redirect('accounts:login')
    email = get_email(request)
    return render(request, 'transactions/income_tracker.html', {"email": email})

@csrf_exempt
def get_incomes(request):
    if not is_authenticated(request):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    return get_incomes_util(request)

@csrf_exempt
def add_category(request):
    if not is_authenticated(request):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    if request.method == "POST":
        user_id = get_user_id(request)
        data = json.loads(request.body)
        category_name = data.get("category_name")
        if not category_name:
            return JsonResponse({"error": "Category name is required"}, status=400)
        return add_category_util(user_id, category_name)
    return JsonResponse({"error": "Method not allowed"}, status=405)
