from django.urls import path
from . import views

app_name = 'insights'

urlpatterns = [
    path('predictive-analysis/', views.predictive_analysis_page, name='predictive_analysis'),
    path('smart-categorization/', views.smart_categorization_page, name='smart_categorization'),
    path('api/get-smart-analysis/', views.get_smart_analysis_api, name='get_smart_analysis_api'),
]