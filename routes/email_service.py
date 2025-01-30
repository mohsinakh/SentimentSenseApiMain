from fastapi import APIRouter, HTTPException
from email_service.service import send_email,get_email_limit,reset_email_count_if_needed,update_email_limit,auto_reply_email
from schemas.email_service import EmailRequest
from config import EMAIL_USER,MAX_EMAILS_PER_DAY
from datetime import datetime, timedelta


router = APIRouter()



@router.post("/contact")
async def send_email_endpoint(request: EmailRequest):
    # Get or create the email limit for the user
    email_limit = get_email_limit(request.email)

    # Reset email count if needed (i.e., new day)
    reset_email_count_if_needed(email_limit)

    # Check if user has exceeded the daily limit
    if email_limit['emails_sent_today'] >= MAX_EMAILS_PER_DAY:
        raise HTTPException(
            status_code=429,
            detail=f"You've reached the daily limit of {MAX_EMAILS_PER_DAY} emails."
        )
    modified_subject = f"{request.subject} - From: {request.email}"

    # Send the actual email and auto-reply
    send_email(EMAIL_USER, modified_subject, request.body)
    auto_reply_email(request.email)

    # Update the email sent count for the user
    update_email_limit(request.email, email_limit["emails_sent_today"] + 1, datetime.utcnow())


    return {"message": "Email sent and auto-reply delivered successfully"}

