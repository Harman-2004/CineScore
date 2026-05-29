from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.tmdb import tmdb_service, GENRE_MAP
from app.models.movie import Movie
from app.models.rating import Rating
from app.models.review import Review
from app.schemas.movie import MovieResponse, MovieListResponse
from app.scraper.scraper import movie_scraper
from typing import List, Dict, Any, Optional

router = APIRouter(prefix="/movies", tags=["Movies"])

def _calculate_hybrid_score(imdb: Optional[float], tmdb: Optional[float], metacritic: Optional[float], sentiment_avg: float) -> float:
    """
    Implements the core project innovation Hybrid Rating Formula:
    FinalScore = 0.4(IMDb) + 0.2(TMDb) + 0.1(Metacritic) + 0.3(NLPReviewScore)
    
    Normalizes average review sentiment polarity (-1.0 to 1.0) onto a clean 1.0 to 10.0 scale.
    Uses re-normalized weights if specific score items are missing.
    """
    weights = {"imdb": 0.4, "tmdb": 0.2, "metacritic": 0.1, "nlp": 0.3}
    values = {}
    
    if imdb is not None and imdb > 0:
        values["imdb"] = float(imdb)
    if tmdb is not None and tmdb > 0:
        values["tmdb"] = float(tmdb)
    if metacritic is not None and metacritic > 0:
        values["metacritic"] = float(metacritic)
        
    # Map average sentiment polarity (-1.0 to 1.0) onto a 0.0 to 10.0 scale
    # 0.0 sentiment -> 5.0 rating, +1.0 sentiment -> 10.0 rating, -1.0 sentiment -> 0.0 rating
    nlp_rating = 5.0 + (sentiment_avg * 5.0)
    values["nlp"] = max(0.0, min(10.0, nlp_rating))
    
    if not values:
        return 0.0
        
    weighted_sum = sum(values[k] * weights[k] for k in values)
    sum_weights = sum(weights[k] for k in values)
    
    final_score = weighted_sum / sum_weights
    return round(float(final_score), 2)

def _cache_movie_if_needed(db: Session, movie_details: dict) -> Movie:
    """
    Saves or updates movie metadata in the local database 'movies' table.
    Also automatically calculates composite scores and maintains the 'ratings' table.
    """
    movie_id = movie_details.get("id")
    if not movie_id:
        return None
        
    db_movie = db.query(Movie).filter(Movie.id == movie_id).first()
    
    genres_list = movie_details.get("genres", [])
    if genres_list and isinstance(genres_list, list):
        if len(genres_list) > 0 and isinstance(genres_list[0], int):
            genres_list = [{"id": gid, "name": GENRE_MAP.get(gid, "Unknown")} for gid in genres_list]
    else:
        genre_ids = movie_details.get("genre_ids", [])
        genres_list = [{"id": gid, "name": GENRE_MAP.get(gid, "Unknown")} for gid in genre_ids]

    imdb_val = movie_details.get("imdb_rating")
    if imdb_val is not None:
        imdb_val = float(imdb_val)
        
    metacritic_val = movie_details.get("metacritic_score")
    if metacritic_val is not None:
        metacritic_val = float(metacritic_val)

    if not db_movie:
        db_movie = Movie(
            id=movie_id,
            title=movie_details.get("title"),
            overview=movie_details.get("overview"),
            poster_path=movie_details.get("poster_path"),
            release_date=movie_details.get("release_date"),
            genres=genres_list,
            vote_average=float(movie_details.get("vote_average", 0.0)),
            imdb_rating=imdb_val,
            metacritic_score=metacritic_val
        )
        db.add(db_movie)
    else:
        db_movie.title = movie_details.get("title")
        db_movie.overview = movie_details.get("overview")
        db_movie.poster_path = movie_details.get("poster_path")
        db_movie.release_date = movie_details.get("release_date")
        db_movie.genres = genres_list
        db_movie.vote_average = float(movie_details.get("vote_average", 0.0))
        if imdb_val is not None:
            db_movie.imdb_rating = imdb_val
        if metacritic_val is not None:
            db_movie.metacritic_score = metacritic_val
            
    db.commit()
    db.refresh(db_movie)

    # Upsert 'ratings' table record
    db_rating = db.query(Rating).filter(Rating.movie_id == movie_id).first()
    
    tmdb_score = db_movie.vote_average
    imdb_score = db_movie.imdb_rating
    metacritic_score = db_movie.metacritic_score
    
    sentiment_avg = db_rating.sentiment_avg if db_rating else 0.0
    rating_count = db_rating.rating_count if db_rating else 0
    
    aggregate = _calculate_hybrid_score(imdb_score, tmdb_score, metacritic_score, sentiment_avg)

    if not db_rating:
        db_rating = Rating(
            movie_id=movie_id,
            imdb_score=imdb_score,
            tmdb_score=tmdb_score,
            metacritic_score=metacritic_score,
            aggregate_score=aggregate,
            rating_count=rating_count,
            sentiment_avg=sentiment_avg
        )
        db.add(db_rating)
    else:
        db_rating.imdb_score = imdb_score
        db_rating.tmdb_score = tmdb_score
        db_rating.metacritic_score = metacritic_score
        db_rating.aggregate_score = aggregate
        
    db.commit()
    return db_movie

