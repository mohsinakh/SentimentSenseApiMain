from fastapi import APIRouter, Depends,HTTPException
from sentiment.analyzer import get_sentiment
from auth.dependencies import get_current_user
from schemas.sentiment import TextRequest
from db.crud import save_analysis_history,convert_objectid_to_str
from db.models import User
from db.db_config import analysis_history_collection

router = APIRouter()

@router.post("/analyze-sentiment")
async def analyze_sentiment(request: TextRequest, user: User = Depends(get_current_user)):
    """Analyze sentiment of text input."""
    text = request.text
    sentiment = get_sentiment(text)

    # Save analysis history (if user is logged in)
    if user:
        result = save_analysis_history(user.username, "sentiment", {"text": text, "sentiment": sentiment})
        # Adjust the message check to match what save_analysis_history returns
        if result.get("message") == "Analysis already exists":
            return result

    return {"text": text, "sentiment": sentiment}
 




@router.get("/analysis-history")
async def get_analysis_history(user: User = Depends(get_current_user)):
    """Fetch the analysis history of a user."""
    try:
        if user:
            # Fetch the analysis history
            history = analysis_history_collection.find({"user_id": user.username})
            history_list = list(history)  # Convert to list
            
            # Convert ObjectId to string
            history_list = convert_objectid_to_str(history_list)
            
            return {"history": history_list}
        else:
            return {"message": "Not Logged In"}  # No user ID
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch analysis history")

