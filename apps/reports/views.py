from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from apps.common_utils.firebase_config import FIREBASE_API_KEY
from apps.common_utils.auth_utils import get_user_id, get_email, get_user_full_name
from apps.common_utils.firebase_service import get_user_profile
from apps.reports.services import get_dashboard_data, generate_visualizations_data

def dashboard_view(request):
    dashboard_data = get_dashboard_data(request)
    context = {
        "FIREBASE_API_KEY": FIREBASE_API_KEY,
        "total_expenses": dashboard_data['total_expenses'],
        "total_income":dashboard_data['total_income'],
        "savings": dashboard_data['savings'],
        "recent_transactions": dashboard_data['recent_transactions'],
    }
    return render(request, 'reports/dashboard.html', context)

@csrf_exempt
def visualize(request):
    email = get_email(request)
    user_id = get_user_id(request)
    
    visualizations = generate_visualizations_data(user_id)
    
    data = {'email':email,'visualizations':visualizations}

    # Render the visualize.html template with visualizations
    return render(request, "reports/visualize.html",data)