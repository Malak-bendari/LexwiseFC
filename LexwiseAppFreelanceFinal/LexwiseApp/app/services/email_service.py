import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        # Disable real email to avoid errors
        self.enabled = False
        print("📧 Email service is DISABLED (no emails will be sent)")
    
    def send_welcome_email(self, to_email, username):
        print(f"[EMAIL DEBUG] Would send welcome email to {to_email}")
        return True
    
    def send_password_reset(self, to_email, reset_token, username):
        print(f"[EMAIL DEBUG] Would send password reset to {to_email}")
        print(f"[EMAIL DEBUG] Reset link: http://127.0.0.1:5000/reset-password?token={reset_token}")
        return True
    
    def send_match_notification(self, to_email, from_name, match_score, project_title):
        print(f"[EMAIL DEBUG] Would send match notification to {to_email}")
        return True
    
    def send_match_accepted(self, to_email, investor_name, project_title):
        print(f"[EMAIL DEBUG] Would send match accepted to {to_email}")
        return True

# Create singleton instance
email_service = EmailService()