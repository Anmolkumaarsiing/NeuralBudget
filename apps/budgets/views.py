from django.shortcuts import render, redirect
from django.contrib import messages
from apps.common_utils.auth_utils import get_email

def set_budget(request):
    email=get_email(request)
    if request.method == "POST":
        budget = request.POST.get("budget")
        category = request.POST.get("category")
        # Example logic to save the budget (You may need to connect with your database)
        messages.success(request, f"Budget of {budget} for {category} set successfully!")
        return redirect("set_budget")
    return render(request, "budgets/set_Budget.html", {"email": email})
