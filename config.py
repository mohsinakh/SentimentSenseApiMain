import os
from dotenv import load_dotenv

load_dotenv()

# Security
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your_default_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 400

# Email
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
EMAIL_USER = os.environ.get("EMAIL_USER", "your_email@gmail.com")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "your_email_password")

# Email limit threshold (e.g., max emails per day)
MAX_EMAILS_PER_DAY = 10


RESET_TOKEN_EXPIRE_MINUTES = 60  # Token validity in minutes
BASE_URL = "http://sentiment-sense.netlify.app"

# APIs
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET")
