from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ReviewCreate(BaseModel):
    movie_id: int = Field(..., description="TMDb Movie ID to review")
    rating: float = Field(..., ge=1.0, le=10.0, description="Rating from 1.0 to 10.0")
    review_text: str = Field(..., min_length=5, max_length=5000, description="Constructive review text")

class ReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=1.0, le=10.0)
    review_text: Optional[str] = Field(None, min_length=5, max_length=5000)

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    movie_id: int
    rating: float
    review_text: str
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserReviewProfile(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class MovieReviewResponse(ReviewResponse):
    user: UserReviewProfile

    class Config:
        from_attributes = True
