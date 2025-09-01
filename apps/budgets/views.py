# in apps/budgets/views.py

import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse

from apps.common_utils.auth_utils import get_user_id
from apps.budgets.services import (
    get_categories,
    set_budget as set_budget_service,
    get_budgets as get_budgets_service,
    delete_budget as delete_budget_service,
    get_budget_analysis,
    CATEGORY_DISPLAY_MAP
)
from . import services

def set_budget(request):
    user_id = get_user_id(request)
    if request.method == "POST":
        budget = request.POST.get("budget")
        category = request.POST.get("category")
        period = request.POST.get("period")
        set_budget_service(user_id, category, budget, period)
        messages.success(
            request,
            f"Budget of {budget} for {category} ({period}) set successfully!",
        )
        return redirect("budgets:set_budget")

    user_available_categories = get_categories(user_id)
    budget_analysis = get_budget_analysis(user_id)

    user_available_categories_for_dropdown = []
    for cat_name in user_available_categories:
        display_name = CATEGORY_DISPLAY_MAP.get(
            cat_name.lower(),
            f"📝 {cat_name.replace('_', ' ').title()}",
        )
        user_available_categories_for_dropdown.append(
            {"value": cat_name, "display": display_name}
        )

    context = {
        "categories": budget_analysis["processed_categories"],
        "user_available_categories": user_available_categories_for_dropdown,
        "total_budget": budget_analysis["total_budget"],
        "total_spent": budget_analysis["total_spent"],
        "total_remaining": budget_analysis["total_remaining"],
    }
    return render(request, "budgets/set_budget.html", context)

def get_budgets(request):
    user_id = get_user_id(request)
    budgets = get_budgets_service(user_id)
    return JsonResponse({"budgets": budgets})

def delete_budget(request):
    if request.method == "DELETE":
        user_id = get_user_id(request)
        data = json.loads(request.body)
        budget_id = data.get("budget_id")
        delete_budget_service(user_id, budget_id)
        return JsonResponse({"message": "Budget deleted successfully"})
    return JsonResponse({"error": "Invalid request method"}, status=405)


# --- Smart Saver AI Planner View (Stateless) ---

def smart_saver(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            plan_data = services.create_smart_saver_plan(data)
            return JsonResponse(plan_data)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

   
    return render(request, "budgets/Smart_saver.html")


# --- Smart Categorization (budgets) ---

def smart_categorization(request):
    return render(request, "budgets/smart_categorization.html")


def get_smart_analysis_data(request):
    """API endpoint that returns the AI-generated spending analysis."""
    if request.method == "GET":
        user_id = get_user_id(request)
        analysis_data = services.generate_smart_categorization(user_id)
        if "error" in analysis_data:
            return JsonResponse(analysis_data, status=400)
        return JsonResponse(analysis_data)
    return JsonResponse({"error": "Invalid request method"}, status=405)
