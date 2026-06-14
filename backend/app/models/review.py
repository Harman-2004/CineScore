from sqlalchemy import Column, Integer, ForeignKey, Text, Float, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Review(Base):
    """
    Represents the 'reviews' table, accommodating both user-submitted reviews
    and scraped reviews from external web sources.
    Establishes relationships with users (many-to-one) and movies (many-to-one).
    """
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Float, nullable=False)
    review_text = Column(Text, nullable=False)
    
    # Sentiment Evaluation Fields
    sentiment_score = Column(Float, nullable=True)
    sentiment_label = Column(String, nullable=True)
    aspect_scores_json = Column(Text, nullable=True)
    
    # Scraping Fields
    is_scraped = Column(Boolean, default=False, nullable=False)
    author = Column(String, nullable=True)
    source = Column(String(50), default='Web', nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="reviews")
    movie = relationship("Movie", back_populates="reviews")
