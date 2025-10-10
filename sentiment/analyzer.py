# import httpx
# import os
import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os
from huggingface_hub import InferenceClient

HF_TOKEN = os.environ.get("HF_TOKEN")  # store token as env variable
if not HF_TOKEN:
    logger.error("❌ HF_TOKEN environment variable not set")
client = InferenceClient(provider="hf-inference", api_key=HF_TOKEN)

HF_MODEL = "j-hartmann/emotion-english-distilroberta-base"


logger = logging.getLogger(__name__)
analyzer = SentimentIntensityAnalyzer()



def get_sentiment(text: str) -> str:
    sentiment_score = analyzer.polarity_scores(text)
    compound_score = sentiment_score['compound']
    
    if compound_score >= 0.05:
        return "positive"
    elif compound_score <= -0.05:
        return "negative"
    else:
        return "neutral"


# Load the model pipeline once (globally for efficiency)
# emotion_classifier = None




async def get_emotions(text: str):
    try:
        # HF Inference call (first 512 chars for safety)
        result = client.text_classification(text[:512], model=HF_MODEL)
        # result is a list of dicts: [{"label": "joy", "score": 0.95}, ...]
        if result:
            top_prediction = max(result, key=lambda x: x["score"])
            return {"label": top_prediction["label"], "score": top_prediction["score"]}
        else:
            return {"error": "No valid classification result"}
    except Exception as e:
        return {"error": f"Hugging Face inference failed: {e}"}