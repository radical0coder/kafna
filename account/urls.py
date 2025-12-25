# accounts/urls.py
from django.urls import path
from .views import get_user_rank_api, request_otp_view, verify_otp_view, profile_api_view, logout_view, redeem_code_view, get_user_rank_api, request_payment_view, validate_promo_code_api

app_name = 'accounts' # It's good practice to namespace your app's URLs

urlpatterns = [
    path('api/request-otp/', request_otp_view, name='api_request_otp'),
    path('api/verify-otp/', verify_otp_view, name='api_verify_otp'),
    path('api/profile/', profile_api_view, name='api_profile'),
    path('logout/', logout_view, name='logout'),
    path('api/redeem-code/', redeem_code_view, name='api_redeem_code'),
    path('api/user-rank/', get_user_rank_api, name='api_user_rank'),
    path('api/request-payment/', request_payment_view, name='api_request_payment'),
    path('api/validate-promo-code/', validate_promo_code_api, name='api_validate_promo_code'),
]