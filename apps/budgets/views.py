# in apps/budgets/views.py

import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse

from apps.common_utils.auth_utils import get_email, get_user_id
from . import services

# --- Budgeting Tools Views (These can remain as they are) ---

def set_budget(request):
    # ... your existing set_budget code ...
    return render(request, "budgets/set_budget.html")

def get_budgets(request):
    # ... your existing get_budgets code ...
    return JsonResponse({})


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