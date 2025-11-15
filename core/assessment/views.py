# assessment/views.py

import json
from django.http import JsonResponse
from django.shortcuts import render
from .models import Question, AssessmentResult
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

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

@csrf_exempt
@require_http_methods(["POST"])
def submit_answers_api(request):
    try:
        data = json.loads(request.body)
        
        # Save to DB (you can expand this model later)
        AssessmentResult.objects.create(
            user_name=data.get('user_name', ''),
            user_phone=data.get('user_phone', ''),
            answers=data.get('answers', [])  # now list of dicts
        )

        return JsonResponse({"status": "success", "message": "نتایج با موفقیت ذخیره شد."})
    
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "داده نامعتبر"}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)