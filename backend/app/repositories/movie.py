# movie.py
# Data repository module encapsulating database queries for the Movie model.

from sqlalchemy.orm import Session
from app.models.movie import Movie
from typing import Optional, List

class MovieRepository:
    @staticmethod
    def get_by_id(db: Session, movie_id: int) -> Optional[Movie]:
        """
        Retrieves movie metadata by TMDb ID.
        """
        return db.query(Movie).filter(Movie.id == movie_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Movie]:
        """
        Retrieves a paginated list of movies.
        """
        return db.query(Movie).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_ids(db: Session, movie_ids: List[int]) -> List[Movie]:
        """
        Retrieves movie records corresponding to a list of IDs.
        """
        return db.query(Movie).filter(Movie.id.in_(movie_ids)).all()

    @staticmethod
    def create(db: Session, movie: Movie) -> Movie:
        """
        Persists a new movie metadata record.
        """
        db.add(movie)
        db.commit()
        db.refresh(movie)
        return movie

    @staticmethod
    def commit(db: Session):
        """
        Commits any pending transaction changes.
        """
        db.commit()
