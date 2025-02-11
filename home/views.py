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
    if request.session.get('id_token'):
        return redirect('home:dashboard')

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
    if request.method == "POST":
        logout(request)  # Django logout function
        request.session.flush()  # Clears session data
        return JsonResponse({"message": "Logged out successfully"}, status=200)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)

def dashboard_view(request):
    context = {
        "user": request.user,
        "total_balance": 5250,
        "total_expenses": 1750,
        "total_income": 3500,
        "budget_utilization": 50,  # Example percentage
        "transactions":'TODO',  # Replace with actual DB query
    }
    return render(request, 'home/dashboard.html', context)


from django.shortcuts import render, redirect
from .models import Transaction

def add_transaction(request):
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
from django.shortcuts import render
from datetime import date
def income_tracker(request):
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