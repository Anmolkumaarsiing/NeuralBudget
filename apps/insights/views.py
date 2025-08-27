from django.shortcuts import render
from django.http import JsonResponse
from apps.common_utils.auth_utils import get_email, get_user_id
from . import services


def predictive_analysis_page(request):
    """Renders the Predictive Analysis page and provides data."""
    user_id = get_user_id(request)
    email = get_email(request)
    user_name = email.split("@")[0] if email else "User"

    visualizations_data = services.generate_predictive_analysis(user_id)
    context = {"user_name": user_name, "visualizations": visualizations_data}
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


# in apps/insights/views.py

from django.shortcuts import render
from django.http import JsonResponse
from apps.common_utils.auth_utils import get_email, get_user_id
from . import services


def spending_insights_page(request):
    """
    Renders the Spending Insights page instantly with a loading state.
    """
    email = get_email(request)
    user_name = email.split("@")[0] if email else "User"
    return render(request, "insights/spending_insights.html", {"user_name": user_name})


def get_spending_insights_api(request):
    """
    API endpoint that handles the slow task of calling the Gemini API.
    """
    if request.method == "GET":
        try:
            user_id = get_user_id(request)
            insights_data = services.generate_spending_insights(user_id)
            if "error" in insights_data:
                return JsonResponse(insights_data, status=400)
            return JsonResponse(insights_data)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)
