from fastapi import APIRouter, Depends,HTTPException
from auth.dependencies import get_current_user
from schemas.youtube import VideoRequest
from db.models import User
from googleapiclient.discovery import build
from config import YOUTUBE_API_KEY
from sentiment.analyzer import get_emotions
from db.crud import save_analysis_history
import re,logging

router = APIRouter()



# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Set up YouTube Data API with your API key
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY,cache_discovery=False)

@router.post("/fetch-comments")
async def fetch_comments(request: VideoRequest, user: User = Depends(get_current_user)):
    """Fetch and analyze YouTube comments."""
    try:
        video_id = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", request.video_url).group(1)
        response = youtube.commentThreads().list(part="snippet", videoId=video_id, maxResults=10000, textFormat="plainText").execute()

        # Ensure all async operations are awaited properly
        comments = []
        for item in response.get("items", []):
            text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            sentiment_result = await get_emotions(text)
            sentiment_label = sentiment_result.get("label") if sentiment_result else "unknown"
            comments.append({
                "text": text,
                "sentiment": sentiment_label,
                "username": item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
            })

        # Save analysis history only if not already saved
        if user:
            result = save_analysis_history(user.username, "youtube", {"video_id": video_id, "comments": comments})
            if result.get("message") == "Analysis already saved.":
                return result

        return {"video_id": video_id, "comments": comments}
    except Exception as e:
        logger.error(f"Error fetching or processing comments: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch comments")
