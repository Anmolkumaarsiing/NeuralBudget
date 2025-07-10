from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')), # Core app URLs
    path('accounts/', include('apps.accounts.urls')), # Accounts app URLs
    path('transactions/', include('apps.transactions.urls')), # Transactions app URLs
    path('budgets/', include('apps.budgets.urls')), # Budgets app URLs
    path('reports/', include('apps.reports.urls')), # Reports app URLs
    path('ml-features/', include('apps.ml_features.urls')), # ML Features app URLs
]
