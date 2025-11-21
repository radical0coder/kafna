# assessment/urls.py
from django.urls import path
from .views import (
    assessment_view, 
    get_test_questions_api, 
    get_ai_analysis_view,
    dashboard_api_view,
    get_tests_list_api,
)

urlpatterns = [
    path('', assessment_view, name='assessment_home'),
    path('api/dashboard/', dashboard_api_view, name='api_dashboard'),
    path('api/tests/<int:test_id>/questions/', get_test_questions_api, name='api_get_test_questions'),
    path('api/tests/<int:test_id>/submit/', get_ai_analysis_view, name='api_get_ai_analysis'),
    path('api/tests/list/', get_tests_list_api, name='api_get_tests_list'),
]