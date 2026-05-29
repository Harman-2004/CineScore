from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.review import Review
from app.models.user import User
from app.models.movie import Movie
from app.models.rating import Rating
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse, MovieReviewResponse
from app.auth.router import get_current_user
from app.sentiment.analyzer import sentiment_service

router = APIRouter(prefix="/reviews", tags=["Reviews"])

def _update_rating_statistics(db: Session, movie_id: int):
    """
    Recalculates review count and sentiment averages in the 'ratings' table
    whenever reviews are added, updated, or deleted.
    Leverages the Hybrid Rating Formula to compute the unified aggregate score.
    """
    from app.routers.movies import _calculate_hybrid_score
    
    all_reviews = db.query(Review).filter(Review.movie_id == movie_id).all()
    count = len(all_reviews)
    
    sentiments = [r.sentiment_score for r in all_reviews if r.sentiment_score is not None]
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
    
    db_rating = db.query(Rating).filter(Rating.movie_id == movie_id).first()
    movie_record = db.query(Movie).filter(Movie.id == movie_id).first()
    
    tmdb_val = movie_record.vote_average if movie_record else 0.0
    imdb_val = movie_record.imdb_rating if movie_record else None
    metacritic_val = movie_record.metacritic_score if movie_record else None
    
    aggregate = _calculate_hybrid_score(imdb_val, tmdb_val, metacritic_val, avg_sentiment)
    
    if not db_rating:
        db_rating = Rating(
            movie_id=movie_id,
            imdb_score=imdb_val,
            tmdb_score=tmdb_val,
            metacritic_score=metacritic_val,
            aggregate_score=aggregate,
            sentiment_avg=round(float(avg_sentiment), 4),
            rating_count=count
        )
        db.add(db_rating)
    else:
        db_rating.imdb_score = imdb_val
        db_rating.tmdb_score = tmdb_val
        db_rating.metacritic_score = metacritic_val
        db_rating.sentiment_avg = round(float(avg_sentiment), 4)
        db_rating.rating_count = count
        db_rating.aggregate_score = aggregate
        
    db.commit()

@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(review_in: ReviewCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Create a new movie review.
    Automatically invokes the Hugging Face sentiment engine and updates statistics.
    """
    existing_review = db.query(Review).filter(
        Review.user_id == current_user.id,
        Review.movie_id == review_in.movie_id
    ).first()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already submitted a review for this movie. Use PUT to edit it."
        )

    # Perform sentiment analysis
    sentiment = sentiment_service.analyze_text(review_in.review_text)
    polarity = sentiment["positive_score"] - sentiment["negative_score"]
    
    db_review = Review(
        user_id=current_user.id,
        movie_id=review_in.movie_id,
        rating=review_in.rating,
        review_text=review_in.review_text,
        sentiment_score=round(float(polarity), 4),
        sentiment_label=sentiment["final_sentiment"]
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    try:
        _update_rating_statistics(db, review_in.movie_id)
    except Exception:
        pass
        
    return db_review

@router.get("/movie/{movie_id}", response_model=List[MovieReviewResponse])
def get_movie_reviews(movie_id: int, db: Session = Depends(get_db)):
    """
    Fetch all user reviews for a specific movie, including reviewer profile information.
    """
    reviews = db.query(Review).filter(Review.movie_id == movie_id).order_by(Review.created_at.desc()).all()
    return reviews

@router.get("/user/{user_id}", response_model=List[ReviewResponse])
def get_user_reviews(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all reviews posted by a specific user.
    """
    reviews = db.query(Review).filter(Review.user_id == user_id).order_by(Review.created_at.desc()).all()
    return reviews

@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(review_id: int, review_in: ReviewUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Update an existing review's rating and description.
    Recalculates sentiment score on edits and updates ratings statistics.
    """
    db_review = db.query(Review).filter(Review.id == review_id).first()
    if not db_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
        
    if db_review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this review"
        )
        
    if review_in.rating is not None:
        db_review.rating = review_in.rating
        
    if review_in.review_text is not None:
        db_review.review_text = review_in.review_text
        sentiment = sentiment_service.analyze_text(review_in.review_text)
        polarity = sentiment["positive_score"] - sentiment["negative_score"]
        db_review.sentiment_score = round(float(polarity), 4)
        db_review.sentiment_label = sentiment["final_sentiment"]
        
    db.commit()
    db.refresh(db_review)
    
    try:
        _update_rating_statistics(db, db_review.movie_id)
    except Exception:
        pass
        
    return db_review

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Permanently delete a movie review.
    """
    db_review = db.query(Review).filter(Review.id == review_id).first()
    if not db_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
        
    if db_review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this review"
        )
        
    movie_id = db_review.movie_id
    db.delete(db_review)
    db.commit()
    
    try:
        _update_rating_statistics(db, movie_id)
    except Exception:
        pass
        
    return None
