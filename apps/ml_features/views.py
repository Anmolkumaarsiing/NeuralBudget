from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
import json

# Import AI functions
from AI.categorization.run_ocr import get_ocr_text
from AI.categorization.structured_output import process_transaction_text
from apps.common_utils.firebase_service import add_transaction

@csrf_exempt
def categorize_expense_view(request):
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_image = request.FILES['image']
        user_id = request.session.get('user_id') # Get user ID from session

        if not user_id:
            return JsonResponse({"error": "User not authenticated"}, status=401)

        # Create a temporary directory if it doesn't exist
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        os.makedirs(temp_dir, exist_ok=True)

        temp_image_path = os.path.join(temp_dir, uploaded_image.name)
        with open(temp_image_path, 'wb+') as destination:
            for chunk in uploaded_image.chunks():
                destination.write(chunk)

        try:
            ocr_text = get_ocr_text(temp_image_path)
            transaction_data = process_transaction_text(ocr_text, user_id)

            add_transaction(user_id, transaction_data, 'transactions')

            return JsonResponse({'message': 'Image processed successfully', 'transaction': transaction_data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            # Clean up the temporary image
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
    return JsonResponse({'error': 'Invalid request'}, status=400)