from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, sentiment, email_service, youtube, reddit
from mangum import Mangum
import httpx,random,asyncio,logging


app = FastAPI()


logger = logging.getLogger(__name__)

# CORS Configuration (Good)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sentiment-sense.netlify.app", "https://sentiment.mohsinabbas.site"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers (Correct)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(sentiment.router, prefix="/sentiment", tags=["sentiment"])
app.include_router(email_service.router, prefix="/email", tags=["email"])
app.include_router(youtube.router, prefix="/youtube", tags=["youtube"])
app.include_router(reddit.router, prefix="/reddit", tags=["reddit"])

# Self-pinger Improvement
async def self_pinger():
    """Keep Render instance active with random ping interval between 4 and 5 minutes"""
    while True:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.get("https://sentimentsense-ttjy.onrender.com/health")
        except Exception as e:
            logger.error(f"Ping failed: {str(e)}")
        # Random sleep time between 240 and 300 seconds (4 to 5 minutes)
        await asyncio.sleep(random.randint(200, 299))

@app.on_event("startup")
async def startup_event():
    # Create dedicated task instead of BackgroundTasks
    asyncio.create_task(self_pinger())

@app.get("/")
def read_root():
    return {"message": "Welcome to Sentiment Sense API"}

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}

# Mangum handler (Must be last line)
handler = Mangum(app)
