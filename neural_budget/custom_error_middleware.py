
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

class CustomErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        logger.error(f"Unhandled exception: {exception}", exc_info=True)
        return JsonResponse({
            'error': 'An unexpected error occurred. Please try again later.'
        }, status=500)
