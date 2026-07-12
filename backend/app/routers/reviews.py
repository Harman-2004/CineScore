# reviews.py
# Router module defining endpoints for movie reviews management, routing calls to ReviewService.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse, MovieReviewResponse
from app.auth.router import get_current_user
from app.services.review import ReviewService
from app.repositories import ReviewRepository

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review_in: ReviewCreate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
) -> Review:
    """
    Submit a movie review. Evaluates sentiment and aggregates ratings.
    """
    return ReviewService.create_review(db, current_user.id, review_in)

@router.get("/movie/{movie_id}", response_model=List[MovieReviewResponse])
def get_movie_reviews(movie_id: int, db: Session = Depends(get_db)) -> List[Review]:
    """
    Fetch all reviews posted for a specific movie.
    """
    return ReviewRepository.get_by_movie(db, movie_id)

@router.get("/user/{user_id}", response_model=List[ReviewResponse])
def get_user_reviews(user_id: int, db: Session = Depends(get_db)) -> List[Review]:
    """
    Retrieve all reviews posted by a specific user.
    """
    return ReviewRepository.get_by_user(db, user_id)

@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int, 
    review_in: ReviewUpdate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
) -> Review:
    """
    Update a previously submitted movie review.
    """
    return ReviewService.update_review(db, review_id, current_user.id, review_in)

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Permanently delete a movie review.
    """
    ReviewService.delete_review(db, review_id, current_user.id)
    return None
