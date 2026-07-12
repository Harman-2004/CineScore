# rating.py
# Data repository module encapsulating database queries for the Rating model.

from sqlalchemy.orm import Session
from app.models.rating import Rating
from typing import Optional

class RatingRepository:
    @staticmethod
    def get_by_movie_id(db: Session, movie_id: int) -> Optional[Rating]:
        """
        Retrieves rating statistics (sentiment average, composite score) for a movie.
        """
        return db.query(Rating).filter(Rating.movie_id == movie_id).first()

    @staticmethod
    def create(db: Session, rating: Rating) -> Rating:
        """
        Persists a new movie rating metadata record.
        """
        db.add(rating)
        db.commit()
        db.refresh(rating)
        return rating

    @staticmethod
    def commit(db: Session):
        """
        Commits pending session transactions.
        """
        db.commit()
