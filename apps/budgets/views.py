# in apps/budgets/views.py

import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse

from apps.common_utils.auth_utils import get_email, get_user_id
from apps.budgets.services import get_categories, set_budget as set_budget_service, get_budgets as get_budgets_service
from . import services



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
    return render(request, "budgets/set_budget.html", {"email": email, "categories": categories})

def get_budgets(request):
    user_id = get_user_id(request)
    budgets = get_budgets_service(user_id)
    return JsonResponse({"budgets": budgets})


# --- Smart Saver AI Planner View (Stateless) ---

def smart_saver(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # Call the service, which will now be stateless
            plan_data = services.create_smart_saver_plan(data)
            return JsonResponse(plan_data)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    # For GET requests, just render the page
    email = get_email(request)
    return render(request, "budgets/Smart_saver.html", {"email": email})


# Add these two new views to your budgets/views.py file

def smart_categorization(request):
    """Renders the main page for the Smart Categorization feature."""
    email = get_email(request)
    return render(request, 'budgets/smart_categorization.html', {'email': email})

def get_smart_analysis_data(request):
    """API endpoint that returns the AI-generated spending analysis."""
    if request.method == "GET":
        user_id = get_user_id(request)
        analysis_data = services.generate_smart_categorization(user_id)
        if "error" in analysis_data:
            return JsonResponse(analysis_data, status=400)
        return JsonResponse(analysis_data)
    return JsonResponse({"error": "Invalid request method"}, status=405)