from django.urls import path
from . import views

app_name = 'budgets'

urlpatterns =[
    path('set-budget/', views.set_budget, name="set_budget"),
]
