from fastapi import APIRouter, Depends, HTTPException
from auth.utils import create_access_token, hash_password
from auth.dependencies import get_current_user
from db.crud import authenticate_user,convert_objectid_to_str
from schemas.auth import UserCreate, UserLogin,UserCheckRequest,GoogleLoginRequest,GoogleSignupRequest,ForgotPasswordRequest,ResetPasswordRequest
from db.models import User
from db.db_config import users_collection
import logging,requests
from jose import jwt, JWTError
from email_service.html_email import REGISTER_HTML_BODY,LOGIN_HTML_BODY
from pydantic import EmailStr
from datetime import  timedelta
from email_service.service import send_email
from config import SECRET_KEY, ALGORITHM, BASE_URL,RESET_TOKEN_EXPIRE_MINUTES




router = APIRouter()


# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/register")
async def register_user(user: UserCreate):
    logging.debug(f"Received registration request for username: {user.username} and email: {user.email}")

    # Step 1: Check if the username or email already exists
    existing_user = users_collection.find_one({"$or": [{"email": user.email}, {"username": user.username}]})
    if existing_user:
        if existing_user.get("email") == user.email:
            logging.warning(f"User with email {user.email} already exists.")
            raise HTTPException(status_code=400, detail="Email already registered")
        if existing_user.get("username") == user.username:
            logging.warning(f"User with username {user.username} already exists.")
            raise HTTPException(status_code=400, detail="Username already taken")

    logging.debug(f"No existing user found for email: {user.email} or username: {user.username}. Proceeding to create new user.")

    # Step 2: Hash the password
    try:
        hashed_password = hash_password(user.password)
        logging.debug("Password hashed successfully.")
    except Exception as e:
        logging.error(f"Error while hashing password: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during password hashing")

    # Step 3: Create user in the database
    try:
        new_user = {
            "username": user.username,
            "email": user.email,
            "password": hashed_password,
        }
        users_collection.insert_one(new_user)
        logging.debug(f"User {user.username} registered successfully.")
    except Exception as e:
        logging.error(f"Error while saving user to the database: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while saving user")

    # Step 4: Return success message
    logging.info(f"User {user.username} successfully registered with email {user.email}")
    # Send confirmation email
    try:
        html_body = REGISTER_HTML_BODY.format(username=user.username)
        send_email(
            user.email,
            "Welcome to Our Service!",
            html_body
        )

    except Exception as e:
        logging.error(f"Error while sending mail: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while mailing user")
    

    return {"message": "User registered successfully"}



