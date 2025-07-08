from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from firebase_admin import exceptions as firebase_exceptions
import json,requests
from home.firebase_config import FIREBASE_API_KEY
from home.utils.python.help import get_user_id,get_email
from home.utils.auth import firebase_login, verify_firebase_token, is_authenticated
from home.utils.transaction_utils import submit_transaction_util, delete_income_util, get_incomes_util
from home.utils.dashboard_utils import get_dashboard_data
from home.utils.views_utils import register_user, logout_user
from home.utils.visualization_utils import generate_visualizations_data

def home(request):
    return render(request, 'home/index.html')

def login_view(request):
    if is_authenticated(request):
        return redirect('home:dashboard')
    elif request.method == 'GET':
        return render(request, 'home/login.html', {'FIREBASE_API_KEY': FIREBASE_API_KEY})
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

            request.session['user_id'] = uid
            request.session['email'] = email
            request.session['id_token'] = id_token

            return JsonResponse({
                'message': 'Login successful',
                'email': email,
                'uid': uid,
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
        return render(request, 'home/dashboard.html')

    if request.method == "POST":
        data = json.loads(request.body)
        response = register_user(data)
        return JsonResponse(response)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)

def dashboard_view(request):
    if not is_authenticated(request):
        print("User is not authenticated")
        return redirect('home:login')
    try:    
        email = get_email(request)
        dashboard_data = get_dashboard_data(request)
        context = {
            "email": email,
            "FIREBASE_API_KEY": FIREBASE_API_KEY,
            "total_expenses": dashboard_data['total_expenses'],
            "savings": dashboard_data['savings'],
            "budget_left": dashboard_data['budget_left'],
            "recent_transactions": dashboard_data['recent_transactions'],
            "expense_chart_data": dashboard_data['expense_chart_data'],
        }
        return render(request, 'home/dashboard.html', context)
    except Exception:
        return redirect('/login/')  # Redirect if token is invalid

@csrf_exempt
def logout_view(request):
    if request.method == "POST":
        response = logout_user(request)
        return JsonResponse(response)
    
    return JsonResponse({
        "error": "Method not allowed"
    }, status=405)

def submit_transaction(request):
    if not is_authenticated(request):
        return redirect('home:login')
    
    if request.method == "GET":
        email = get_email(request)
        return render(request, 'home/add_transaction.html', {"email": email})
    if request.method == "POST":
        return submit_transaction_util(request)

    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def delete_income(request):
    if request.method == "DELETE":
        return delete_income_util(request)

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
    return get_incomes_util(request)

@csrf_exempt
def visualize(request):
    if not is_authenticated(request):
        return redirect('home:login')
    email = get_email(request)
    user_id = get_user_id(request)
    
    visualizations = generate_visualizations_data(user_id)
    
    data = {'email':email,'visualizations':visualizations}

    # Render the visualize.html template with visualizations
    return render(request, "home/visualize.html",data) 


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

def set_budget(request):
    email=get_email(request)
    if request.method == "POST":
        budget = request.POST.get("budget")
        category = request.POST.get("category")
        # Example logic to save the budget (You may need to connect with your database)
        messages.success(request, f"Budget of {budget} for {category} set successfully!")
        return redirect("set_budget")
    return render(request, "home/set_Budget.html", {"email": email})
