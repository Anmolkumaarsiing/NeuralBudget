# apps/core/middleware/auth_middleware.py

from django.shortcuts import redirect
from django.urls import reverse
from apps.common_utils.auth_utils import is_authenticated
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
            reverse('accounts:google_login'),
            '/',
        ]

    def __call__(self, request):
        # Token expiration handling
        if 'firebase_token_expiration' in request.session:
            expiration_time = request.session['firebase_token_expiration']
            if time.time() > expiration_time:
                # Token has expired, redirect to login
                request.session.flush()
                return redirect('accounts:login')

        if not is_authenticated(request) and request.path not in self.public_urls and not request.path.startswith('/static/') and not request.path.startswith('/media/'):
            return redirect('accounts:login')
        
        response = self.get_response(request)
        return response