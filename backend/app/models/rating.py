from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Rating(Base):
    """
    Represents the 'ratings' table, storing consolidated and aggregated scores,
    supporting the hybrid weighted composite formula:
    FinalScore = 0.4(IMDb) + 0.2(TMDb) + 0.1(Metacritic) + 0.3(NLPReviewScore)
    """
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    aggregate_score = Column(Float, default=0.0)      # Mapped hybrid FinalScore
    imdb_score = Column(Float, nullable=True)          # IMDb score
    tmdb_score = Column(Float, nullable=True)          # TMDb score
    metacritic_score = Column(Float, nullable=True)    # Metacritic score (out of 10)
    sentiment_avg = Column(Float, default=0.0)        # Review sentiment average (-1.0 to 1.0)
    rating_count = Column(Integer, default=0)          # Number of reviews
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # One-to-one relationship with Movie
    movie = relationship("Movie", back_populates="rating")
