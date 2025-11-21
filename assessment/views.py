# assessment/views.py
import json
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from .models import Test, AssessmentResult, Job
from .ai import get_ai_analysis

@ensure_csrf_cookie
def assessment_view(request):
    """
    Renders the main SPA.
    Always sends logged-in users to the Home page, ready to start.
    """
    context = {'is_authenticated': request.user.is_authenticated}
    
    if request.user.is_authenticated:
        # 1. Always start at Home
        context['initial_page'] = 'home'
        
        # 2. Find the Primary Assessment ID so the "Start" button knows what to load
        primary_test = Test.objects.filter(is_primary_assessment=True).first()
        if primary_test:
            context['start_test_id'] = primary_test.id
    else:
        # Guest users start at Login
        context['initial_page'] = 'user-info'

    return render(request, 'assessment/assessment.html', context)

@login_required
def get_test_questions_api(request, test_id):
    """API to get the questions for a specific test."""
    test = get_object_or_404(Test, pk=test_id)
    return JsonResponse(test.questions, safe=False)

@login_required
def get_ai_analysis_view(request, test_id):
    """API to submit answers and get analysis."""
    test = get_object_or_404(Test, pk=test_id)
    if request.method == 'POST':
        try:
            answers_data = json.loads(request.body)
            
            # 1. Get analysis from AI
            ai_analysis = get_ai_analysis(answers_data, test.system_prompt)
            
            # 2. THE NEW LOGIC: Match Jobs to Tests
            # We iterate through the recommended jobs and check if we have a test for them.
            if 'recommended_jobs' in ai_analysis:
                for job_item in ai_analysis['recommended_jobs']:
                    job_name = job_item.get('job')
                    # Look for a test linked to a Job with this exact name
                    related_test = Test.objects.filter(related_job__name=job_name).first()
                    if related_test:
                        # If found, attach the test ID to the JSON response
                        job_item['test_id'] = related_test.id

            # 3. Save the result (now including the test_ids in the analysis JSON)
            AssessmentResult.objects.create(
                user=request.user,
                test=test,
                answers=answers_data,
                ai_analysis=ai_analysis
            )
            
            return JsonResponse({'status': 'success', 'analysis': ai_analysis})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=405)

@login_required
def dashboard_api_view(request):
    """API to get the data for the user's dashboard."""
    # Find the latest primary assessment result
    primary_result = AssessmentResult.objects.filter(user=request.user, test__is_primary_assessment=True).order_by('-created_at').first()
    
    recommended_tests = []
    if primary_result and primary_result.ai_analysis:
        recommended_job_names = [job['job'] for job in primary_result.ai_analysis.get('recommended_jobs', [])]
        # Find tests related to the recommended jobs
        recommended_tests = list(Test.objects.filter(related_job__name__in=recommended_job_names).values('id', 'name', 'description'))

    # Get all other non-primary tests
    other_tests = list(Test.objects.filter(is_primary_assessment=False).exclude(id__in=[t['id'] for t in recommended_tests]).values('id', 'name', 'description'))

    data = {
        'recommended_tests': recommended_tests,
        'other_tests': other_tests,
    }
    return JsonResponse(data)


@login_required
def get_tests_list_api(request):
    """Returns a list of all non-primary (Level Assessment) tests."""
    # We filter for tests that are NOT the primary assessment
    tests = Test.objects.filter(is_primary_assessment=False).values('id', 'name', 'description')
    return JsonResponse({'status': 'success', 'tests': list(tests)})