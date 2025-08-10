from django.shortcuts import render
import json
import google.generativeai as genai
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

def home(request):
    return render(request, 'core/index.html')

@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_msg = data.get("message", "")

            if not user_msg:
                return JsonResponse({"error": "No message provided"}, status=400)

            # Call Gemini
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(
                f"Give me financial suggestions for: {user_msg}"
            )

            # Extract reply safely
            reply = ""
            if hasattr(response, "text"):
                reply = response.text
            elif hasattr(response, "candidates"):
                reply = response.candidates[0].content.parts[0].text

            return JsonResponse({"reply": reply})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
