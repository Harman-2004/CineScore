from sqlalchemy import Column, Integer, String, Text, Float, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class MovieEmbedding(Base):
    """
    Stores 384-dimensional Sentence Transformer embeddings (all-MiniLM-L6-v2)
    for movies to enable semantic search and similarity matching.
    """
    __tablename__ = "movie_embeddings"

    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    overview_embedding = Column(JSON, nullable=True)  # List of 384 floats
    themes_embedding = Column(JSON, nullable=True)    # List of 384 floats
    keywords_embedding = Column(JSON, nullable=True)  # List of 384 floats
    combined_embedding = Column(JSON, nullable=True)  # List of 384 floats

    movie = relationship("Movie", back_populates="embeddings")

class RecommendationCache(Base):
    """
    Caches calculated hybrid recommendation payloads to achieve sub-300ms response times.
    """
    __tablename__ = "recommendation_cache"

    id = Column(Integer, primary_key=True, index=True)
    target_movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    recommendation_type = Column(String(50), nullable=False)  # "similar", "themes", "gems", "trending", "personalized", "all"
    results = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class UserPreference(Base):
    """
    Stores a dynamically updated user preference profile mapping metadata terms to affinity scores.
    """
    __tablename__ = "user_preferences"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    preferred_genres = Column(JSON, nullable=True)    # dict: {genre_name: weight_score}
    preferred_keywords = Column(JSON, nullable=True)  # dict: {keyword: weight_score}
    preferred_directors = Column(JSON, nullable=True) # dict: {director: weight_score}
    preferred_cast = Column(JSON, nullable=True)      # dict: {actor_name: weight_score}
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="preferences")

class UserInteraction(Base):
    """
    Logs raw user behaviors (view, search, save, like) to drive dynamic profile scoring.
    """
    __tablename__ = "user_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    interaction_type = Column(String(50), nullable=False)  # "view", "search", "save", "like"
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
