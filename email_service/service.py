import smtplib,logging
from datetime import datetime, timedelta
from fastapi import HTTPException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import SMTP_SERVER, SMTP_PORT, EMAIL_USER, EMAIL_PASSWORD
from db.db_config import email_limit_collection
from db.models import EmailLimit




# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)





# Helper functions for email limits
def get_email_limit(email: str):
    """Get the current email limit for the user."""
    email_limit = email_limit_collection.find_one({"email": email})
    if email_limit:
        return email_limit
    # If no entry, create a new one for the user
    email_limit = EmailLimit(email=email, emails_sent_today=0, last_sent_date=datetime.utcnow())
    email_limit_dict = email_limit.dict()  # Convert to dictionary
    email_limit_collection.insert_one(email_limit_dict)
    return email_limit_dict

def update_email_limit(email: str, emails_sent_today: int, last_sent_date: datetime):
    """Update the email limit document in the database."""
    email_limit_collection.update_one(
        {"email": email},
        {"$set": {"emails_sent_today": emails_sent_today, "last_sent_date": last_sent_date}},
    )

def reset_email_count_if_needed(email_limit: dict):
    # Assuming email_limit is a dictionary
    if 'last_sent_date' in email_limit and email_limit['last_sent_date'].date() < datetime.utcnow().date():
        logger.debug("email is to be reset")
        # Reset email count logic here
        email_limit['emails_sent_today'] = 0
        # Update the database or email limit logic here
        email_limit_collection.update_one(
            {"email": email_limit['email']},
            {"$set": {"emails_sent_today": email_limit['emails_sent_today'], "last_sent_date": datetime.utcnow()}}
        )

def send_email(to_email: str, subject: str, body: str, is_html: bool = True):
    try:
        # Create the message container
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject

        # Attach the body with HTML content
        if is_html:
            msg.attach(MIMEText(body, 'html'))  # HTML body
        else:
            msg.attach(MIMEText(body, 'plain'))  # Plain text body

        # Send the email using the SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(EMAIL_USER, to_email, text)

        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise Exception("Failed to send email")
    


def auto_reply_email(to_email: str):
    subject = "Thank you for contacting Sentiment Sense"
    body = (
        "Hello,\n\n"
        "Thank you for reaching out to Sentiment Sense. Your query is important to us, and we will respond as soon as possible.\n\n"
        "Best regards,\n"
        "The Sentiment Sense Team"
    )
    send_email(to_email, subject, body)

