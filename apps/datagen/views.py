import json
from django.shortcuts import render
from django.http import JsonResponse
from apps.common_utils.auth_utils import get_email, get_user_id
# Make sure get_user_profile is imported
from apps.common_utils.firebase_service import get_user_profile
from . import services

def data_generator_page(request):
    """Renders the data generator tool page."""
    # --- FIX: Fetch user profile to get the name ---
    user_id = get_user_id(request)
    user_profile = get_user_profile(user_id)
    user_name = user_profile.get('display_name') if user_profile else get_email(request)
    
    return render(request, 'datagen/data_generator.html', {'user_name': user_name})

def generate_data_api(request):
    """API endpoint to handle the data generation request."""
    if request.method == 'POST':
        try:
            user_id = get_user_id(request)
            data = json.loads(request.body)
            num_transactions = int(data.get('num_transactions', 10))

            if not 1 <= num_transactions <= 100:
                return JsonResponse({'error': 'Please enter a number between 1 and 100.'}, status=400)

            added_count = services.add_generated_data_to_user(user_id, num_transactions)
            
            return JsonResponse({'message': f'Successfully generated and added {added_count} new transactions to your account!'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def delete_data_page(request):
    """Renders the data deletion tool page."""
    # --- FIX: Fetch user profile to get the name ---
    user_id = get_user_id(request)
    user_profile = get_user_profile(user_id)
    user_name = user_profile.get('display_name') if user_profile else get_email(request)

    return render(request, 'datagen/delete_data.html', {'user_name': user_name})

def delete_data_api(request):
    """API endpoint to handle the data deletion request."""
    if request.method == 'POST':
        try:
            user_id = get_user_id(request)
            deleted_count = services.delete_all_user_transactions(user_id)
            return JsonResponse({'message': f'Successfully deleted {deleted_count} transaction records.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def admin_overview_page(request):
    """Renders the main admin overview page."""
    user_id = get_user_id(request)
    user_profile = get_user_profile(user_id)
    user_name = user_profile.get('display_name') if user_profile else get_email(request)
    
    context = {
        'user_name': user_name
    }
    return render(request, 'datagen/overview.html', context)

def get_admin_analytics_api(request):
    """API endpoint that provides analytics data to the frontend."""
    if request.method == 'GET':
        try:
            analytics_data = services.get_admin_dashboard_analytics()
            return JsonResponse(analytics_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def historical_data_page(request):
    """Renders the historical data generator tool page."""
    email = get_email(request)
    return render(request, 'datagen/historical_data_generator.html', {'email': email})

def generate_historical_data_api(request):
    """API endpoint to handle the historical data generation request."""
    if request.method == 'POST':
        try:
            user_id = get_user_id(request)
            data = json.loads(request.body)
            
            # Add validation for the new inputs
            constraints = {
                "start_date": data.get("start_date"),
                "end_date": data.get("end_date"),
                "district": data.get("district"),
                "min_amount": int(data.get("min_amount", 10)),
                "max_amount": int(data.get("max_amount", 1000)),
                "num_transactions": int(data.get("num_transactions", 10))
            }

            added_count = services.generate_historical_data(user_id, constraints)
            return JsonResponse({'message': f'Successfully generated and added {added_count} historical transactions!'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)