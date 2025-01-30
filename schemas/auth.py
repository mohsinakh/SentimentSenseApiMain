from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    credential: str  # Can be username or email
    password: str 

class Token(BaseModel):
    access_token: str
    token_type: str


class UserCheckRequest(BaseModel):
    username: str 
    email: str = None
    token: str = None



class GoogleLoginRequest(BaseModel):
    token: str

class GoogleSignupRequest(BaseModel):
    token: str
    username:str
    password:str


# Define a request model
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


# Define a request model
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str