from django.urls import path
from . import views

app_name = 'insights'

urlpatterns = [
    path('predictive-analysis/', views.predictive_analysis_page, name='predictive_analysis'),
    path('api/get-smart-analysis/', views.get_smart_analysis_api, name='get_smart_analysis_api'),

     # New URLs for the Spending Insights page
    path('spending-insights/', views.spending_insights_page, name='spending_insights'),

     # New URLs for the Investment Guide
    path('investment-guide/', views.investment_guide_page, name='investment_guide'),
    path('api/generate-investment-tips/', views.generate_investment_tips_api, name='generate_investment_tips_api'),
    path("api/get-city/", views.get_city_api, name="get_city_api"),
    path('api/get-spending-insights/', views.get_spending_insights_api, name='get_spending_insights_api'),
]
