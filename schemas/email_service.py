from pydantic import BaseModel, EmailStr

# Request models
class EmailRequest(BaseModel):
    email: EmailStr
    subject: str
    body: str
    