@router.post("/token")
async def login(request: UserLogin):
    user = authenticate_user(request.credential, request.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username/email or password")
    
    # Generate JWT token
    access_token = create_access_token(data={"sub": user["username"]})
    
    # Include user data in the response
    user_data = {
        "username": user["username"],
        "email": user["email"]
    }

    # Send confirmation email
    try:
        html_body = LOGIN_HTML_BODY.format(username=user_data.get("username"))
        send_email(
            user_data.get("email"),
            "Welcome to Our Service!",
            html_body
        )

    except Exception as e:
        logging.error(f"Error while sending mail: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while mailing user")
    

    return {"access_token": access_token, "token_type": "bearer", "user": user_data}



@router.post("/check-user")
async def check_user(user: UserCheckRequest):
    try:
        if user.token:
            # Google token validation logic here
            response = requests.get(
                'https://www.googleapis.com/oauth2/v1/userinfo',
                params={"access_token": user.token},
                headers={"Accept": "application/json", "Authorization": f'Bearer {user.token}'}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Unable to fetch user info from Google")

            user_info = response.json()

            if not user_info.get("verified_email"):
                raise HTTPException(status_code=400, detail="Email is not verified")
            existing_user = users_collection.find_one({"$or": [{"email": user_info.get("email")}, {"username": user.username}]})
            
            if existing_user:
                if existing_user.get("email") == user_info.get("email"):
                    return {"error": "Email already registered ,Please Log in ..."}
                if existing_user.get("username") == user.username:
                    return {"error": "Username already taken"}
            
        else:
            existing_user = users_collection.find_one({"$or": [{"email": user.email}, {"username": user.username}]})
            if existing_user:
                if existing_user.get("email") == user.email:
                    return {"error": "Email already registered ,Please Log in ..."}
                if existing_user.get("username") == user.username:
                    return {"error": "Username already taken"}
        
        return {"message": "Username and email are available"}

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    


#Google verification routes 
#Google Sign up
@router.post("/google-signup")
async def google_signup(request: GoogleSignupRequest):
    """
    Endpoint to handle Google user signup.
    """
    try:
        # Verify Google token
        logging.info(f'TOKEN : {request.token}')
        response = requests.get(
            'https://www.googleapis.com/oauth2/v1/userinfo',
            params={"access_token": request.token},
            headers={"Accept": "application/json", "Authorization": f'Bearer {request.token}'}
        )

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Unable to fetch user info from Google")


        
        user = response.json()
        user["username"] = request.username
        logger.info(f'user : {user}and email :{user["email"]}')

        if not user["verified_email"]:
            raise HTTPException(status_code=403 , detail="Email Not Verified By Google")
        

    # Step 1: Check if the username or email already exists
        existing_user = users_collection.find_one({"$or": [{"email": user["email"]}, {"username": user["username"]}]})
        if existing_user:
            if existing_user.get("email") == user["email"]:
                # logging.info(f"User with email {user["email"]} already exists.")
                raise HTTPException(status_code=400, detail="Email already registered")
            if existing_user.get("username") == user["username"]:
                # logging.warning(f"User with username {user["username"]} already exists.")
                raise HTTPException(status_code=400, detail="Username already taken")

        logging.info(f"No existing user found for email: {user['email']} or username: {user['username']}. Proceeding to create new user.")

        # Step 2: Hash the password
        try:
            hashed_password = hash_password(request.password)
            logging.info("Password hashed successfully.")
        except Exception as e:
            logging.error(f"Error while hashing password: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during password hashing")

        # Step 3: Create user in the database
        try:
            new_user = {
                "username": user["username"],
                "email": user["email"],
                "password": hashed_password,
            }
            result = users_collection.insert_one(new_user)
            new_user["_id"] = convert_objectid_to_str(result.inserted_id)
            new_user.pop("password", None)
            logging.info(f"User {user['username']} registered successfully.")
        except Exception as e:
            logging.error(f"Error while saving user to the database: {e}")
            raise HTTPException(status_code=500, detail="Internal server error while saving user")


        try:
            html_body = REGISTER_HTML_BODY.format(username=new_user["username"])
            send_email(
                new_user["email"],
                "Welcome to Our Service!",
                html_body
            )
        except Exception as e:
            logging.error(f"Error while sending mail: {e}")
            raise HTTPException(status_code=500, detail="Internal server error while mailing user")
        



        # Generate JWT for the newly created user
        access_token = create_access_token(data={"sub": new_user["username"]})

        return {"message": "User signed up successfully", "access_token": access_token,"user_info":new_user}
    except Exception as e:
        logger.error(f"Google signup failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to sign up with Google")



#Google Login
@router.post("/google-login")
async def google_login(request: GoogleLoginRequest):
    """
    Endpoint to handle Google login for existing users.
    """
    try:
        # Verify Google token
        response = requests.get(
            'https://www.googleapis.com/oauth2/v1/userinfo',
            params={"access_token": request.token},
            headers={"Accept": "application/json", "Authorization": f'Bearer {request.token}'}
        )

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Unable to fetch user info from Google")

        user_info = response.json()

        if not user_info.get("verified_email"):
            raise HTTPException(status_code=400, detail="Email is not verified")

        # Check if the user exists in `users_collection`
        existing_user = users_collection.find_one({"email": user_info["email"]}) 
        if not existing_user:
            raise HTTPException(status_code=404, detail="User does not exist. Please sign up first.")

        
         # Remove the `_id` field
        existing_user.pop("_id", None)

        # Send confirmation email
        try:
            html_body = LOGIN_HTML_BODY.format(username=existing_user.get("username"))
            send_email(
                existing_user.get("email"),
                "Welcome to Our Service!",
                html_body
            )

        except Exception as e:
            logging.error(f"Error while sending mail: {e}")
            raise HTTPException(status_code=500, detail="Internal server error while mailing user")

        # Generate JWT for existing user
        access_token = create_access_token(data={"sub": existing_user["username"]})
        return {"access_token": access_token, "token_type": "bearer", "user_info": existing_user}

    except Exception as e:
        logger.error(f"Google login failed: {e}")
        raise HTTPException(status_code=401, detail="Failed to authenticate with Google")








# Forgot Password Route
@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    email = request.email
    """Send a password reset link to the user's email if the user exists in the database."""
    # Check if the user exists in the database
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail={"message":"No user with this email,Please Log in... "})

    # Generate a reset token
    reset_token = create_access_token(
        data={"sub": email},
        expires_delta=timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    )

    # Create a password reset link
    reset_link = f"{BASE_URL}/reset-password?token={reset_token}"

    # Send the email with the reset link
    subject = "Password Reset Request"
    body = (
        f"Hello,\n\n"
        f"We received a request to reset your password. Click the link below to reset it:\n"
        f"{reset_link}\n\n"
        f"If you did not request this, please ignore this email.\n\n"
        f"Best regards,\n"
        f"The Sentiment Sense Team"
    )
    send_email(email, subject, body)

    return {"message": "Password reset link sent to your email."}




# Reset Password Route
@router.post("/reset-password")
async def reset_password(request:ResetPasswordRequest):
    token= request.token
    new_password = request.new_password
    """Reset the user's password if the reset token is valid."""
    try:
        # Decode the reset token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token.")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")

    # Find the user by email
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Hash the new password
    hashed_password = hash_password(new_password)

    # Update the user's password in the database
    users_collection.update_one({"email": email}, {"$set": {"password": hashed_password}})

    return {"message": "Password has been reset successfully."}

