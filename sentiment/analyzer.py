from transformers import pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging

logger = logging.getLogger(__name__)
analyzer = SentimentIntensityAnalyzer()

# Initialize classifier as None globally
classifier = None

def get_sentiment(text: str) -> str:
    sentiment_score = analyzer.polarity_scores(text)
    compound_score = sentiment_score['compound']
    
    if compound_score >= 0.05:
        return "positive"
    elif compound_score <= -0.05:
        return "negative"
    else:
        return "neutral"

def get_emotions(text: str):
    global classifier

    # Lazy-load on first use
    if classifier is None:
        try:
            classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base"
            )
            logger.info("Model loaded successfully on demand.")
        except Exception as e:
            logger.error(f"Failed to load model on demand: {e}")
            return {"error": "Model could not be loaded."}

    try:
        text = text[:512]
        result = classifier(text)
        logger.info(f"Model Output: {result}")
        if isinstance(result, list) and result:
            top_prediction = result[0]
            return {"label": top_prediction["label"], "score": top_prediction["score"]}
        else:
            return {"error": "No valid classification result"}
    except Exception as e:
        return {"error": f"Error during classification: {e}"}
