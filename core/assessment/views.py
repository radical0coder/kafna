import json
from .ai import get_ai_analysis
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


@csrf_exempt
@require_http_methods(["POST"])
def get_ai_analysis_view(request):
    """
    1. Receives: {user_name, user_phone, answers: [{id,question,answer}, …]}
    2. Calls LLM → `ai_analysis`
    3. Saves **both** to AssessmentResult (no user required)
    4. Returns the analysis for instant rendering
    """
    try:
        data = json.loads(request.body)

        # ------------------------------------------------------------------
        #  Build the *rich* answers list (front-end already sends it)
        # ------------------------------------------------------------------
        answers_list = data.get("answers", [])
        if not isinstance(answers_list, list):
            raise ValueError("answers must be a list")

        # ------------------------------------------------------------------
        #  Call LLM
        # ------------------------------------------------------------------
        ai_analysis = get_ai_analysis(answers_list)

        # ------------------------------------------------------------------
        #  Save everything anonymously
        # ------------------------------------------------------------------
        AssessmentResult.objects.create(
            user_name=data.get("user_name", ""),
            user_phone=data.get("user_phone", ""),
            answers=answers_list,
            ai_analysis=ai_analysis
        )

        return JsonResponse({
            "status": "success",
            "analysis": ai_analysis
        })

    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

    # GET not allowed
    return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)