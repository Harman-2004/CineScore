from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from jose import jwt

from app.database import get_db
from app.services.recommendation import recommendation_service
from app.schemas.movie import MovieResponse
from app.config import settings

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

class RecommendedMovieResponse(MovieResponse):
    recommendation_score: float
    explanation: Dict[str, Any]

@router.get("", response_model=List[RecommendedMovieResponse])
async def get_recommendations(
    request: Request,
    user_id: int = Query(1, description="User ID for personalized recommendations"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of recommendations to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Retrieve personalized movie recommendations tailored to the user's rating profile.
    """
    import logging
    router_logger = logging.getLogger("cinescore.router.recommendations")
    resolved_user_id = user_id
    auth_header = request.headers.get("Authorization")
    router_logger.info(f"[Recommendations API] Query user_id: {user_id}, Auth Header: {auth_header}")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id_str = payload.get("sub")
            if user_id_str:
                resolved_user_id = int(user_id_str)
                router_logger.info(f"[Recommendations API] Resolved user_id from token: {resolved_user_id}")
        except Exception as e:
            router_logger.error(f"[Recommendations API] JWT decode error: {e}")

    try:
        recommendations = recommendation_service.get_personalized_recommendations(
            db=db,
            user_id=resolved_user_id,
            limit=limit
        )
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while compiling recommendations: {str(e)}"
        )

@router.get("/{movie_id}")
async def get_movie_recommendations(
    movie_id: int,
    user_id: int = Query(1, description="User ID for personalized scoring"),
    db: Session = Depends(get_db)
):
    """
    Retrieve hybrid recommendation sliders (Similar Movies, Similar Themes,
    Hidden Gems, and Trending Alternatives) for a specific movie, with explanation metrics.
    """
    try:
        recs = recommendation_service.get_netflix_recommendations(
            db=db,
            target_movie_id=movie_id,
            user_id=user_id
        )
        return recs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating movie recommendations: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[RecommendedMovieResponse])
async def get_user_recommendations(
    user_id: int,
    limit: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Retrieve personalized hybrid recommendations for a specific user.
    """
    try:
        recs = recommendation_service.get_personalized_recommendations(
            db=db,
            user_id=user_id,
            limit=limit
        )
        return recs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving user recommendations: {str(e)}"
        )

@router.post("/{movie_id}/interaction")
async def log_interaction(
    movie_id: int,
    interaction_type: str = Query(..., description="view, search, save, or like"),
    user_id: int = Query(1, description="User ID for logging interaction"),
    db: Session = Depends(get_db)
):
    """
    Log a user interaction (view, search, save, or like) on a movie to dynamically
    update their interest profile weights.
    """
    if interaction_type not in ["view", "search", "save", "like"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid interaction type. Choose from: view, search, save, like."
        )
    try:
        recommendation_service.log_user_interaction(
            db=db,
            user_id=user_id,
            movie_id=movie_id,
            interaction_type=interaction_type
        )
        return {"status": "success", "message": f"Logged interaction '{interaction_type}' for movie ID {movie_id}"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while logging interaction: {str(e)}"
        )
