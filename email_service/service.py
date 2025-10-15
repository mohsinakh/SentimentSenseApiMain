import logging
from datetime import datetime
from fastapi import HTTPException
import resend
from db.db_config import email_limit_collection
from db.models import EmailLimit
from config import EMAIL_USER

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set your Resend API key
import os
resend.api_key = os.environ["RESEND_API_KEY"]


# Helper functions for email limits
def get_email_limit(email: str):
    email_limit = email_limit_collection.find_one({"email": email})
    if email_limit:
        return email_limit
    # If no entry, create a new one
    email_limit = EmailLimit(email=email, emails_sent_today=0, last_sent_date=datetime.utcnow())
    email_limit_dict = email_limit.dict()
    email_limit_collection.insert_one(email_limit_dict)
    return email_limit_dict

def update_email_limit(email: str, emails_sent_today: int, last_sent_date: datetime):
    email_limit_collection.update_one(
        {"email": email},
        {"$set": {"emails_sent_today": emails_sent_today, "last_sent_date": last_sent_date}},
    )

def reset_email_count_if_needed(email_limit: dict):
    if 'last_sent_date' in email_limit and email_limit['last_sent_date'].date() < datetime.utcnow().date():
        logger.debug("Resetting email count for user")
        email_limit['emails_sent_today'] = 0
        email_limit_collection.update_one(
            {"email": email_limit['email']},
            {"$set": {"emails_sent_today": email_limit['emails_sent_today'], "last_sent_date": datetime.utcnow()}}
        )

# Function to send email via Resend
def send_email(to_email: str, subject: str, body: str, is_html: bool = True):
    try:
        reset_email_count_if_needed(get_email_limit(to_email))
        
        response = resend.Emails.send({
            "from": EMAIL_USER,
            "to": to_email,
            "subject": subject,
            "html": body if is_html else None,
            "text": None if is_html else body
        })

        # Update email limit
        email_limit = get_email_limit(to_email)
        email_limit['emails_sent_today'] += 1
        email_limit['last_sent_date'] = datetime.utcnow()
        update_email_limit(to_email, email_limit['emails_sent_today'], email_limit['last_sent_date'])

        logger.info(f"Email sent to {to_email}, response id: {response['id']}")
    except Exception as e:
        logger.error(f"Failed to send email via Resend: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email")

# Auto-reply email
def auto_reply_email(to_email: str):
    subject = "Thank you for contacting Sentiment Sense"
    body = (
        "Hello,<br><br>"
        "Thank you for reaching out to Sentiment Sense. Your query is important to us, and we will respond as soon as possible.<br><br>"
        "Best regards,<br>"
        "The Sentiment Sense Team"
    )
    send_email(to_email, subject, body)
