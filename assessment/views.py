import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from .models import Test, AssessmentResult
from .ai import get_ai_analysis

@ensure_csrf_cookie
def assessment_view(request):
    context = {'is_authenticated': request.user.is_authenticated}
    
    if request.user.is_authenticated:
        context['initial_page'] = 'home'
        primary_test = Test.objects.filter(is_primary_assessment=True).first()
        if primary_test:
            context['start_test_id'] = primary_test.id
    else:
        context['initial_page'] = 'user-info'

    return render(request, 'assessment/assessment.html', context)

@login_required
def get_test_questions_api(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    return JsonResponse(test.questions, safe=False)

def find_related_test_id(job_name):
    if not job_name:
        return None
    
    job_name = job_name.strip()
    
    test = Test.objects.filter(related_job__name__iexact=job_name).first()
    if test:
        return test.id

    test = Test.objects.filter(name__iexact=job_name).first()
    if test:
        return test.id

    test = Test.objects.filter(name__icontains=job_name).first()
    if test:
        return test.id
        
    return None

def link_jobs_to_analysis(ai_analysis):
    if 'recommended_jobs' in ai_analysis:
        for job_item in ai_analysis['recommended_jobs']:
            job_name = job_item.get('job', '')
            linked_id = find_related_test_id(job_name)
            if linked_id:
                job_item['test_id'] = linked_id

@login_required
def get_ai_analysis_view(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    
    if request.method == 'POST':
        try:
            answers_data = json.loads(request.body)
            ai_analysis = get_ai_analysis(answers_data, test.system_prompt)
            
            link_jobs_to_analysis(ai_analysis)

            AssessmentResult.objects.create(
                user=request.user,
                test=test,
                answers=answers_data,
                ai_analysis=ai_analysis
            )
            
            return JsonResponse({'status': 'success', 'analysis': ai_analysis})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only POST requests allowed'}, status=405)

@login_required
def dashboard_api_view(request):
    primary_result = AssessmentResult.objects.filter(user=request.user, test__is_primary_assessment=True).order_by('-created_at').first()
    
    recommended_tests = []
    if primary_result and primary_result.ai_analysis:
        recommended_job_names = [job['job'] for job in primary_result.ai_analysis.get('recommended_jobs', [])]
        recommended_tests = list(Test.objects.filter(related_job__name__in=recommended_job_names).values('id', 'name', 'description'))

    other_tests = list(Test.objects.filter(is_primary_assessment=False).exclude(id__in=[t['id'] for t in recommended_tests]).values('id', 'name', 'description'))

    data = {
        'recommended_tests': recommended_tests,
        'other_tests': other_tests,
    }
    return JsonResponse(data)

@login_required
def get_tests_list_api(request):
    tests = Test.objects.filter(is_primary_assessment=False).values('id', 'name', 'description')
    return JsonResponse({'status': 'success', 'tests': list(tests)})

@login_required
def get_user_history_api(request):
    results = AssessmentResult.objects.filter(user=request.user).select_related('test').order_by('-created_at')
    
    history_data = []
    for r in results:
        history_data.append({
            'id': r.id,
            'test_name': r.test.name,
            'date': r.created_at.strftime('%Y/%m/%d'),
            'time': r.created_at.strftime('%H:%M'),
            'answers': r.answers,
            'analysis': r.ai_analysis
        })
        
    return JsonResponse({'status': 'success', 'history': history_data})

@login_required
def save_draft_view(request, test_id):
    if request.method == 'POST':
        test = get_object_or_404(Test, pk=test_id)
        try:
            answers_data = json.loads(request.body)
            
            result = AssessmentResult.objects.create(
                user=request.user,
                test=test,
                answers=answers_data,
                ai_analysis=None
            )
            
            return JsonResponse({'status': 'success', 'result_id': result.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)

@login_required
def perform_analysis_view(request, test_id, result_id):
    if request.method == 'POST':
        try:
            result = get_object_or_404(AssessmentResult, pk=result_id, user=request.user)
            test = result.test
            
            ai_analysis = get_ai_analysis(result.answers, test.system_prompt)
            link_jobs_to_analysis(ai_analysis)
            
            result.ai_analysis = ai_analysis
            result.save()
            
            return JsonResponse({'status': 'success', 'analysis': ai_analysis})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error'}, status=405)