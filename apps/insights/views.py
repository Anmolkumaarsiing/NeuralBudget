from django.shortcuts import render
from django.http import JsonResponse
import json
from apps.common_utils.auth_utils import get_email, get_user_id
from apps.common_utils.firebase_service import get_user_profile
from . import services


def predictive_analysis_page(request):
    """Renders the Predictive Analysis page and provides data."""
    user_id = get_user_id(request)
    visualizations_data = services.generate_predictive_analysis(user_id)
    context = {"visualizations": visualizations_data}
    return render(request, "insights/predictive_analysis.html", context)


def smart_categorization_page(request):
    """Renders the Smart Categorization page."""
    email = get_email(request)
    user_name = email.split("@")[0] if email else "User"
    return render(request, "insights/smart_categorization.html", {"user_name": user_name})


def get_smart_analysis_api(request):
    """API endpoint that returns the AI-generated spending analysis."""
    user_id = get_user_id(request)
    analysis_data = services.generate_smart_categorization(user_id)
    if "error" in analysis_data:
        return JsonResponse(analysis_data, status=400)
    return JsonResponse(analysis_data)


def spending_insights_page(request):
    """
    Renders the Spending Insights page instantly with a loading state.
    """
    return render(request, "insights/spending_insights.html")

def investment_guide_page(request):
    """
    Renders the Investment Guide page. It checks if the user has a salary set
    and passes the initial state to the template.
    """
    user_id = get_user_id(request)
    user_profile = get_user_profile(user_id)
    
    # Check if salary is already saved in the user's profile
    current_salary = user_profile.get('monthly_salary') if user_profile else None
    
    context = {
        'current_salary': current_salary
    }
    return render(request, 'insights/investment_guide.html', context)

def generate_investment_tips_api(request):
    """
    API endpoint that saves the user's salary and returns AI-generated tips.
    """
    if request.method == "POST":
        try:
            user_id = get_user_id(request)
            data = json.loads(request.body)
            salary = data.get('salary')
            location = data.get('location')

            if not salary or not location:
                return JsonResponse({"error": "Salary and location are required."}, status=400)
            
            # Save the salary to the user's profile for future use
            services.update_user_salary(user_id, salary)
            
            # Generate the investment tips
            tips_data = services.generate_investment_guide(user_id, location, salary)
            
            if "error" in tips_data:
                return JsonResponse(tips_data, status=400)
            return JsonResponse(tips_data)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)


def get_city_api(request):
    """
    API to resolve lat/lon into a city name (server-side to avoid OSM 403).
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            lat = data.get("lat")
            lon = data.get("lon")
            if not lat or not lon:
                return JsonResponse({"error": "Latitude and longitude required"}, status=400)
            city = services.get_city_from_coordinates(lat, lon)
            return JsonResponse({"city": city})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid method"}, status=405)


def get_spending_insights_api(request):
    """
    API endpoint that returns the AI-generated spending insights.
    """
    user_id = get_user_id(request)
    insights_data = services.generate_spending_insights(user_id)
    if "error" in insights_data:
        return JsonResponse(insights_data, status=400)
    return JsonResponse(insights_data)
