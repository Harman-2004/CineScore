from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.auth.router import get_current_user
from app.models.user import User
from app.services.recommendation import recommendation_service
from app.schemas.movie import MovieResponse

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

class RecommendedMovieResponse(MovieResponse):
    recommendation_score: float

@router.get("", response_model=List[RecommendedMovieResponse])
async def get_recommendations(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of recommendations to retrieve"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve personalized movie recommendations tailored to the current user's rating profile.
    Analyzes historical reviews to score new movies by genre correlation and overall quality.
    """
    try:
        recommendations = await recommendation_service.get_recommendations_for_user(
            db=db,
            user_id=current_user.id,
            limit=limit
        )
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while compiling recommendations: {str(e)}"
        )
