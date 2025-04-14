import httpx
import os
import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


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



HUGGINGFACE_API_TOKEN = os.environ.get("HUGGINGFACE_API_TOKEN")  # keep token in .env
HUGGINGFACE_API_URL = os.environ.get("HUGGINGFACE_API_URL")  # keep token in .env


async def get_emotions(text: str):
    api_url = HUGGINGFACE_API_URL
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(api_url, headers=headers, json={"inputs": text[:512]})
            response.raise_for_status()
            results = response.json()

            # Debugging: print the structure of results
            logger.info(f"Response from Hugging Face API: {results}")

            # Check if the response contains a list and access the first list in it
            if isinstance(results, list) and results:
                emotions_list = results[0]  # This accesses the first list of emotions
                top_prediction = max(emotions_list, key=lambda x: x["score"])
                return {"label": top_prediction["label"], "score": top_prediction["score"]}
            else:
                return {"error": "No valid classification result"}

        except httpx.RequestError as e:
            return {"error": f"Hugging Face API request failed: {e}"}