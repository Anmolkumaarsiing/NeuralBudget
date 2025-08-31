# apps/core/middleware/auth_middleware.py

from django.shortcuts import redirect
from django.urls import reverse
from apps.common_utils.auth_utils import is_authenticated, refresh_firebase_token
import time

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.public_urls = [
            reverse('accounts:login'),
            reverse('accounts:signup'),
            reverse('accounts:send_password_reset_email'),
            reverse('accounts:reset_password_form'),
            reverse('accounts:reset_done'),
        ]

    def __call__(self, request):
        # Token expiration handling
        if 'firebase_token_expiration' in request.session:
            expiration_time = request.session['firebase_token_expiration']
            if time.time() > expiration_time:
                try:
                    new_token_data = refresh_firebase_token(request)
                    request.session['firebase_id_token'] = new_token_data['id_token']
                    request.session['firebase_token_expiration'] = time.time() + new_token_data['expires_in']
                except Exception as e:
                    # Handle token refresh failure (e.g., redirect to login)
                    return redirect('accounts:login')

        if not is_authenticated(request) and request.path not in self.public_urls:
            # allow access to the root path
            if request.path == '/':
                return self.get_response(request)
            return redirect('accounts:login')
        
        response = self.get_response(request)
        return response