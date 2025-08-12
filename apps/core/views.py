from django.shortcuts import render
import json
# import google.generativeai as genai
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings

# Configure Gemini API
# genai.configure(api_key=settings.GEMINI_API_KEY)

def home(request):
    return render(request, 'core/index.html')

def chatbot_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method. Please use POST."}, status=405)

    try:
        data = json.loads(request.body)
        user_msg = data.get("message", "").strip()

        if not user_msg:
            return JsonResponse({"error": "No message provided."}, status=400)

        prompt = (
            "You are a helpful and friendly financial assistant for an app called Neural Budget AI. "
            "Provide clear, safe, and general financial advice. Do not give personalized investment advice. "
            f"The user's query is: {user_msg}"
        )

        # Use the latest, recommended model
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(prompt)
        
        return JsonResponse({"reply": response.text})
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON in request body."}, status=400)
    except Exception as e:
        print(f"An error occurred in chatbot_api: {e}") 
        return JsonResponse({"error": "An internal server error occurred."}, status=500)