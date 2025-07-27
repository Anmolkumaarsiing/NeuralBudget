from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('add_transaction/', views.submit_transaction, name="add_transaction"),
    path('delete_transaction/', views.delete_transaction, name="delete_transaction"),
    path('transaction_history/', views.transaction_history, name="transaction_history"),
    path('get_transactions/', views.get_transactions_history, name="get_transactions"),
    path('add_category/', views.add_category, name="add_category"),
]
