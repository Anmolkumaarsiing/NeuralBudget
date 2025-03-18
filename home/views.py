from django.shortcuts import render, redirect
from django.contrib.auth import logout
from firebase_admin import auth
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from firebase_admin import exceptions as firebase_exceptions
import json,requests
from home.firebase_config import FIREBASE_API_KEY, db
from home.utils.python.help import verify_token, get_user_id,get_email
from home.utils.python.firebase_service import add_transaction, get_transactions
from home.utils.python.ml_util import preprocess_data, predict_future_income, categorize_spending, generate_visualizations

FIREBASE_SIGN_IN_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
collection = 'incomes'

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
        print("in view login")
        return render(request, 'home/login.html')
    elif request.method == 'POST':
        try:
            body = json.loads(request.body)
            email = body.get('email')
            password = body.get('password')

            if not email or not password:
                return JsonResponse({'error': 'Email and password are required'}, status=400)

            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            params = {"key": FIREBASE_API_KEY}
            response = requests.post(FIREBASE_SIGN_IN_URL, json=payload, params=params)
            response_data = response.json()

            if response.status_code != 200:
                error_message = response_data.get("error", {}).get("message", "Authentication failed")
                return JsonResponse({'error': error_message}, status=401)

            id_token = response_data.get("idToken")
            if not id_token:
                return JsonResponse({'error': 'Failed to retrieve ID token'}, status=401)

            try:
                decoded_token = verify_token(id_token)
                uid = decoded_token['uid']

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
            request.session['user_id'] = uid
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
    try:    
        email = get_email(request)
        print(email)
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
        email = get_email(request)
        return render(request, 'home/add_transaction.html', {"email": email})
    if request.method == "POST":
        try:
            # Parse JSON data from the request
            data = json.loads(request.body)
            user_id = data.get("id")  # Get user ID from session
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
            income_ref = db.collection(collection).document(income_id)
            income_ref.delete()
            return JsonResponse({"message": "Income deleted successfully"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)

def income_tracker(request):
    if not is_authenticated(request):
        return redirect('home:login')
    email = get_email(request)
    return render(request, 'home/income_tracker.html', {"email": email})

@csrf_exempt
def get_incomes(request):
    if not is_authenticated(request):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    user_id = request.session.get("user_id")
    if not user_id:
        return JsonResponse({"error": "User ID is missing"}, status=400)
    itemCount = int(request.GET.get("itemCount"))
    # print(type(itemsPerPage),type(page))
    try:
        incomes = get_transactions(user_id,itemCount,collection)
        return JsonResponse({"incomes": incomes}, safe=False)
    except Exception as e:
        print(e)
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def visualize(request):
    if not is_authenticated(request):
        return redirect('home:login')
    email = get_email(request)
    user_id = get_user_id(request)
    # Fetch income data from Firestore
    incomes = get_transactions(user_id,100,collection)

    df = preprocess_data(incomes)
    # print(df)

    # # Run ML models
    future_income = predict_future_income(df)
    df = categorize_spending(df)
    visualizations = generate_visualizations(df, future_income)
    data = {'email':email,'visualizations':visualizations}

    # Render the visualize.html template with visualizations
    return render(request, "home/visualize.html",data) 