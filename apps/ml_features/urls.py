from django.urls import path
from . import views

app_name = 'ml_features'

urlpatterns = [
    path('categorize_expense/', views.categorize_expense_view, name='categorize_expense'),
]