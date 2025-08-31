from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
import json
from apps.ml_features.services.chatbot_service import get_chatbot_response

# Import AI functions
from AI.categorization.run_ocr import get_ocr_text
from AI.categorization.structured_output import process_transaction_text
from apps.common_utils.firebase_service import add_transaction

@csrf_exempt
def categorize_expense_view(request):
    if request.method == 'POST':
        if not request.FILES:
            return JsonResponse({'error': 'No image uploaded.'}, status=400)

        if len(request.FILES.getlist('image')) > 1:
            return JsonResponse({'error': 'Please upload only one image at a time.'}, status=400)
        
        uploaded_image = request.FILES.get('image')
        if not uploaded_image:
            return JsonResponse({'error': 'Invalid image field.'}, status=400)

        user_id = request.session.get('user_id') # Get user ID from session

        # Create a temporary directory if it doesn't exist
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        os.makedirs(temp_dir, exist_ok=True)

        temp_image_path = os.path.join(temp_dir, uploaded_image.name)
        with open(temp_image_path, 'wb+') as destination:
            for chunk in uploaded_image.chunks():
                destination.write(chunk)

        try:
            ocr_text = get_ocr_text(temp_image_path)
            
            # If OCR text is empty, return a standard error
            if not ocr_text.strip():
                return JsonResponse({'error': 'Could not extract text from the image. Please upload a clear image of a transaction.'}, status=400)

            transaction_data = process_transaction_text(ocr_text, user_id)

            # The transaction is added by the frontend after this view returns.
            # add_transaction(user_id, transaction_data, 'transactions')

            return JsonResponse({'message': 'Image processed successfully', 'transaction': transaction_data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            # Clean up the temporary image
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def chatbot_response_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message')
            user_id = request.session.get('user_id')

            if not user_message:
                return JsonResponse({"error": "No message provided"}, status=400)

            response_message = get_chatbot_response(user_id, user_message)
            return JsonResponse({"response": response_message})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
