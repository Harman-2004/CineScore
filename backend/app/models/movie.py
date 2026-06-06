from sqlalchemy import Column, Integer, String, Text, Float, JSON, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Movie(Base):
    """
    Represents the 'movies' table storing movie metadata, including IMDb and Metacritic.
    """
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)  # Matches TMDb Movie ID
    imdb_id = Column(String, nullable=True, index=True)  # Local cache index for official OMDb details
    title = Column(String, nullable=False, index=True)
    overview = Column(Text, nullable=True)
    poster_path = Column(String, nullable=True)
    release_date = Column(String, nullable=True)
    genres = Column(JSON, nullable=True)  # e.g., [{"id": 28, "name": "Action"}]
    runtime = Column(Integer, nullable=True)  # Runtime in minutes
    vote_average = Column(Float, default=0.0)
    imdb_rating = Column(Float, nullable=True)
    metacritic_score = Column(Float, nullable=True)  # Metacritic score column (out of 10)
    is_details_loaded = Column(Boolean, default=False, nullable=False)
    omdb_status = Column(String, nullable=True)
    omdb_error = Column(String, nullable=True)
    media_type = Column(String, nullable=True)
    rating_source = Column(String, nullable=True)
    cached_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    reviews = relationship("Review", back_populates="movie", cascade="all, delete-orphan")
    rating = relationship("Rating", back_populates="movie", uselist=False, cascade="all, delete-orphan")
