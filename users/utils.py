import os
from django.core.mail import send_mail

def send_verification_email(user, otp_code):
    subject = 'Your OTP Code'
    html_message = f'Your OTP code is {otp_code}. It is valid for 5 minutes.'
    from_email = os.getenv("GMAIL_MAIL")
    recipient_list = [user.email]

    try:
        send_mail(subject, message=html_message, html_message=html_message, from_email=from_email, recipient_list=recipient_list)
        return True, None
    except Exception as e:
        print(f"Error sending email: {e}")
        return False, str(e)

