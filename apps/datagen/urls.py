from django.urls import path
from . import views

app_name = 'datagen'

urlpatterns = [
    # AI Data Generator tool
    path('', views.data_generator_page, name='data_generator_page'),
    path('api/generate-data/', views.generate_data_api, name='generate_data_api'),

    # Data Deletion tool
    path('delete-data/', views.delete_data_page, name='delete_data_page'),
    path('api/delete-data/', views.delete_data_api, name='delete_data_api'),

    #Admin Overview page
    path('overview/', views.admin_overview_page, name='admin_overview_page'),
    path('api/get-admin-analytics/', views.get_admin_analytics_api, name='get_admin_analytics_api'),
]