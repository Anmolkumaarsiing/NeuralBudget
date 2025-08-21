from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')), # Core app URLs
    path('accounts/', include('apps.accounts.urls')), # Accounts app URLs
    path('transactions/', include('apps.transactions.urls')), # Transactions app URLs
    path('budgets/', include('apps.budgets.urls')), # Budgets app URLs
    path('reports/', include('apps.reports.urls')), # Reports app URLs
    path('ml_features/', include('apps.ml_features.urls')), # ML Features app URLs
    path('datagen/', include('apps.datagen.urls')), # datagen app URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
