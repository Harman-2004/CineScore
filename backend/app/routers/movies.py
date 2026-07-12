# movies.py
# Router module defining endpoints for movie searches, popular titles, and scrapers.

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.movie import MovieResponse, MovieListResponse
from app.services.movie import MovieService

router = APIRouter(prefix="/movies", tags=["Movies"])

# Backward-compatible helper functions for external imports
def _calculate_hybrid_score(imdb, tmdb, metacritic, sentiment_avg, youtube_score=None) -> float:
    """
    Exposed wrapper for compatibility with legacy imports.
    """
    from app.services.scoring import calculate_normalized_weights
    nlp_rating = 5.0 + (sentiment_avg * 5.0)
    nlp_rating = max(0.0, min(10.0, nlp_rating))
    score, _, _, _ = calculate_normalized_weights(imdb, tmdb, metacritic, nlp_rating, youtube_score)
    return score

def _cache_movie_if_needed(db: Session, movie_details: dict, fetch_transcript: bool = False):
    """
    Exposed wrapper for compatibility with legacy imports.
    """
    return MovieService.cache_movie_if_needed(db, movie_details, fetch_transcript)


@router.get("/popular", response_model=MovieListResponse)
async def get_popular(page: int = Query(1, ge=1), db: Session = Depends(get_db)):
    """
    Retrieve popular movies from TMDb.
    """
    return await MovieService.get_popular_movies(db, page)

@router.get("/search", response_model=MovieListResponse)
async def search(query: str = Query(..., min_length=1), page: int = Query(1, ge=1), db: Session = Depends(get_db)):
    """
    Search for movies matching query keywords.
    """
    return await MovieService.search_movies(db, query, page)

@router.get("/{movie_id}", response_model=MovieResponse)
async def get_details(movie_id: int, db: Session = Depends(get_db)):
    """
    Retrieve full details for a movie by TMDb ID.
    """
    return await MovieService.get_movie_details(db, movie_id)

@router.get("/{movie_id}/scraped-reviews")
async def get_scraped_reviews(movie_id: int, db: Session = Depends(get_db)):
    """
    Trigger reviews scraping and NLP analysis.
    """
    return await MovieService.get_scraped_reviews(db, movie_id)
