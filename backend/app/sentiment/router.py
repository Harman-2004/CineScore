from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.sentiment.analyzer import sentiment_service

router = APIRouter(prefix="/analysis", tags=["Sentiment Analysis"])

class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000, description="The raw review text or comment to analyze")

class SentimentResponse(BaseModel):
    text: str
    positive_score: float = Field(..., description="Probability score representing positive sentiment (0.0 to 1.0)")
    negative_score: float = Field(..., description="Probability score representing negative sentiment (0.0 to 1.0)")
    final_sentiment: str = Field(..., description="Final sentiment category: POSITIVE, NEUTRAL, or NEGATIVE")
    method: str = Field(..., description="The algorithm engine utilized (hugging_face_transformers or local_lexicon_fallback)")

@router.post("/sentiment", response_model=SentimentResponse)
def analyze_sentiment(payload: SentimentRequest):
    """
    Evaluate the sentiment of a movie review text.
    Returns the positive probability score, negative probability score, and the final sentiment.
    """
    try:
        result = sentiment_service.analyze_text(payload.text)
        return SentimentResponse(
            text=payload.text,
            positive_score=result["positive_score"],
            negative_score=result["negative_score"],
            final_sentiment=result["final_sentiment"],
            method=result["method"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during sentiment evaluation: {str(e)}"
        )
