# review.py
# Data repository module encapsulating database queries for the Review model.

from sqlalchemy.orm import Session
from app.models.review import Review
from typing import Optional, List

class ReviewRepository:
    @staticmethod
    def get_by_id(db: Session, review_id: int) -> Optional[Review]:
        """
        Finds a single review by database ID.
        """
        return db.query(Review).filter(Review.id == review_id).first()

    @staticmethod
    def get_by_user_and_movie(db: Session, user_id: int, movie_id: int) -> Optional[Review]:
        """
        Checks if a user has already reviewed a specific movie.
        """
        return db.query(Review).filter(
            Review.user_id == user_id,
            Review.movie_id == movie_id
        ).first()

    @staticmethod
    def get_by_movie(db: Session, movie_id: int) -> List[Review]:
        """
        Gets all reviews for a movie, ordered by creation date descending.
        """
        return db.query(Review).filter(Review.movie_id == movie_id).order_by(Review.created_at.desc()).all()

    @staticmethod
    def get_by_user(db: Session, user_id: int) -> List[Review]:
        """
        Gets all reviews submitted by a specific user.
        """
        return db.query(Review).filter(Review.user_id == user_id).order_by(Review.created_at.desc()).all()

    @staticmethod
    def create(db: Session, review: Review) -> Review:
        """
        Creates and persists a new movie review.
        """
        db.add(review)
        db.commit()
        db.refresh(review)
        return review

    @staticmethod
    def delete(db: Session, review: Review):
        """
        Removes a movie review.
        """
        db.delete(review)
        db.commit()

    @staticmethod
    def commit(db: Session):
        """
        Commits pending session transactions.
        """
        db.commit()
