from django.http import JsonResponse
from firebase_admin import auth
from django.contrib.auth import logout

def register_user(data):
    try:
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        user = auth.create_user(
            email=email,
            password=password,
            display_name=username
        )
        uid = user.uid

        return {"message": "Registration successful", "uid": uid, "redirect_url": "/dashboard/"}

    except auth.EmailAlreadyExistsError:
        return {"error": "Email already exists"}
    except Exception as e:
        return {"error": str(e)}

def logout_user(request):
    try:
        # Clear Firebase session
        if 'id_token' in request.session:
            del request.session['id_token']
        if 'user_id' in request.session:
            del request.session['user_id']
        if 'email' in request.session:
            del request.session['email']
        
        # Django logout
        logout(request)
        request.session.flush()
        
        return {"message": "Logged out successfully", "redirect_url": "/home/login/"}
    except Exception as e:
        return {"error": str(e)}
