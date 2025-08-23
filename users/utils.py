import os
from django.core.mail import send_mail

def send_verification_email(user, otp_code):
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp_code}. It is valid for 5 minutes.'
    html_message = f"""
    <!doctype html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta charset="utf-8">
  <meta name="x-apple-disable-message-reformatting">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Verify your email</title>
</head>
<body style="margin:0; padding:0; background:#f6f4ff;" class="bg">
  <!-- Wrapper -->
  <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="background:#f6f4ff;">
    <tr>
      <td align="center" style="padding:24px;">
        <!-- Container -->
        <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="max-width:600px;">
          <!-- Header -->
          <tr>
            <td
              style="
                padding:28px 24px;
                border-radius:16px 16px 0 0;
                background: linear-gradient(90deg,#6d28d9,#2563eb);
                color:#ffffff; font-family:Inter,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
              "
            >
              <h1 style="margin:0; font-size:22px; line-height:1.3; font-weight:700;">Verify your email</h1>
              <p style="margin:6px 0 0; font-size:14px; opacity:.92;">
                Use the code below to finish signing in.
              </p>
            </td>
          </tr>

          <!-- Card -->
          <tr>
            <td class="card" style="background:#ffffff; padding:24px; border:1px solid #e9e4ff; border-top:none; border-radius:0 0 16px 16px; font-family:Inter,Segoe UI,Roboto,Helvetica,Arial,sans-serif;">
              
              <!-- Code block -->
              <p class="text" style="margin:0 0 8px; font-size:14px; color:#1f2340;">
                Your verification code:
              </p>
              <div
                class="code"
                style="
                  display:inline-block;
                  letter-spacing:6px;
                  font-weight:800;
                  font-size:28px;
                  padding:14px 18px;
                  border-radius:12px;
                  border:1px solid #e9e4ff;
                  background:#faf9ff;
                  color:#1f2340;
                "
              >
                {otp_code}
              </div>





              <p class="muted" style="margin:16px 0 0; font-size:12px; color:#5b5f7a;">
                This code expires in 5 minutes. If you didn’t request it, you can safely ignore this email.
              </p>


              


              <hr style="border:none; border-top:1px solid #eeeafd; margin:20px 0;">
              <p class="muted" style="margin:0; font-size:12px; color:#5b5f7a;">
                Thanks,<br>Thapar Drone Challenge Team
              </p>
            </td>
          </tr>

          <tr><td style="height:24px;"></td></tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
    from_email = os.getenv("GMAIL_MAIL")
    recipient_list = [user.email]

    try:
        send_mail(subject, message=message, html_message=html_message, from_email=from_email, recipient_list=recipient_list)
        return True, None
    except Exception as e:
        print(f"Error sending email: {e}")
        return False, str(e)

