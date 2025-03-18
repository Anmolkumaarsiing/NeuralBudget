from django.urls import path
from . import views
from .views import visualize,login_view, register_view, logout_view, dashboard_view,get_incomes, income_tracker, submit_transaction, delete_income
app_name = 'home'

urlpatterns =[
    path('', views.home, name='home'),
    path("login/", login_view, name="login"),
    path("signup/", register_view, name="signup"),
    path("logout/", logout_view, name="logout"),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('income_tracker/', income_tracker, name='income_tracker'), 
    path('add_transaction/', submit_transaction, name='add_transaction'),
    path('get_incomes/', get_incomes, name='get_incomes'),
    path("set-budget/", views.set_budget, name="set_budget"),
    path('delete_income/', delete_income, name='delete_income'),
    path('visualize/', visualize, name='visualize'),
]
