from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
import logging


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
    




# Try to load the classifier with error handling
try:
    # Switching to a zero-shot-classification pipeline or manually specifying model configuration
    classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")
    logger.info("Model loaded successfully")
except Exception as e:
    logger.info(f"Error loading model: {e}")
    classifier = None  # Fallback or additional handling here




# Function to classify emotions
def get_emotions(text: str):
    if classifier is not None:
        text = text[:512]  # Limit input size
        try:
            result = classifier(text)  # No candidate_labels in text-classification
            logging.info(f"Model Output: {result}")

            if isinstance(result, list) and len(result) > 0:
                top_prediction = result[0]  # Take the first result
                return {"label": top_prediction["label"], "score": top_prediction["score"]}
            else:
                return {"error": "No valid classification result"}
        except Exception as e:
            return {"error": f"Error during classification: {e}"}
    else:
        return {"error": "Model not loaded successfully"}