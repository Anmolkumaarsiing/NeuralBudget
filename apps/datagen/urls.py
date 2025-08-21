from django.urls import path
from . import views

app_name = 'datagen'

urlpatterns = [
    path('', views.data_generator_page, name='data_generator_page'),
    path('api/generate-data/', views.generate_data_api, name='generate_data_api'),
]