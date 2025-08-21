import json
from django.shortcuts import render
from django.http import JsonResponse
from apps.common_utils.auth_utils import get_email, get_user_id
from . import services

def data_generator_page(request):
    """Renders the data generator tool page."""
    email = get_email(request)
    return render(request, 'datagen/data_generator.html', {'email': email})

def generate_data_api(request):
    """API endpoint to handle the data generation request."""
    if request.method == 'POST':
        try:
            user_id = get_user_id(request)
            data = json.loads(request.body)
            num_transactions = int(data.get('num_transactions', 10))

            if not 1 <= num_transactions <= 100: # Limit requests to 100
                return JsonResponse({'error': 'Please enter a number between 1 and 100.'}, status=400)

            added_count = services.add_generated_data_to_user(user_id, num_transactions)
            
            return JsonResponse({'message': f'Successfully generated and added {added_count} new transactions to your account!'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)