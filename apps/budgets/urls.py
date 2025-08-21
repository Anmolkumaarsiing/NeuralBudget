from django.urls import path
from . import views

app_name = 'budgets'

urlpatterns =[
    path('set-budget/', views.set_budget, name="set_budget"),
    path('get_budgets/', views.get_budgets, name="get_budgets"),
    path('smart-saver/', views.smart_saver, name="smart_saver"),
    path('smart-categorization/', views.smart_categorization, name='smart_categorization'),
    path('api/get-smart-analysis/', views.get_smart_analysis_data, name='get_smart_analysis_data'),
]
