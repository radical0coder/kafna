import json
from .ai import get_ai_analysis
from django.http import JsonResponse
from django.shortcuts import render
from .models import Question, AssessmentResult
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

# This view serves the main HTML page (the "shell")
@ensure_csrf_cookie
def assessment_view(request):
    """
    Renders the main SPA. The logic is now simple again.
    """
    context = {}
    context['is_authenticated'] = request.user.is_authenticated

    if request.user.is_authenticated:
        # A logged-in user always starts at the homepage.
        context['initial_page'] = 'home'
    else:
        # An anonymous user always starts at the login page.
        context['initial_page'] = 'user-info'

    return render(request, 'assessment/assessment.html', context)

# This is our API endpoint
def get_questions_api(request):
    """
    API endpoint that returns all assessment questions as JSON.
    """
    # Use order_by to be certain they are in the correct sequence
    questions_queryset = Question.objects.order_by('order').prefetch_related('choices').all()
    
    questions_list = []
    for q in questions_queryset:
        question_data = {
            'id': q.id,
            'type': q.question_type,
            'question': q.question_text,
        }
        if q.question_type == 'multiple':
            # Ensure choices are ordered if you add an order field to them later
            question_data['options'] = [choice.choice_text for choice in q.choices.all()]
        elif q.question_type == 'slider':
            question_data['min'] = 1
            question_data['max'] = 5
        
        questions_list.append(question_data)
        
    return JsonResponse(questions_list, safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def get_ai_analysis_view(request):
    """
    This is now our SINGLE endpoint. It receives the answers,
    saves them, gets an AI analysis, and returns the analysis.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'User not authenticated.'}, status=403)
        try:
            answers_data = json.loads(request.body)
            
            # --- Call the AI service ---
            ai_analysis = get_ai_analysis(answers_data)
            
            # --- Save the complete result ---
            AssessmentResult.objects.create(
                user=request.user,
                answers=answers_data,
                ai_analysis=ai_analysis
            )
            
            # --- Return the analysis to the frontend ---
            return JsonResponse({'status': 'success', 'analysis': ai_analysis})
        
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed.'}, status=405)