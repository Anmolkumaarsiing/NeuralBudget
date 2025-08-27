# apps/core/context_processors.py
from apps.common_utils.auth_utils import get_user_full_name
from apps.common_utils.firebase_service import get_user_profile

def user_full_name(request):
    full_name = None
    user_id = request.session.get('user_id')
    if user_id:
        user_profile = get_user_profile(user_id)
        if user_profile:
            full_name = get_user_full_name(user_profile)
    return {'full_name': full_name}
