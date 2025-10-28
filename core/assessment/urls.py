# assessment/urls.py
from django.urls import path
# Add submit_answers_api to the import
from .views import assessment_view, get_questions_api, submit_answers_api

urlpatterns = [
    path('', assessment_view, name='assessment_home'),
    path('api/questions/', get_questions_api, name='api_get_questions'),
    # New URL for submitting answers
    path('api/submit-answers/', submit_answers_api, name='api_submit_answers'),
]