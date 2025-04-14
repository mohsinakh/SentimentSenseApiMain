from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from auth.dependencies import get_current_user
from schemas.reddit import RedditRequest
from db.models import User
from db.crud import save_analysis_history, convert_objectid_to_str
from sentiment.analyzer import get_emotions
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET
import re, asyncpraw, logging

router = APIRouter()

logger = logging.getLogger(__name__)

# Set up Reddit API client using AsyncPRAW
reddit = asyncpraw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent="Sentiment Analysis"
)

@router.post("/fetch-comments")
async def fetch_reddit_comments(request: RedditRequest, user: Optional[User] = Depends(get_current_user)):
    """Fetch and analyze Reddit post comments. Allows unauthenticated users as well."""
    try:
        # Extract post ID from URL
        post_id = re.search(r"(?:comments\/)([0-9A-Za-z_-]+)", request.post_url).group(1)
        
        # 🔥 Await the coroutine to get the actual post object
        post = await reddit.submission(id=post_id)
        
        # ✅ Fetch necessary attributes explicitly
        await post.load()  # 🔥 Ensures we get all submission details
        post_author = post.author.name if post.author else "Anonymous"
        post_content = post.selftext if hasattr(post, "selftext") else "No content available"
        
        # Fetch and await comments
        post_comments = await post.comments()
        await post.comments.replace_more(limit=0)  # 🔥 Ensure this is awaited to get the comments correctly
        post_comments = post.comments.list()  # Now this is a list of comment objects

        # Get all comments and analyze sentiment
        comments = []
        for comment in post_comments:
            sentiment_result = await get_emotions(comment.body)  # Ensure this is awaited
            sentiment_label = sentiment_result.get("label") if sentiment_result else "unknown"
            comment_data = {
                "text": comment.body,
                "sentiment": sentiment_label,
                "user": comment.author.name if comment.author else "Anonymous"
            }
            comments.append(comment_data)

        # If user is authenticated, save analysis history
        if user:
            result = save_analysis_history(user.username, "reddit", {
                "post_id": post_id,
                "post": {
                    "title": post.title,
                    "author": post_author if post_author else "Deleted",
                    "content": post_content,
                    "url": post.url,
                    "upvotes": post.ups,
                    "downvotes": post.downs,
                    "comments_count": len(post_comments)
                },
                "comments": comments
            })
            
            # Check if result is a list or dict and handle accordingly
            if isinstance(result, list):
                logging.error(f"Result is a list: {result}")
                raise HTTPException(status_code=500, detail="Analysis already exists")
            elif isinstance(result, dict) and result.get("message") == "Analysis already exists":
                return result

        # Convert ObjectId to string in the response
        return convert_objectid_to_str({
            "post": {
                "title": post.title, 
                "author": post.author.name if post.author else "Deleted", 
                "content": post.selftext,
                "url": post.url,
                "upvotes": post.ups,
                "downvotes": post.downs,
                "comments_count": len(post.comments)
            },
            "comments": comments
        })
    except Exception as e:
        logging.error(f"Error fetching Reddit comments: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch Reddit comments")
