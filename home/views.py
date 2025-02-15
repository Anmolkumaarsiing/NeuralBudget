from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from firebase_admin import auth
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from firebase_admin import exceptions as firebase_exceptions
import json,requests
from .firebase_config import FIREBASE_API_KEY
from home.utils.python.help import verify_token

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
            print("Register view called")  # Debug line

            # Parse JSON data from the request
            data = json.loads(request.body)
            print("Request data:", data)  # Debug line

            username = data.get("username")
            email = data.get("email")
            password = data.get("password")

            # Create user in Firebase
            print("Creating user in Firebase...")  # Debug line
            user = auth.create_user(
                email=email,
                password=password,
                display_name=username
            )
            uid = user.display_name
            print("User created in Firebase! UID:", uid)  # Debug line

            # Optionally, you can generate a custom token for the user
            custom_token = auth.create_custom_token(uid)
            print("Custom token generated:", custom_token)  # Debug line

            # Store user information in session (optional)
            request.session['uid'] = uid
            request.session['email'] = email
            request.session['username'] = username

            print("Registration successful, redirecting to dashboard")  # Debug line
            return JsonResponse({
                "message": "Registration successful",
                "uid": uid,
                "redirect_url": "/dashboard/"
            })

        except auth.EmailAlreadyExistsError:
            print("Email already exists error")  # Debug line
            return JsonResponse({"error": "Email already exists"}, status=400)
        except Exception as e:
            print("Unexpected error:", str(e))  # Debug line
            return JsonResponse({"error": str(e)}, status=500)
    

    print("Method not allowed")  # Debug line
    return JsonResponse({"error": "Method not allowed"}, status=405)

def dashboard_view(request):
    if not is_authenticated(request):
        print("User is not authenticated")
        return redirect('home:login')
    
    id_token = request.session.get('id_token')
    try:    
        decoded_token = verify_token(id_token)
        user = auth.get_user_by_email(decoded_token.get('email'))
        context = {
        "email": decoded_token.get('email'),
        'uid': user.display_name # Replace with actual DB query
    }
        return render(request, 'home/dashboard.html', context)
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




def add_transaction(request):
    if not request.session.get('id_token'):
        return redirect('home:login')
    
    if request.method == "POST":
        name = request.POST.get('name')
        category = request.POST.get('category')
        other_category = request.POST.get('other_category', '')  # Get other category if provided
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        status = request.POST.get('status')

        # Use "Other" category input if it's provided
        if category == "Other" and other_category:
            category = other_category

        # Save transaction to database
        Transaction.objects.create(
            name=name,
            category=category,
            amount=amount,
            date=date,
            status=status
        )

        return redirect('dashboard')  # Redirect to dashboard after adding transaction

    return render(request, 'home/add_transaction.html')

def income_tracker(request):
    if not request.session.get('id_token'):
        return redirect('home:login')
    
    incomes = [
        {"source": "Gift", "amount": "200.00", "date": "Feb. 15, 2024", "status": "Received"},
        {"source": "Investments", "amount": "800.00", "date": "Feb. 10, 2024", "status": "Received"},
        {"source": "Freelancing", "amount": "1200.00", "date": "Feb. 5, 2024", "status": "Pending"},
        {"source": "Salary", "amount": "5000.00", "date": "Feb. 1, 2024", "status": "Received"},
        {"source": "Stock Trading", "amount": "1500.00", "date": "Jan. 28, 2024", "status": "Completed"},
        {"source": "Rental Income", "amount": "900.00", "date": "Jan. 25, 2024", "status": "Failed"},
        {"source": "Side Business", "amount": "2200.00", "date": "Jan. 20, 2024", "status": "Cancelled"},
        {"source": "Dividends", "amount": "300.00", "date": "Jan. 15, 2024", "status": "Partially Paid"},
        {"source": "Bonus", "amount": "2500.00", "date": "Jan. 10, 2024", "status": "Due"},
    ]
    return render(request, "home/income_tracker.html", {"incomes": incomes})