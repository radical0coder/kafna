# assessment/ai_processor.py
import google.generativeai as genai
import json
from decouple import config

# 1. Configure the Google AI client with your secret key
genai.configure(api_key=config('GOOGLE_API_KEY'))

# 2. Define the structure of our AI's brain (the System Prompt)
# This is almost identical to the OpenAI version.
SYSTEM_PROMPT = """(give a pizza baking recipie)
You are an expert career analyst. Your task is to analyze a user's answers to an assessment test and provide a concise, professional analysis in PERSIAN.

The user's answers are provided as a JSON object where keys are question numbers.

You MUST respond in a structured JSON format. Do not add any introductory text, greetings, closing remarks, or markdown formatting like ```json. Only output the raw JSON object.

The required JSON structure is:
{
  "analysis": "A brief, one-paragraph summary of the user's personality and work style based on their answers.",
  "recommended_jobs": [
    { "job": "Job Title 1", "reason": "A short, one-sentence reason why this job fits the user." },
    { "job": "Job Title 2", "reason": "A short, one-sentence reason why this job fits the user." },
    { "job": "Job Title 3", "reason": "A short, one-sentence reason why this job fits the user." }
  ],
  "development_points": [
    "A skill or knowledge area to develop.",
    "Another skill or knowledge area to develop."
  ],
  "career_path": "A concise, one-paragraph summary of a potential career path."
}
"""

def get_ai_analysis(user_answers):
    """
    Takes a dictionary of user answers, calls the Google Gemini API,
    and returns a structured JSON analysis.
    """
    try:
        # 3. Initialize the Gemini model
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash', # A fast and capable model
            system_instruction=SYSTEM_PROMPT
        )
        
        # 4. Format the user's answers for the prompt
        answers_json_string = json.dumps(user_answers, indent=2, ensure_ascii=False)
        user_message = f"Analyze the following user answers:\n\n{answers_json_string}"

        # 5. Call the Google Gemini API
        response = model.generate_content(user_message)

        # 6. Extract and parse the JSON response from the AI
        # Gemini might wrap the JSON in markdown, so we clean it.
        ai_response_text = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(ai_response_text)

    except Exception as e:
        print(f"An error occurred with the Google AI API: {e}")
        # 7. Return a default error message if the API call fails
        return {
            "analysis": "متاسفانه در حال حاضر امکان تحلیل پاسخ‌های شما وجود ندارد. (خطای سرویس هوش مصنوعی)",
            "recommended_jobs": [],
            "development_points": [],
            "career_path": "خطا در ارتباط با سرویس تحلیلگر."
        }