@router.get("/popular", response_model=MovieListResponse)
async def get_popular(page: int = Query(1, ge=1), db: Session = Depends(get_db)):
    """
    Retrieve a paginated list of popular movies from TMDb.
    Pre-caches returned movies in the database.
    """
    try:
        data = await tmdb_service.get_popular_movies(page=page)
        for m in data.get("results", []):
            try:
                _cache_movie_if_needed(db, m)
            except Exception:
                pass
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching popular movies: {str(e)}"
        )

@router.get("/search", response_model=MovieListResponse)
async def search(query: str = Query(..., min_length=1), page: int = Query(1, ge=1), db: Session = Depends(get_db)):
    """
    Search for movies on TMDb by title or keywords.
    Pre-caches search results in the database.
    """
    try:
        data = await tmdb_service.search_movies(query=query, page=page)
        for m in data.get("results", []):
            try:
                _cache_movie_if_needed(db, m)
            except Exception:
                pass
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching movies: {str(e)}"
        )

@router.get("/{movie_id}", response_model=MovieResponse)
async def get_details(movie_id: int, db: Session = Depends(get_db)):
    """
    Retrieve full details for a specific movie.
    Checks and populates local database cache.
    """
    try:
        data = await tmdb_service.get_movie_details(movie_id=movie_id)
        _cache_movie_if_needed(db, data)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID {movie_id} could not be found: {str(e)}"
        )

@router.get("/{movie_id}/scraped-reviews")
async def get_scraped_reviews(movie_id: int, db: Session = Depends(get_db)):
    """
    Scrape real-time web reviews for a given movie across platforms,
    automatically storing all scraped reviews persistently in the PostgreSQL database.
    """
    try:
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if not movie:
            try:
                movie_data = await tmdb_service.get_movie_details(movie_id=movie_id)
                _cache_movie_if_needed(db, movie_data)
                title = movie_data["title"]
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Movie details not cached and could not be fetched for ID {movie_id}"
                )
        else:
            title = movie.title
            
        scraped_reviews = await movie_scraper.scrape_reviews_for_movie(title)
        
        for r in scraped_reviews:
            existing = db.query(Review).filter(
                Review.movie_id == movie_id,
                Review.author == r["reviewer"],
                Review.is_scraped == True
            ).first()
            
            if not existing:
                db_review = Review(
                    movie_id=movie_id,
                    rating=r["scraped_rating"],
                    review_text=r["review_text"],
                    sentiment_score=r["sentiment_score"],
                    sentiment_label=r["sentiment_label"],
                    is_scraped=True,
                    author=r["reviewer"]
                )
                db.add(db_review)
                
        db.commit()
        
        from app.routers.reviews import _update_rating_statistics
        try:
            _update_rating_statistics(db, movie_id)
        except Exception:
            pass
            
        return {
            "movie_id": movie_id,
            "movie_title": title,
            "reviews_scraped": len(scraped_reviews),
            "reviews": scraped_reviews
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to scrape reviews: {str(e)}"
        )
