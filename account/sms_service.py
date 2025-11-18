# accounts/sms_service.py
import requests
import json
from decouple import config

# 1. Load your secret credentials from the .env file
API_KEY = config('SMS_IR_API_KEY')
TEMPLATE_ID = config('SMS_IR_TEMPLATE_ID')

# 2. Define the API endpoint
API_URL = "https://api.sms.ir/v1/send/verify"

def send_otp_sms(phone_number, code):
    """
    Sends a real OTP SMS using the sms.ir verification API.
    """
    # 3. Prepare the data payload dynamically
    # This structure matches the API documentation.
    payload = {
        "mobile": phone_number,
        "templateId": TEMPLATE_ID,
        "parameters": [
            {
                "name": "CODE",  # The parameter name must match what you defined in your sms.ir template
                "value": code
            }
        ]
    }

    # 4. Prepare the required headers
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'text/plain',
        'x-api-key': API_KEY
    }

    try:
        # 5. Make the API call using the 'requests' library
        response = requests.post(API_URL, json=payload, headers=headers)

        # 6. Check for errors and log the response for debugging
        if response.status_code == 200:
            print(f"Successfully sent OTP to {phone_number}. Response: {response.text}")
        else:
            print(f"Error sending OTP to {phone_number}. Status: {response.status_code}, Response: {response.text}")
    
    except Exception as e:
        print(f"An exception occurred while trying to send SMS: {e}")