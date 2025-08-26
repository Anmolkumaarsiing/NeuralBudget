from django.shortcuts import render
from django.http import JsonResponse
from apps.common_utils.auth_utils import get_email, get_user_id
from . import services

def predictive_analysis_page(request):
    """Renders the Predictive Analysis page and provides data."""
    user_id = get_user_id(request)
    email = get_email(request)
    visualizations_data = services.generate_predictive_analysis(user_id)
    context = {'email': email, 'visualizations': visualizations_data}
    return render(request, 'insights/predictive_analysis.html', context)

def smart_categorization_page(request):
    """Renders the Smart Categorization page."""
    email = get_email(request)
    return render(request, 'insights/smart_categorization.html', {'email': email})

def get_smart_analysis_api(request):
    """API endpoint that returns the AI-generated spending analysis."""
    user_id = get_user_id(request)
    analysis_data = services.generate_smart_categorization(user_id)
    if "error" in analysis_data:
        return JsonResponse(analysis_data, status=400)
    return JsonResponse(analysis_data)