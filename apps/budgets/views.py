from django.shortcuts import render, redirect
from django.contrib import messages
from apps.common_utils.auth_utils import get_email, get_user_id
from apps.budgets.services import get_categories, set_budget as set_budget_service, get_budgets as get_budgets_service
from django.http import JsonResponse

def set_budget(request):
    email=get_email(request)
    user_id = get_user_id(request)
    categories = get_categories(user_id)
    if request.method == "POST":
        budget = request.POST.get("budget")
        category = request.POST.get("category")
        set_budget_service(user_id, category, budget)
        messages.success(request, f"Budget of {budget} for {category} set successfully!")
        return redirect("budgets:set_budget")
    return render(request, "budgets/set_Budget.html", {"email": email, "categories": categories})

def get_budgets(request):
    user_id = get_user_id(request)
    budgets = get_budgets_service(user_id)
    return JsonResponse({"budgets": budgets})
