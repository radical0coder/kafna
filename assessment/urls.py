# assessment/urls.py
from django.urls import path
from .views import (
    assessment_view, 
    get_test_questions_api, 
    get_ai_analysis_view,
     dashboard_api_view,
    get_tests_list_api,
    get_user_history_api,
    save_draft_view,
    perform_analysis_view
)

urlpatterns = [
    path('', assessment_view, name='assessment_home'),
    path('api/dashboard/', dashboard_api_view, name='api_dashboard'),
    path('api/tests/<int:test_id>/questions/', get_test_questions_api, name='api_get_test_questions'),
    path('api/tests/<int:test_id>/submit/', get_ai_analysis_view, name='api_get_ai_analysis'),
    path('api/tests/list/', get_tests_list_api, name='api_get_tests_list'),
    path('api/history/', get_user_history_api, name='api_get_user_history'),
    path('api/tests/<int:test_id>/save-draft/', save_draft_view, name='api_save_draft'),
    path('api/tests/<int:test_id>/analyze/<int:result_id>/', perform_analysis_view, name='api_perform_analysis'),
]