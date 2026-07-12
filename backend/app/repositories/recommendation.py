# recommendation.py
# Data repository module encapsulating database operations for recommendations, preferences, and embeddings.

from sqlalchemy.orm import Session
from app.models.recommendation import MovieEmbedding, RecommendationCache, UserPreference, UserInteraction
from typing import Optional, List

class RecommendationRepository:
    @staticmethod
    def get_embedding_by_movie_id(db: Session, movie_id: int) -> Optional[MovieEmbedding]:
        """
        Retrieves cached SentenceTransformer embeddings for a movie overview.
        """
        return db.query(MovieEmbedding).filter(MovieEmbedding.movie_id == movie_id).first()

    @staticmethod
    def get_all_embeddings(db: Session) -> List[MovieEmbedding]:
        """
        Retrieves all movie embeddings from the database.
        """
        return db.query(MovieEmbedding).all()

    @staticmethod
    def create_embedding(db: Session, embedding: MovieEmbedding) -> MovieEmbedding:
        """
        Caches calculated text embeddings for a movie.
        """
        db.add(embedding)
        db.commit()
        db.refresh(embedding)
        return embedding

    @staticmethod
    def get_user_interactions(db: Session, user_id: int) -> List[UserInteraction]:
        """
        Retrieves interaction history (views, saves, likes) for a user.
        """
        return db.query(UserInteraction).filter(UserInteraction.user_id == user_id).all()

    @staticmethod
    def create_interaction(db: Session, interaction: UserInteraction) -> UserInteraction:
        """
        Persists a user interaction.
        """
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        return interaction

    @staticmethod
    def get_user_preference(db: Session, user_id: int) -> Optional[UserPreference]:
        """
        Retrieves interest weights profiles (genres, keywords, cast) for a user.
        """
        return db.query(UserPreference).filter(UserPreference.user_id == user_id).first()

    @staticmethod
    def create_user_preference(db: Session, pref: UserPreference) -> UserPreference:
        """
        Saves or initializes interest weights profiles for a user.
        """
        db.add(pref)
        db.commit()
        db.refresh(pref)
        return pref

    @staticmethod
    def get_recommendation_cache(db: Session, user_id: int) -> Optional[RecommendationCache]:
        """
        Retrieves the cached personalized recommendation list for a user.
        """
        return db.query(RecommendationCache).filter(RecommendationCache.user_id == user_id).first()

    @staticmethod
    def create_recommendation_cache(db: Session, cache: RecommendationCache) -> RecommendationCache:
        """
        Caches a compiled personalized recommendation list.
        """
        db.add(cache)
        db.commit()
        db.refresh(cache)
        return cache

    @staticmethod
    def commit(db: Session):
        """
        Commits pending session transactions.
        """
        db.commit()
