import json
from .ai import get_ai_analysis
from django.http import JsonResponse
from django.shortcuts import render
from .models import Question, AssessmentResult
from django.views.decorators.csrf import csrf_exempt

# This view serves the main HTML page (the "shell")
def assessment_view(request):
    return render(request, 'assessment/assessment.html')

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
def submit_answers_api(request):
    if request.method == 'POST':
        try:
            # Load the JSON from the request into a Python dictionary
            data = json.loads(request.body)
            
            AssessmentResult.objects.create(answers=data)
            
            return JsonResponse({'status': 'success', 'message': 'Results saved successfully.'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=405)


def get_ai_analysis_view(request):
    """
    API endpoint that gets an AI analysis AND saves the complete result anonymously.
    """
    if request.method == 'POST':
        try:
            answers_data = json.loads(request.body)
            ai_analysis = get_ai_analysis(answers_data)

            # THE FIX: We create the AssessmentResult without any user.
            AssessmentResult.objects.create(
                answers=answers_data,
                ai_analysis=ai_analysis
            )

            return JsonResponse({'status': 'success', 'analysis': ai_analysis})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=405)