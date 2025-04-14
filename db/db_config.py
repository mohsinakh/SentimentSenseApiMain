# db/db_config.py
import logging
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get MongoDB URL from environment variables
MONGO_URL = os.environ.get("MONGO_URL")

if not MONGO_URL:
    raise ValueError("MONGO_URL environment variable is not set!")

# MongoDB connection with SSL context
client = MongoClient(MONGO_URL, tls=True, tlsDisableOCSPEndpointCheck=True)
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use lazy initialization
_client = None

# Establish connection to MongoDB
try:
    db = client["sentiment_analysis"]
    users_collection = db["users"]
    google_users_collection = db["google_users"]
    analysis_history_collection = db["analysis_history"]  # New collection for analysis history
    email_limit_collection = db["email_limit"]
    logger.info("MongoDB connection established successfully")
except Exception as e:
    logger.error(f"Error connecting to MongoDB: {e}")
    raise

def get_database():
    return db
