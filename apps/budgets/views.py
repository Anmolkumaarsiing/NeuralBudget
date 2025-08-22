# in apps/budgets/views.py

import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse

from apps.common_utils.auth_utils import get_email, get_user_id
from apps.budgets.services import get_categories, set_budget as set_budget_service, get_budgets as get_budgets_service
from . import services
from datetime import datetime
from apps.common_utils.firebase_service import get_transactions

def set_budget(request):
    email = get_email(request)
    user_id = get_user_id(request)

    if request.method == "POST":
        budget = request.POST.get("budget")
        category = request.POST.get("category")
        period = request.POST.get("period") # Get the period
        set_budget_service(user_id, category, budget, period) # Pass period to service
        messages.success(request, f"Budget of {budget} for {category} ({period}) set successfully!")
        return redirect("budgets:set_budget")
    
    user_budgets = get_budgets_service(user_id) # Fetch all budgets
    user_expenses = get_transactions(user_id, 'expenses') # Fetch all expenses
    user_available_categories = get_categories(user_id) # Fetch user's available categories

    # Define a mapping for category display names and emojis
    category_display_map = {
        'groceries': '🛒 Groceries',
        'transportation': '🚗 Transportation',
        'shopping & personal care': '🛍️ Shopping & Personal Care',
        'entertainment & dining': '🎬 Entertainment & Dining',
        'utilities': '💡 Utilities',
        'healthcare': '🏥 Healthcare',
        'education & self-development': '📚 Education & Self-Development',
        'travel': '✈️ Travel',
        'savings & investments': '💰 Savings & Investments',
        'debt payments': '💳 Debt Payments',
        'housing': '🏠 Housing',
        'other': '📝 Other',
        'uncategorized': '❓ Uncategorized', # For categories without a specific emoji
    }

    # Prepare categories for the dropdown, ensuring emojis are maintained
    user_available_categories_for_dropdown = []
    for cat_name in user_available_categories:
        display_name = category_display_map.get(cat_name.lower(), f'📝 {cat_name.replace('_', ' ').title()}')
        user_available_categories_for_dropdown.append({'value': cat_name, 'display': display_name})

    total_budget = 0
    total_spent = 0
    budget_data_map = {}

    # Process budgets
    for b in user_budgets:
        cat_name = b.get('category')
        amount = float(b.get('budget', 0))
        period = b.get('period', 'monthly') # Default to monthly if not set

        total_budget += amount
        budget_data_map[cat_name] = {
            'name': cat_name,
            'budget_amount': amount,
            'spent_amount': 0,
            'period': period,
            'icon': '', # Will be set later
            'display_name': cat_name # Will be set later
        }

    # Process expenses
    for e in user_expenses:
        cat_name = e.get('category')
        amount = float(e.get('amount', 0))
        total_spent += amount

        if cat_name in budget_data_map:
            budget_data_map[cat_name]['spent_amount'] += amount

    # Calculate remaining and percentage for each category
    processed_categories = []
    for cat_name_raw, data in budget_data_map.items():
        # Ensure cat_name is a string, default to 'uncategorized' if None
        cat_name = cat_name_raw if cat_name_raw is not None else 'uncategorized'

        budget_amount = data['budget_amount']
        spent_amount = data['spent_amount']

        remaining = budget_amount - spent_amount
        progress_percentage = (spent_amount / budget_amount * 100) if budget_amount > 0 else 0

        # Assign icon and display name (simple mapping for now, can be expanded)
        category_icons = {
            'food': 'fas fa-utensils',
            'transport': 'fas fa-bus',
            'shopping': 'fas fa-shopping-bag',
            'entertainment': 'fas fa-film',
            'bills': 'fas fa-lightbulb',
            'healthcare': 'fas fa-heartbeat',
            'education': 'fas fa-graduation-cap',
            'travel': 'fas fa-plane',
            'savings': 'fas fa-piggy-bank',
            'other': 'fas fa-question-circle',
            'uncategorized': 'fas fa-question-circle', # Add icon for uncategorized
        }
        data['icon'] = category_icons.get(cat_name.lower(), 'fas fa-question-circle')
        data['display_name'] = category_display_map.get(cat_name.lower(), cat_name.replace('_', ' ').title()) # Use display map for consistency

        data['remaining'] = remaining
        data['progress_percentage'] = min(100, round(progress_percentage, 2)) # Cap at 100%
        processed_categories.append(data)

    total_remaining = total_budget - total_spent
    # If no budget is set (total_budget is 0), then remaining should also be 0
    if total_budget == 0:
        total_remaining = 0

    print(f"[DEBUG] Final total_budget: {total_budget}")
    print(f"[DEBUG] Final total_spent: {total_spent}")
    print(f"[DEBUG] Final total_remaining: {total_remaining}")
    print(f"[DEBUG] Final processed_categories: {processed_categories}")

    context = {
        "email": email,
        "categories": processed_categories, # Pass processed data for budget display
        "user_available_categories": user_available_categories_for_dropdown, # Pass for dropdown
        "total_budget": total_budget,
        "total_spent": total_spent,
        "total_remaining": total_remaining,
    }
    return render(request, "budgets/set_budget.html", context)

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