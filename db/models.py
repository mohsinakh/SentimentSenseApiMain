from pydantic import BaseModel, Field,EmailStr
from datetime import datetime
from bson import ObjectId
from typing import Optional
from pydantic import Field

# User model for registration
class User(BaseModel):
    id: str = Field(default_factory=str)  # String version of ObjectId
    username: str
    email: EmailStr
    password: str 

    class Config:
        from_attributes = True

    @classmethod
    def json_encoders(cls):
        return {ObjectId: lambda v: str(v)}  # Convert ObjectId to string
    



# AnalysisHistory model for storing user analysis history
class AnalysisHistory(BaseModel):
    user_id: Optional[str] = None  # User ID can be optional if not logged in
    analysis_type: str  # E.g., 'sentiment', 'youtube', 'reddit'
    analysis_data: dict  # Store the analysis results (text, video URL, etc.)
    timestamp: datetime = Field(default_factory=datetime.utcnow)  # Store the timestamp of the analysis

    class Config:
        from_attributes = True

# EmailLimit model for tracking email limits for users
class EmailLimit(BaseModel):
    email: str  # The user's email address
    emails_sent_today: int = 0  # Number of emails sent today
    last_sent_date: datetime  # The date of the last email sent

    class Config:
        from_attributes = True

    @classmethod
    def json_encoders(cls):
        return {ObjectId: lambda v: str(v)}  # Convert ObjectId to string
