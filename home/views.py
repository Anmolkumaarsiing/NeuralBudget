from django.shortcuts import render, redirect
from django.contrib.auth import logout
from firebase_admin import auth
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from firebase_admin import exceptions as firebase_exceptions
import json,requests
from home.firebase_config import FIREBASE_API_KEY, db
from home.utils.python.help import verify_token, get_user_id
from home.utils.python.firebase_service import add_transaction, get_transactions

FIREBASE_SIGN_IN_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"


def is_authenticated(request):
    if request.session.get('id_token'):
        return True
    return False

def home(request):
    return render(request, 'home/index.html')

@csrf_exempt
def login_view(request):
    if is_authenticated(request):
        return redirect('home:dashboard')
    elif request.method == 'GET':
        return render(request, 'home/login.html')
    elif request.method == 'POST':
        try:
            # Parse the request body
            body = json.loads(request.body)
            email = body.get('email')
            password = body.get('password')
            print("Email:", email)
            print("Password:", password)

            # Validate email and password
            if not email or not password:
                return JsonResponse({'error': 'Email and password are required'}, status=400)

            # Authenticate with Firebase REST API
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            params = {"key": FIREBASE_API_KEY}
            response = requests.post(FIREBASE_SIGN_IN_URL, json=payload, params=params)
            response_data = response.json()
            print("Firebase response:", response_data)

            # Handle Firebase authentication errors
            if response.status_code != 200:
                error_message = response_data.get("error", {}).get("message", "Authentication failed")
                return JsonResponse({'error': error_message}, status=401)

            # Extract the Firebase ID token
            id_token = response_data.get("idToken")
            if not id_token:
                return JsonResponse({'error': 'Failed to retrieve ID token'}, status=401)

            # Verify the ID token using Firebase Admin SDK
            try:
                decoded_token = verify_token(id_token)
                uid = decoded_token['uid']
                print("Decoded token UID:", uid)

                # Store user information in the session
                request.session['user_id'] = uid
                request.session['email'] = email
                request.session['id_token'] = id_token

                # Return success response
                return JsonResponse({
                    'message': 'Login successful',
                    'email': email,
                    'uid': uid,
                })

            except firebase_exceptions.FirebaseError as e:
                return JsonResponse({'error': f'Firebase error: {str(e)}'}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            print("Unexpected error:", str(e))  # Log unexpected errors
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

    # Return method not allowed for non-POST requests
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def register_view(request):
    if is_authenticated(request):
        return render(request, 'home/dashboard.html')

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")

            user = auth.create_user(
                email=email,
                password=password,
                display_name=username
            )
            uid = user.display_name
            

            # Optionally, you can generate a custom token for the user
            custom_token = auth.create_custom_token(uid)

            # Store user information in session (optional)
            request.session['uid'] = uid
            request.session['email'] = email
            request.session['username'] = username

            return JsonResponse({
                "message": "Registration successful",
                "uid": uid,
                "redirect_url": "/dashboard/"
            })

        except auth.EmailAlreadyExistsError:
            return JsonResponse({"error": "Email already exists"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)

def dashboard_view(request):
    if not is_authenticated(request):
        print("User is not authenticated")
        return redirect('home:login')
    
    id_token = request.session.get('id_token')
    try:    
        email = get_user_id(id_token)
        return render(request, 'home/dashboard.html', {"email": email})
    except Exception:
        return redirect('/login/')  # Redirect if token is invalid

@csrf_exempt
def logout_view(request):
    if request.method == "POST":
        try:
            # Clear Firebase session
            if 'id_token' in request.session:
                del request.session['id_token']
            if 'user_id' in request.session:
                del request.session['user_id']
            if 'email' in request.session:
                del request.session['email']
            
            # Django logout
            logout(request)
            request.session.flush()
            
            return JsonResponse({
                "message": "Logged out successfully",
                "redirect_url": "/home/login/"
            })
        except Exception as e:
            return JsonResponse({
                "error": str(e)
            }, status=400)
    
    return JsonResponse({
        "error": "Method not allowed"
    }, status=405)
from django.http import JsonResponse


@csrf_exempt
def submit_transaction(request):
    if not is_authenticated(request):
        return redirect('home:login')
    if request.method == "GET":
        email = get_user_id(request.session.get('id_token'))
        return render(request, 'home/add_transaction.html', {"email": email})
    if request.method == "POST":
        try:
            # Parse JSON data from the request
            data = json.loads(request.body)
            user_id = data.get("id")  # Get user ID from session
            print(user_id)
            if not user_id:
                return JsonResponse({"error": "User not authenticated"}, status=401)

            # Add transaction to Firestore
            add_transaction(user_id, data)
            return JsonResponse({"message": "Transaction added successfully"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def delete_income(request):
    """Delete an income transaction."""
    if request.method == "DELETE":
        try:
            income_id = request.GET.get("income_id")  # Get income ID from query params

            if not income_id:
                return JsonResponse({"error": "Income ID is required"}, status=400)

            # Delete the income from Firestore
            income_ref = db.collection("transactions").document(income_id)
            income_ref.delete()

            return JsonResponse({"message": "Income deleted successfully"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)

def income_tracker(request):
    if not is_authenticated(request):
        return redirect('home:login')
    email = get_user_id(request.session.get('id_token'))
    return render(request, 'home/income_tracker.html', {"email": email})

@csrf_exempt
def get_incomes(request):
    if not is_authenticated(request):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    user_id = request.session.get("user_id")
    print(user_id)
    if not user_id:
        return JsonResponse({"error": "User ID is missing"}, status=400)

    try:
        incomes = get_transactions(user_id)
        print(incomes)
        return JsonResponse({"incomes": incomes}, safe=False)
    except Exception as e:
        print(e)
        return JsonResponse({"error": str(e)}, status=500)