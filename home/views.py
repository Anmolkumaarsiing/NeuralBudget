from django.shortcuts import render, redirect
from django.contrib.auth import logout

from firebase_admin import auth
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import json

def home(request):
    return render(request, 'home/index.html')

def verify_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token,clock_skew_seconds=5)
        return decoded_token
    except Exception as e:
        print(f"Token verification error: {str(e)}")
        raise

@csrf_exempt  # Temporarily disable CSRF for testing
def login_view(request):
    if request.session.get('id_token'):
        return redirect('home:dashboard')

    if request.method == 'POST':
        try:
            # Get the authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return JsonResponse({'error': 'No authorization header'}, status=401)
            token = auth_header.split('Bearer ')[1]
            body = json.loads(request.body)
            email = body.get('email')
            try:
                # Verify the Firebase token
                decoded_token = verify_token(token)
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
    if request.method == "POST":
        try:
            print("Register view called")  # Debug line

            # Parse JSON data from the request
            data = json.loads(request.body)
            print("Request data:", data)  # Debug line

            username = data.get("username")
            email = data.get("email")
            id_token = data.get("idToken")

            print("Verifying Firebase token...")  # Debug line
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            print("Token verified, UID:", uid)  # Debug line

            # Store user data in session
            request.session['id_token'] = id_token
            request.session['uid'] = uid
            request.session['email'] = email
            request.session['username'] = username

            print("Registration successful, redirecting to dashboard")  # Debug line
            return JsonResponse({
                "message": "Registration successful",
                "redirect_url": "/dashboard/"
            })

        except auth.EmailAlreadyExistsError:
            print("Email already exists error")  # Debug line
            return JsonResponse({"error": "Email already exists"}, status=400)
        except Exception as e:
            print("Unexpected error:", str(e))  # Debug line
            return JsonResponse({"error": str(e)}, status=500)

    print("Method not allowed")  # Debug line
    return JsonResponse({"error": "Method not allowed"}, status=405)    # if request.session.get('id_token'):
    #     return redirect('home:dashboard')
    if request.method == "POST":
        try:
            print("Register view called")
            data = json.loads(request.body)
            print("data",data)
            username = data.get("username")
            email = data.get("email")
            id_token = data.get("idToken")

            # Verify the Firebase token
            decoded_token = verify_token(id_token)
            uid = decoded_token['uid']
            print("uid",uid)

            # Store user data in session
            request.session['id_token'] = id_token
            request.session['uid'] = uid
            request.session['email'] = email
            request.session['username'] = username

            return JsonResponse({
                "message": "Registration successful",
                "redirect_url": "/dashboard/"
            })

        except auth.EmailAlreadyExistsError:
            return JsonResponse({"error": "Email already exists"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)

def dashboard_view(request):
    if not request.session.get('id_token'):
        return redirect('home:login')
    
    id_token = request.session.get('id_token')
    try:    
        decoded_token = auth.verify_id_token(id_token)
        context = {
        "user": request.user,
        "email": decoded_token.get('email'),
        "total_balance": 5250,
        "total_expenses": 1750,
        "total_income": 3500,
        "budget_utilization": 50,  # Example percentage
        "transactions":'TODO',  # Replace with actual DB query
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