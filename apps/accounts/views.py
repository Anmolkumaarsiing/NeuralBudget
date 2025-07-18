from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from firebase_admin import exceptions as firebase_exceptions
import json,requests
from apps.common_utils.firebase_config import FIREBASE_API_KEY
from apps.common_utils.auth_utils import get_user_id, get_email
from apps.common_utils.firebase_service import firebase_login, verify_firebase_token, get_user_profile, create_user_profile
from apps.common_utils.auth_utils import is_authenticated
from apps.accounts.services import register_user, logout_user,update_profile_service,upload_profile_picture_service, send_password_reset_email_service

def login_view(request):
    if is_authenticated(request):
        return redirect('reports:dashboard')
    if request.method == 'GET':
        return render(request, 'accounts/login.html', {'FIREBASE_API_KEY': FIREBASE_API_KEY})
    elif request.method == 'POST':
        try:
            body = json.loads(request.body)
            email = body.get('email')
            password = body.get('password')

            if not email or not password:
                return JsonResponse({'error': 'Email and password are required'}, status=400)

            response_data = firebase_login(email, password)
            id_token = response_data.get("idToken")

            if not id_token:
                return JsonResponse({'error': 'Failed to retrieve ID token'}, status=401)

            decoded_token = verify_firebase_token(id_token)
            uid = decoded_token['uid']
            display_name = decoded_token.get('name', email.split('@')[0]) # Get display name from token or default to email prefix

            # Fetch or create user profile
            user_profile = get_user_profile(uid)
            if not user_profile:
                create_user_profile(uid, email, display_name)
                user_profile = get_user_profile(uid) # Fetch again to get the newly created profile
            
            # Use display name from profile if available
            display_name_from_profile = user_profile.get('display_name', display_name)

            request.session['user_id'] = uid
            request.session['email'] = email
            request.session['id_token'] = id_token
            request.session['display_name'] = display_name_from_profile # Store display name in session

            return JsonResponse({
                'message': 'Login successful',
                'email': email,
                'uid': uid,
                'display_name': display_name_from_profile,
                'redirect_url': '/reports/dashboard' # Add redirect URL
            })

        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=401)
        except firebase_exceptions.FirebaseError as e:
            return JsonResponse({'error': f'Firebase error: {str(e)}'}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

def register_view(request):
    if is_authenticated(request):
        return render(request, 'reports/dashboard.html')

    if request.method == "POST":
        data = json.loads(request.body)
        response = register_user(request, data)
        if "error" in response:
            status_code = 400 
            if "Email already exists" in response["error"]:
                status_code = 409
            elif "An unexpected error occurred" in response["error"]:
                status_code = 500
            return JsonResponse(response, status=status_code)
        else:
            return JsonResponse(response, status=201) # 201 Created for successful registration
    
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def logout_view(request):
    if request.method == "POST":
        response = logout_user(request)
        print(response)
        return JsonResponse(response)    
    return JsonResponse({
        "error": "Method not allowed"
    }, status=405)

def profile_view(request):
    if not is_authenticated(request):
        return redirect('accounts:login')
    
    user_id = get_user_id(request)
    user_profile = get_user_profile(user_id)

    context = {
        'email': get_email(request),
        'profile': user_profile
    }
    return render(request, 'accounts/profile.html', context)

@csrf_exempt
def update_profile_view(request):
    if not is_authenticated(request):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    if request.method == "POST":
        user_id = get_user_id(request)
        data = json.loads(request.body)
        response = update_profile_service(user_id, data)
        if "error" in response:
            return JsonResponse(response, status=500)
        return JsonResponse(response)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def refresh_token_view(request):
    """
    Refreshes the Firebase ID token in the Django session.

    This view receives a new Firebase ID token from the client-side.
    It verifies the token with Firebase and, if valid, updates the
    'id_token', 'user_id', and 'email' in the Django session.
    This helps maintain a consistent authenticated state between
    Firebase and the Django backend, especially after the initial
    Firebase ID token expires.
    """
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            id_token = body.get('idToken')

            if not id_token:
                return JsonResponse({'error': 'ID token is required'}, status=400)

            decoded_token = verify_firebase_token(id_token)
            uid = decoded_token['uid']
            email = decoded_token.get('email') # Firebase token might not always have email

            request.session['user_id'] = uid
            request.session['email'] = email
            request.session['id_token'] = id_token

            return JsonResponse({'message': 'Token refreshed successfully'})

        except firebase_exceptions.FirebaseError as e:
            return JsonResponse({'error': f'Firebase token verification failed: {str(e)}'}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def upload_profile_picture_view(request):
    if not is_authenticated(request):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    if request.method == "POST":
        user_id = get_user_id(request)
        if 'profile_picture' not in request.FILES:
            return JsonResponse({"error": "No file provided"}, status=400)
        
        uploaded_file = request.FILES['profile_picture']
        response = upload_profile_picture_service(user_id, uploaded_file)
        
        if "error" in response:
            return JsonResponse(response, status=500)
        return JsonResponse(response)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def send_password_reset_email_view(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            email = body.get('email')
            if not email:
                return JsonResponse({'error': 'Email is required'}, status=400)
            
            response = send_password_reset_email_service(email)
            status_code = response.pop("status", 200) # Get status code, default to 200
            return JsonResponse(response, status=status_code)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)
