import re
from django.shortcuts import render
import json
import random
from django.http import JsonResponse
from django.contrib.auth import login
from .models import CustomUser, OTP, PromoCode
from .sms_service import send_otp_sms
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.db.models import Count, F
from django.db.models.functions import Coalesce
from pyexpat.errors import messages


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


@login_required
def subscription_status_api(request):
    if request.method == 'POST':
        # MOCK PAYMENT: Just set them to premium immediately
        request.user.is_premium = True
        request.user.save()
        return JsonResponse({'status': 'success', 'message': 'Account upgraded!'})
    
    return JsonResponse({'status': 'success', 'is_premium': request.user.is_premium})


@login_required
def redeem_code_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code', '').strip().upper()
            
            # Define your mock codes here
            if code in ['KAFNA_VIP', 'TEST_PREMIUM']: 
                request.user.is_premium = True
                request.user.save()
                return JsonResponse({'status': 'success', 'message': 'Account upgraded to Premium!'})
            
            return JsonResponse({'status': 'error', 'message': 'کد وارد شده نامعتبر است.'})
        except:
            return JsonResponse({'status': 'error', 'message': 'Error processing request.'})
    return JsonResponse({'status': 'error'}, status=405)


@login_required
def get_user_rank_api(request):
    """
    Calculates the rank of the current user based on the number of assessments taken.
    """
    user = request.user
    
    # 1. Annotate all users with the count of their assessments
    # 'Coalesce' ensures that users with zero assessments are counted as 0 instead of None
    all_users_with_counts = CustomUser.objects.annotate(
        assessment_count=Coalesce(Count('assessments'), 0)
    )
    
    # 2. Get the current user's assessment count
    try:
        current_user_data = all_users_with_counts.get(pk=user.pk)
        current_user_assessment_count = current_user_data.assessment_count
    except CustomUser.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)

    # 3. Calculate the rank by counting how many users have MORE assessments
    rank = all_users_with_counts.filter(assessment_count__gt=current_user_assessment_count).count() + 1
    
    # Get the total number of users for context
    total_users = all_users_with_counts.count()

    return JsonResponse({
        'status': 'success',
        'rank': rank,
        'total_users': total_users,
        'assessment_count': current_user_assessment_count,
    })
    
    
def normalize_persian_numerals(text):
    if not text: return text
    persian_to_latin = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
    return text.translate(persian_to_latin)


@login_required
@require_http_methods(["POST"])
def request_payment_view(request):
    """
    MVP MOCK: Instantly upgrades user to premium, now accepting amount and promo code.
    """
    try:
        data = json.loads(request.body)
        amount = data.get('amount', 0)
        promo_code = data.get('promo_code', '')
        
        # This is your mock payment success logic
        request.user.is_premium = True
        request.user.save()
        messages.success(request, f'حساب شما با موفقیت به نسخه ویژه ارتقا یافت! مبلغ پرداخت شده: {amount} تومان.')
        return JsonResponse({'status': 'success', 'message': 'Account instantly upgraded!'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    
@login_required
@require_http_methods(["POST"])
def validate_promo_code_api(request):
    """
    API to validate a promo code and return its discount.
    """
    try:
        data = json.loads(request.body)
        code = data.get('code', '').strip().upper()
        base_price = data.get('base_price', 0) # Frontend sends base price for calculation

        if not code:
            return JsonResponse({'status': 'error', 'message': 'کد تخفیف نمی‌تواند خالی باشد.'}, status=400)
        
        # Look up the promo code in the database
        promo_obj = PromoCode.objects.filter(code=code, is_active=True).first()

        if promo_obj:
            discount = promo_obj.get_discount_amount(base_price)
            return JsonResponse({'status': 'success', 'discount': discount})
        else:
            return JsonResponse({'status': 'error', 'message': 'کد تخفیف نامعتبر یا منقضی شده است.'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)