import re
from django.shortcuts import render
import json
import random
from django.http import JsonResponse
from django.contrib.auth import login
from .models import CustomUser, OTP
from .sms_service import send_otp_sms
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth import logout
from django.shortcuts import redirect



def request_otp_view(request):
    """
    Receives a phone number, generates an OTP, saves it,
    and "sends" it via our mock SMS service.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        phone_number = data.get('phone_number')

        if not phone_number:
            return JsonResponse({'status': 'error', 'message': 'Phone number is required.'}, status=400)

        if not re.match(r'^09\d{9}$', phone_number):
            return JsonResponse({'status': 'error', 'message': 'Invalid phone number format.'}, status=400)
        
        code = str(random.randint(100000, 999999))
        OTP.objects.create(phone_number=phone_number, code=code)
        send_otp_sms(phone_number, code)

        return JsonResponse({'status': 'success', 'message': 'OTP sent successfully.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


def verify_otp_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone_number = data.get('phone_number')
        code = data.get('code')
        full_name = data.get('full_name') # Changed

        if not phone_number or not code or not full_name: # Changed
            return JsonResponse({'status': 'error', 'message': 'All fields are required.'}, status=400)

        otp_entry = OTP.objects.filter(phone_number=phone_number).order_by('-created_at').first()

        if otp_entry and otp_entry.code == code:
            user, created = CustomUser.objects.get_or_create(phone_number=phone_number)
            if created:
                user.full_name = full_name # Changed
                user.save()
            
            login(request, user)
            otp_entry.delete()
            
            request.session['just_logged_in'] = True
             
            return JsonResponse({'status': 'success', 'message': 'Login successful.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid OTP code.'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


@login_required
@require_http_methods(["GET", "POST"]) # This view only accepts GET and POST
def profile_api_view(request):
    """
    API for getting and updating the logged-in user's profile.
    This version robustly handles empty optional fields.
    """
    user = request.user

    if request.method == 'GET':
        # The GET request logic is correct and does not need to change.
        data = {
            'phone_number': user.phone_number,
            'full_name': user.full_name,
            'address': user.address,
            'age': user.age,
            'about_me': user.about_me,
        }
        return JsonResponse({'status': 'success', 'profile': data})

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # --- THE FIX: A clean, scalable loop ---

            # 1. Define which fields the user is allowed to update.
            updatable_fields = ['full_name', 'address', 'about_me', 'age']

            # 2. Loop through the fields and update the user object.
            for field in updatable_fields:
                # Check if the frontend sent a value for this field
                if field in data:
                    value = data[field]
                    
                    # Special handling for the 'age' field
                    if field == 'age':
                        # If age is an empty string or None, set it to None in the database.
                        if value == '' or value is None:
                            setattr(user, field, None)
                        else:
                            # Otherwise, convert it to an integer.
                            setattr(user, field, int(value))
                    else:
                        # For all other fields (text), just set the value.
                        setattr(user, field, value)
            
            user.save()
            return JsonResponse({'status': 'success', 'message': 'Profile updated successfully.'})
        
        except (json.JSONDecodeError, ValueError):
            # This now catches errors from both bad JSON and bad 'age' values (e.g., "abc").
            return JsonResponse({'status': 'error', 'message': 'Invalid data.'}, status=400)
    
    
def logout_view(request):
    logout(request)
    return redirect('assessment_home') # Redirect to the homepage after logout