from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('add_transaction/', views.submit_transaction, name="add_transaction"),
    path('delete_income/', views.delete_income, name="delete_income"),
    path('income_tracker/', views.income_tracker, name="income_tracker"),
    path('get_incomes/', views.get_incomes, name="get_incomes"),
    path('add_category/', views.add_category, name="add_category"),
]
