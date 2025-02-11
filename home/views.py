from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from firebase_admin import auth
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

def home(request):
    return render(request, 'home/index.html')

@csrf_exempt  # Temporarily disable CSRF for testing
def login_view(request):
    
    if request.method == 'POST':
        try:
            # Get the authorization header
            auth_header = request.headers.get('Authorization')
            print(f"Auth header")  # Debug log
            
            if not auth_header:
                return JsonResponse({'error': 'No authorization header'}, status=401)
            
            # Extract the token
            token = auth_header.split('Bearer ')[1]
            print(f"Token: {token}")  # Debug log
            # Get request body
            body = json.loads(request.body)
            email = body.get('email')
            
            try:
                # Verify the Firebase token
                decoded_token = auth.verify_id_token(token)
                uid = decoded_token['uid']
                
                # Store in session
                request.session['user_id'] = uid
                request.session['email'] = email
                request.session['id_token'] = token
                
                return JsonResponse({
                    'message': 'Login successful',
                    'email': email,
                    'uid': uid
                })
                
            except Exception as e:
                print(f"Token verification error: {str(e)}")  # Debug log
                return JsonResponse({'error': f'Token verification failed: {str(e)}'}, status=401)
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")  # Debug log
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")  # Debug log
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'home/login.html')

@csrf_exempt
def register_view(request):
    if request.session.get('id_token'):
        return redirect('home:dashboard')
    
    if request.method == 'POST':
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return JsonResponse({"error": "No authorization header"}, status=401)
            
            id_token = auth_header.split('Bearer ')[1]
            
            # Verify the token
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            
            # Store both token and decoded token in session
            request.session['id_token'] = id_token
            request.session['uid'] = uid
            
            return JsonResponse({
                "message": "Registration successful",
                "redirect_url": "/home/dashboard/"
            })
            
        except Exception as e:
            print(f"Registration error: {str(e)}")
            return JsonResponse({"error": str(e)}, status=400)
    
    return render(request, 'home/register.html')

def dashboard_view(request):
    id_token = request.session.get('id_token')

    if not id_token:
        print("No ID token found in session")
        return redirect('/login/')  # Redirect to login if not authenticated

    try:    
        decoded_token = auth.verify_id_token(id_token)
        return render(request, 'pages/dash.html', {'email': decoded_token.get('email')})
    except Exception:
        return redirect('/login/')  # Redirect if token is invalid


@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        request.session.flush()
        return JsonResponse({"message": "Logged out successfully"})
    return JsonResponse({"error": "Method not allowed"}, status=405)