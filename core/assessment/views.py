# assessment/views.py

import json
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
            question_data['max'] = 10
        
        questions_list.append(question_data)
        
    return JsonResponse(questions_list, safe=False)

@csrf_exempt # Important: For APIs, we often handle CSRF differently.
def submit_answers_api(request):
    if request.method == 'POST':
        try:
            # Load the JSON data from the request body
            data = json.loads(request.body)
            
            # Create a new AssessmentResult record
            AssessmentResult.objects.create(answers=data)
            
            return JsonResponse({'status': 'success', 'message': 'Results saved successfully.'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=405)