# assessment/urls.py
from django.urls import path
from .views import assessment_view, get_questions_api, submit_answers_api, get_ai_analysis_view

urlpatterns = [
    path('', assessment_view, name='assessment_home'),
    path('api/questions/', get_questions_api, name='api_get_questions'),
    path('api/submit-answers/', submit_answers_api, name='api_submit_answers'),
    path('api/get-ai-analysis/', get_ai_analysis_view, name='api_get_ai_analysis'),
]