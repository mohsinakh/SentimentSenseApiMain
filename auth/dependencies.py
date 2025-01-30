from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from db.crud import get_user_by_username
from db.db_config import users_collection
from db.models import User
from auth.utils import verify_password
from config import SECRET_KEY, ALGORITHM
import logging



# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


# Dependency to get the current user
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the JWT token to extract user info
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_info = payload.get("sub")
        if user_info is None:
            raise credentials_exception
        logger.info(f"Token decoded successfully, user_info: {user_info}")
    except JWTError as e:
        logger.error(f"JWT decoding error: {e}")
        raise credentials_exception

    # Check for the user in normal users collection first
    user = users_collection.find_one({"username": user_info})
    if user:
        return User(**user)  # Return normal User Pydantic model
    
    
    # If the user is not found in either collection
    logger.warning(f"User not found in DB: {user_info}")
    raise credentials_exception



