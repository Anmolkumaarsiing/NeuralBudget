from django.http import JsonResponse
from firebase_admin import auth
from django.contrib.auth import logout
from apps.common_utils.firebase_service import copy_default_categories_to_user, create_user_profile, update_user_profile, update_user_profile_picture, firebase_login, verify_firebase_token
from django.core.files.storage import default_storage
from django.conf import settings
import os
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def register_user(request, data, first_name, last_name, phone_number):
    try:
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        # 1. Create user in Firebase Authentication
        user = auth.create_user(
            email=email,
            password=password,
            display_name=username
        )
        uid = user.uid

        # 2. Copy default categories to user's collection
        copy_default_categories_to_user(uid)
        
        # 3. Create user profile in Firestore with new fields
        create_user_profile(uid, email, username, first_name, last_name, phone_number) 

        # 4. Automatically log in the user after registration
        response_data = firebase_login(email, password)
        id_token = response_data.get("idToken")

        if not id_token:
            raise Exception("Failed to retrieve ID token after registration.")

        decoded_token = verify_firebase_token(id_token)
        
        # Use display name from profile if available (or default to username)
        display_name_from_profile = username # For new registration, username is the display name

        request.session['user_id'] = uid
        request.session['email'] = email
        request.session['id_token'] = id_token
        request.session['display_name'] = display_name_from_profile

        return {"message": "Registration successful", "uid": uid, "redirect_url": "/reports/dashboard"}

    except auth.EmailAlreadyExistsError:
        return {"error": "Email already exists"}
    except Exception as e:
        return {"error": str(e)}
#CSRF_Exempt
def logout_user(request):
    try:
        user_id = request.session.get('user_id')
        if user_id:
            # Revoke Firebase refresh tokens for the user
            auth.revoke_refresh_tokens(user_id)
            print(f"[DEBUG] Firebase refresh tokens revoked for user: {user_id}")

        # Clear Firebase session info from Django session
        if 'id_token' in request.session:
            del request.session['id_token']
        if 'user_id' in request.session:
            del request.session['user_id']
        if 'email' in request.session:
            del request.session['email']
        
        # Django logout
        logout(request)
        request.session.flush()
        
        return {"message": "Logged out successfully", "redirect_url": "/accounts/login/"}
    except Exception as e:
        return {"error": str(e)}

def update_profile_service(user_id, data):
    try:
        update_user_profile(user_id, data)
        return {"message": "Profile updated successfully"}
    except Exception as e:
        return {"error": str(e)}

def upload_profile_picture_service(user_id, uploaded_file):
    try:
        # Define the path where the file will be saved
        file_extension = os.path.splitext(uploaded_file.name)[1]
        file_name = f'{user_id}{file_extension}'
        file_path = os.path.join('profile_photos', file_name)

        # Save the file using Django's default storage
        full_path = default_storage.save(file_path, uploaded_file)

        # Construct the URL to the saved file
        photo_url = os.path.join(settings.MEDIA_URL, full_path).replace(os.sep, '/')

        # Update the user's profile in Firestore with the new photo URL
        update_user_profile_picture(user_id, photo_url)

        return {"message": "Profile picture uploaded successfully", "photo_url": photo_url}
    except Exception as e:
        return {"error": str(e)}

def send_password_reset_email_service(email):
    try:
        link = auth.generate_password_reset_link(email)
        # print(f"[DEBUG] Generated password reset link: {link}")
        # print(settings.DEFAULT_FROM_EMAIL)

        # Render email content from a template
        html_message = render_to_string('accounts/password_reset_email.html', {'reset_link': link})
        plain_message = strip_tags(html_message)

        send_mail(
            'Password Reset for NeuralBudget',
            plain_message,
            settings.DEFAULT_FROM_EMAIL, # Sender email
            [email], # Recipient email
            html_message=html_message,
            fail_silently=False,
        )

        return {"message": "Password reset email sent successfully. Please check your inbox."}
    except auth.UserNotFoundError:
        return {"error": "No user found with that email address.", "status": 404}
    except Exception as e:
        print(f"[DEBUG] Exception during password reset email sending: {e}")
        return {"error": str(e), "status": 500}