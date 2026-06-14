from app.database import Base
from app.models.user import User
from app.models.movie import Movie
from app.models.review import Review
from app.models.rating import Rating
from app.models.recommendation import MovieEmbedding, RecommendationCache, UserPreference, UserInteraction

__all__ = ["Base", "User", "Movie", "Review", "Rating", "MovieEmbedding", "RecommendationCache", "UserPreference", "UserInteraction"]

