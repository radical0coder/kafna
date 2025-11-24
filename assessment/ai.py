# assessment/ai_processor.py
import google.generativeai as genai
import json
from decouple import config

# 1. Configure the Google AI client with your secret key
genai.configure(api_key=config('GOOGLE_API_KEY'))

# 2. Define the structure of our AI's brain (the System Prompt)
# This is almost identical to the OpenAI version.
# SYSTEM_PROMPT = """
# You are an expert career analyst. Your task is to analyze a user's answers to an assessment test and provide a concise, professional analysis in PERSIAN.

# The user's answers are provided as a JSON object where keys are question numbers.

# You MUST respond in a structured JSON format. Do not add any introductory text, greetings, closing remarks, or markdown formatting like ```json. Only output the raw JSON object.

# The required JSON structure is:
# {
#   "analysis": "A brief, one-paragraph summary of the user's personality and work style based on their answers.",
#   "recommended_jobs": [
#     { "job": "Job Title 1", "reason": "A short, one-sentence reason why this job fits the user." },
#     { "job": "Job Title 2", "reason": "A short, one-sentence reason why this job fits the user." },
#     { "job": "Job Title 3", "reason": "A short, one-sentence reason why this job fits the user." }
#   ],
#   "development_points": [
#     "A skill or knowledge area to develop.",
#     "Another skill or knowledge area to develop."
#   ],
#   "career_path": "A concise, one-paragraph summary of a potential career path."
# }
# """

def get_ai_analysis(rich_answers_data, system_prompt):
    """
    Takes RICH data (questions + answers), converts to SIMPLE data for AI,
    and returns the analysis.
    """
    try:
        # 1. Extract just the ID and Answer for the AI
        # The AI already knows the questions from the System Prompt
        simple_answers = {}
        
        # Handle cases where data might be old format vs new format
        if 'responses' in rich_answers_data:
            for item in rich_answers_data['responses']:
                simple_answers[item['question_id']] = item['answer']
        else:
            # Fallback for old data format
            simple_answers = rich_answers_data

        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=system_prompt
        )
        
        answers_json_string = json.dumps(simple_answers, indent=2, ensure_ascii=False)
        user_message = f"Analyze the following user answers:\n\n{answers_json_string}"
        
        response = model.generate_content(user_message)
        ai_response_text = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(ai_response_text)

    except Exception as e:
        print(f"AI Error: {e}")
        return {
            "mbti": {"type": "خطا", "description": "عدم دریافت پاسخ از هوش مصنوعی"},
            "recommended_jobs": [],
            "development_path": []
        }