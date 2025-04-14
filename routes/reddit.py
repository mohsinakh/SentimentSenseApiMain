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


@router.post("/fetch-comments")
async def fetch_reddit_comments(request: RedditRequest, user: Optional[User] = Depends(get_current_user)):
    """Fetch and analyze Reddit post comments. Allows unauthenticated users as well."""
    try:
        # 👇 Create Reddit client INSIDE the async request handler
        reddit = asyncpraw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent="Sentiment Analysis"
        )

        post_id_match = re.search(r"(?:comments\/)([0-9A-Za-z_-]+)", request.post_url)
        if not post_id_match:
            raise HTTPException(status_code=400, detail="Invalid Reddit post URL")

        post_id = post_id_match.group(1)
        submission = await reddit.submission(id=post_id)
        await submission.load()

        post_author = submission.author.name if submission.author else "Anonymous"
        post_content = submission.selftext if hasattr(submission, "selftext") else "No content available"

        await submission.comments.replace_more(limit=0)
        post_comments = submission.comments.list()

        comments = []
        for comment in post_comments:
            sentiment_result = await get_emotions(comment.body)
            sentiment_label = sentiment_result.get("label", "unknown")
            comment_data = {
                "text": comment.body,
                "sentiment": sentiment_label,
                "user": comment.author.name if comment.author else "Anonymous"
            }
            comments.append(comment_data)

        # Save history if authenticated
        if user:
            result = save_analysis_history(user.username, "reddit", {
                "post_id": post_id,
                "post": {
                    "title": submission.title,
                    "author": post_author,
                    "content": post_content,
                    "url": submission.url,
                    "upvotes": submission.ups,
                    "downvotes": submission.downs,
                    "comments_count": len(post_comments)
                },
                "comments": comments
            })

            if isinstance(result, dict) and result.get("message") == "Analysis already exists":
                return result

        return convert_objectid_to_str({
            "post": {
                "title": submission.title,
                "author": post_author,
                "content": post_content,
                "url": submission.url,
                "upvotes": submission.ups,
                "downvotes": submission.downs,
                "comments_count": len(post_comments)
            },
            "comments": comments
        })

    except Exception as e:
        logger.error(f"Error fetching Reddit comments: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch Reddit comments")
