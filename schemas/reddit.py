from pydantic import BaseModel

class RedditRequest(BaseModel):
    post_url: str