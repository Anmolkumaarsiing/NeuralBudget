from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

def home(request):
    return render(request, 'home/index.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")  # Change this to your desired page
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "home/login.html")

def signup_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered")
            else:
                user = User.objects.create_user(username, email, password1)
                user.save()
                messages.success(request, "Account created successfully. Please log in.")
                return redirect("login")
        else:
            messages.error(request, "Passwords do not match")
    return render(request, "home/signup.html")

def logout_view(request):
    logout(request)
    return redirect("login")


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Dummy data for transactions (Replace with DB query)
transactions_data = [
    {"category": "Groceries", "amount": 150, "status": "Completed", "payment_date": "2025-02-05"},
    {"category": "OTT Subscriptions", "amount": 999, "status": "Pending", "payment_date": "2025-02-09"},
    {"category": "Electricity Bill", "amount": 800, "status": "Bill Due", "payment_date": "2025-02-11"},
]

def dashboard_view(request):
    context = {
        "user": request.user,
        "total_balance": 5250,
        "total_expenses": 1750,
        "total_income": 3500,
        "budget_utilization": 50,  # Example percentage
        "transactions": transactions_data,  # Replace with actual DB query
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
