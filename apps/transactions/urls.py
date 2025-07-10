from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns =[
    path('income_tracker/', views.income_tracker, name='income_tracker'), 
    path('add_transaction/', views.submit_transaction, name='add_transaction'),
    path('get_incomes/', views.get_incomes, name='get_incomes'),
    path('delete_income/', views.delete_income, name='delete_income'),
]
