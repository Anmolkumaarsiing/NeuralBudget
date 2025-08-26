from django.urls import path
from . import views

app_name = 'datagen'

urlpatterns = [
    # This now makes the 'overview' page the default for the app
    path('', views.admin_overview_page, name='admin_overview_page'),
    
    # URL for the AI Data Generator tool page
    path('generate/', views.data_generator_page, name='data_generator_page'),
    
    # URL for the Data Deletion tool page
    path('delete-data/', views.delete_data_page, name='delete_data_page'),

    # New URLs for the Historical Data Generator
    path('historical-generator/', views.historical_data_page, name='historical_data_page'),
    path('api/generate-historical-data/', views.generate_historical_data_api, name='generate_historical_data_api'),

    # --- API Endpoints ---
    path('api/generate-data/', views.generate_data_api, name='generate_data_api'),
    path('api/delete-data/', views.delete_data_api, name='delete_data_api'),
    path('api/get-admin-analytics/', views.get_admin_analytics_api, name='get_admin_analytics_api'),
]