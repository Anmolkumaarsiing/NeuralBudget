from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from apps.common_utils.firebase_config import FIREBASE_API_KEY
from apps.common_utils.auth_utils import get_user_id, get_email, is_authenticated, get_user_full_name
from apps.common_utils.firebase_service import get_user_profile
from apps.reports.services import get_dashboard_data, generate_visualizations_data

def dashboard_view(request):
    if not is_authenticated(request):
        print("[DEBUG] dashboard_view: User not authenticated, redirecting to login.")
        return redirect('accounts:login')
    
    user_id = get_user_id(request)
    email = get_email(request)
    user_profile = get_user_profile(user_id)
    full_name = get_user_full_name(user_profile)

    dashboard_data = get_dashboard_data(request)
    context = {
        "email": email,
        "full_name": full_name, # Added full_name to context
        "FIREBASE_API_KEY": FIREBASE_API_KEY,
        "total_expenses": dashboard_data['total_expenses'],
        "total_income":dashboard_data['total_income'],
        "savings": dashboard_data['savings'],
        "budget_left": dashboard_data['budget_left'],
        "recent_transactions": dashboard_data['recent_transactions'],
        "expense_chart_data": dashboard_data['expense_chart_data'],
    }
    return render(request, 'reports/dashboard.html', context)

@csrf_exempt
def visualize(request):
    if not is_authenticated(request):
        return redirect('accounts:login')
    email = get_email(request)
    user_id = get_user_id(request)
    
    visualizations = generate_visualizations_data(user_id)
    
    data = {'email':email,'visualizations':visualizations}

    # Render the visualize.html template with visualizations
    return render(request, "reports/visualize.html",data) 
