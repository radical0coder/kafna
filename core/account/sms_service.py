# accounts/sms_service.py

def send_otp_sms(phone_number, code):
    """
    This is a MOCK function. In production, you would replace this
    with an API call to a real SMS gateway like Twilio or Kavenegar.
    """
    print("----------------------------------------------------")
    print(f"--- OTP for: {phone_number} ---")
    print(f"--- CODE: {code} ---")
    print("----------------------------------------------------")
    # This function doesn't need to return anything.