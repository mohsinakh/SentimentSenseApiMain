from fastapi import  HTTPException
from db.models import User, AnalysisHistory 
from bson import ObjectId
from db.db_config import users_collection,analysis_history_collection
from auth.utils import verify_password
import logging


# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




def get_user_by_username(username: str):
    return users_collection.find_one({"username": username})



def save_analysis_history(user_id: str, analysis_type: str, analysis_data: dict):
    """Save analysis history to the database or return existing analysis."""
    existing_analysis = analysis_exists(user_id, analysis_type, analysis_data)
    if existing_analysis:
        logger.info(f"Analysis already exists for user {user_id} - {analysis_type}")
        # Convert ObjectId to string before returning
        existing_analysis = convert_objectid_to_str(existing_analysis)
        return existing_analysis

    try:
        # Create the analysis entry
        analysis_entry = AnalysisHistory(
            user_id=user_id,
            analysis_type=analysis_type,
            analysis_data=analysis_data
        )
        
        # Insert the entry into the collection
        insert_result = analysis_history_collection.insert_one(analysis_entry.dict())
        logger.info(f"Analysis history saved for user {user_id} - {analysis_type}")

        # Convert ObjectId to string after insertion
        analysis_entry_dict = analysis_entry.dict()
        analysis_entry_dict['_id'] = str(insert_result.inserted_id)
        
        return {"message": "Analysis saved successfully", "analysis_data": convert_objectid_to_str(analysis_entry_dict)}
    except Exception as e:
        logger.error(f"Error saving analysis history: {e}")
        raise HTTPException(status_code=500, detail="Error saving analysis history")
    





def authenticate_user(credential: str, password: str):
    """Authenticate a user by username or email and password."""
    user = users_collection.find_one(
        {"$or": [{"username": credential}, {"email": credential}]}
    )
    if not user or not verify_password(password, str(user["password"])):
        return None
    return user



def convert_objectid_to_str(data):
    """Recursively convert all ObjectId fields in the data to strings."""
    if isinstance(data, dict):
        return {key: convert_objectid_to_str(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    return data



# Helper function to check if analysis already exists
def analysis_exists(user_id: str, analysis_type: str, analysis_data: dict):
    """Check if the analysis already exists for the user and return the data."""
    query = {"user_id": user_id, "analysis_type": analysis_type}

    if analysis_type == "youtube":
        query["analysis_data.video_id"] = analysis_data.get("video_id")
    elif analysis_type == "reddit":
        query["analysis_data.post_id"] = analysis_data.get("post_id")
    elif analysis_type == "sentiment":
        query["analysis_data.text"] = analysis_data.get("text")

    existing_analysis = analysis_history_collection.find_one(query)
    if existing_analysis:
        return convert_objectid_to_str(existing_analysis)
    return None
