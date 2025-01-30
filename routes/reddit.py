from fastapi import APIRouter, Depends,HTTPException
from typing import Optional
from auth.dependencies import get_current_user
from schemas.reddit import RedditRequest
from db.models import User
from db.crud import save_analysis_history,convert_objectid_to_str
from sentiment.analyzer import get_sentiment
from config import REDDIT_CLIENT_ID,REDDIT_CLIENT_SECRET
import re,praw

router = APIRouter()


# Set up Reddit API client using PRAW
reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent="Sentiment Analysis")



@router.post("/fetch-comments")
async def fetch_reddit_comments(request: RedditRequest, user: Optional[User] = Depends(get_current_user)):
    """Fetch and analyze Reddit post comments. Allows unauthenticated users as well."""
    try:
        # Extract post ID from URL
        post_id = re.search(r"(?:comments\/)([0-9A-Za-z_-]+)", request.post_url).group(1)
        
        # Fetch Reddit post data
        post = reddit.submission(id=post_id)
        post.comments.replace_more(limit=0)
        
        # Get all comments and analyze sentiment
        comments = [{"text": comment.body, 
                     "sentiment": get_sentiment(comment.body), 
                     "user": comment.author.name if comment.author else "Anonymous"} 
                    for comment in post.comments.list()]
        
        # If user is authenticated, save analysis history
        if user:
            result = save_analysis_history(user.username, "reddit", {
                "post_id": post_id,
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
            if result.get("message") == "Analysis already exists":
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
        print(e)  # Log the exception for debugging
        raise HTTPException(status_code=500, detail="Failed to fetch Reddit comments")
