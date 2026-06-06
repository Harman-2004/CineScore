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

from app.services.scoring import calculate_normalized_weights

def _calculate_hybrid_score(imdb: Optional[float], tmdb: Optional[float], metacritic: Optional[float], sentiment_avg: float) -> float:
    """
    Intelligently normalizes and redistributes rating weights when specific sources are missing.
    """
    nlp_rating = 5.0 + (sentiment_avg * 5.0)
    nlp_rating = max(0.0, min(10.0, nlp_rating))
    
    score, _, _, _ = calculate_normalized_weights(imdb, tmdb, metacritic, nlp_rating)
    return score

def _cache_movie_if_needed(db: Session, movie_details: dict, is_details: bool = False) -> Movie:
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

    imdb_id = movie_details.get("imdb_id")
    
    omdb_status = movie_details.get("omdb_status")
    omdb_error = movie_details.get("omdb_error")
    media_type = movie_details.get("media_type")
    rating_source = movie_details.get("rating_source")
    
    if not db_movie:
        db_movie = Movie(
            id=movie_id,
            imdb_id=imdb_id,
            title=movie_details.get("title"),
            overview=movie_details.get("overview"),
            poster_path=movie_details.get("poster_path"),
            release_date=movie_details.get("release_date"),
            genres=genres_list,
            runtime=movie_details.get("runtime"),
            vote_average=float(movie_details.get("vote_average", 0.0)),
            imdb_rating=imdb_val,
            metacritic_score=metacritic_val,
            omdb_status=omdb_status,
            omdb_error=omdb_error,
            media_type=media_type,
            rating_source=rating_source,
            is_details_loaded=is_details
        )
        db.add(db_movie)
    else:
        db_movie.title = movie_details.get("title")
        db_movie.overview = movie_details.get("overview")
        db_movie.poster_path = movie_details.get("poster_path")
        db_movie.release_date = movie_details.get("release_date")
        db_movie.genres = genres_list
        db_movie.runtime = movie_details.get("runtime")
        db_movie.vote_average = float(movie_details.get("vote_average", 0.0))
        
        if is_details:
            db_movie.is_details_loaded = True
            
        if imdb_id is not None:
            db_movie.imdb_id = imdb_id
        if imdb_val is not None:
            db_movie.imdb_rating = imdb_val
        if metacritic_val is not None:
            db_movie.metacritic_score = metacritic_val            
        if omdb_status is not None:
            db_movie.omdb_status = omdb_status
        if omdb_error is not None:
            db_movie.omdb_error = omdb_error
        if media_type is not None:
            db_movie.media_type = media_type
        if rating_source is not None:
            db_movie.rating_source = rating_source
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
        # Check SQLite database cache first
        db_movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if db_movie and db_movie.is_details_loaded:
            import datetime
            now = datetime.datetime.now(datetime.timezone.utc)
            cached_time = db_movie.cached_at
            if cached_time.tzinfo is None:
                is_fresh = (datetime.datetime.now() - cached_time).total_seconds() < 86400
            else:
                is_fresh = (now - cached_time).total_seconds() < 86400
                
            if is_fresh:
                return {
                    "id": db_movie.id,
                    "imdb_id": db_movie.imdb_id,
                    "title": db_movie.title,
                    "overview": db_movie.overview,
                    "poster_path": db_movie.poster_path,
                    "release_date": db_movie.release_date,
                    "genres": db_movie.genres,
                    "runtime": db_movie.runtime,
                    "vote_average": db_movie.vote_average,
                    "imdb_rating": db_movie.imdb_rating,
                    "metacritic_score": db_movie.metacritic_score,
                    "omdb_status": db_movie.omdb_status,
                    "omdb_error": db_movie.omdb_error,
                    "media_type": db_movie.media_type,
                    "rating_source": db_movie.rating_source
                }

        # Cache miss - fetch from TMDb service
        data = await tmdb_service.get_movie_details(movie_id=movie_id)
        _cache_movie_if_needed(db, data, is_details=True)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID {movie_id} could not be found: {str(e)}"
        )

@router.get("/{movie_id}/diagnose")
async def diagnose_movie_retrieval(movie_id: int, db: Session = Depends(get_db)):
    """
    Diagnostics endpoint to test step-by-step movie lookup and OMDb API key validation.
    """
    from app.services.tmdb import MOCK_MOVIES
    report = {
        "tmdb_movie_id": movie_id,
        "tmdb_configured": tmdb_service._is_configured(),
        "omdb_configured": bool(tmdb_service.omdb_key),
        "steps": []
    }
    
    try:
        # Step 1: TMDb config check
        report["steps"].append("1. Auditing TMDb & OMDb configuration status.")
        if not tmdb_service._is_configured():
            report["steps"].append("TMDb API key is not configured. Falling back to local MOCK_MOVIES.")
            mock_match = next((m for m in MOCK_MOVIES if m["id"] == movie_id), None)
            if mock_match:
                report["status"] = "mock_success"
                report["result"] = mock_match
            else:
                report["status"] = "mock_not_found"
            return report
            
        # Step 2: Fetch TMDb external IDs
        report["steps"].append("2. Fetching TMDb external IDs via /movie/{movie_id}/external_ids")
        ext_ids = await tmdb_service.get_movie_external_ids(movie_id)
        report["ext_ids_response"] = ext_ids
        imdb_id = ext_ids.get("imdb_id")
        report["extracted_imdb_id"] = imdb_id
        
        if not imdb_id:
            report["steps"].append("WARNING: imdb_id was not returned in external_ids. Checking standard details endpoint.")
            
        # Step 3: Fetch TMDb details
        report["steps"].append("3. Fetching TMDb movie details to verify metadata.")
        import httpx
        async with httpx.AsyncClient() as client:
            details_url = f"{tmdb_service.base_url}/movie/{movie_id}"
            params = {"api_key": tmdb_service.api_key, "language": "en-US"}
            response = await client.get(details_url, params=params, headers=tmdb_service.headers)
            report["tmdb_details_status"] = response.status_code
            if response.status_code == 200:
                details_data = response.json()
                if not imdb_id:
                    imdb_id = details_data.get("imdb_id")
                    report["extracted_imdb_id_from_details"] = imdb_id
            else:
                report["tmdb_details_error"] = response.text
                report["status"] = "tmdb_failed"
                return report
                
        if not imdb_id:
            report["steps"].append("ERROR: No IMDb ID could be resolved from TMDb.")
            report["status"] = "missing_imdb_id"
            return report
            
        # Step 4: Validate OMDb API integration
        report["steps"].append(f"4. Querying OMDb API using imdbID: '{imdb_id}'")
        omdb_res = await tmdb_service._fetch_omdb_ratings(imdb_id, movie_id=movie_id)
        report["omdb_diagnostics"] = {
            "error_type": omdb_res.get("error_type"),
            "error_detail": omdb_res.get("error_detail"),
            "raw_response": omdb_res.get("raw_response"),
            "extracted_imdb_rating": omdb_res.get("imdb_rating"),
            "extracted_metacritic_score": omdb_res.get("metacritic_score")
        }
        
        # Step 5: Validate IMDb Scraping fallback
        report["steps"].append("5. Testing BeautifulSoup real-time IMDb scraping fallback.")
        movie_title_fallback = details_data.get("title", "Unknown") if "details_data" in locals() else "Unknown"
        scraped_res = await tmdb_service._scrape_imdb_rating(imdb_id, movie_title=movie_title_fallback)
        report["scraped_imdb_rating"] = scraped_res.get("rating")
        report["scraper_diagnostics"] = scraped_res
        
        # Final evaluation
        if omdb_res.get("imdb_rating") is not None:
            report["status"] = "omdb_success"
            report["steps"].append("Successfully resolved IMDb rating via OMDb.")
        elif scraped_res.get("status") == "success":
            report["status"] = "scrape_success"
            report["steps"].append("OMDb failed but successfully resolved rating via scraping.")
        else:
            report["status"] = "failure"
            report["steps"].append(f"Both OMDb and scraping failed. Error: {scraped_res.get('reason') or 'Unknown failure'}")
            
        # Execute local details cache compiler to review final output
        final_details = await tmdb_service.get_movie_details(movie_id)
        report["final_details_payload"] = final_details
        
    except Exception as e:
        report["status"] = "exception"
        report["error"] = str(e)
        
    return report
@router.get("/{movie_id}/scraped-reviews")
async def get_scraped_reviews(movie_id: int, db: Session = Depends(get_db)):
    """
    Scrape real-time web reviews or fetch from the local database cache if available and fresh.
    """
    try:
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        title = movie.title if movie else None
        
        if not title:
            try:
                movie_data = await tmdb_service.get_movie_details(movie_id=movie_id)
                _cache_movie_if_needed(db, movie_data, is_details=True)
                title = movie_data["title"]
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Movie details not cached and could not be fetched for ID {movie_id}"
                )
                
        # Check SQLite cache for reviews first
        existing_scraped = db.query(Review).filter(Review.movie_id == movie_id, Review.is_scraped == True).all()
        rating_rec = db.query(Rating).filter(Rating.movie_id == movie_id).first()
        is_fresh = False
        if rating_rec:
            import datetime
            now = datetime.datetime.now(datetime.timezone.utc)
            if rating_rec.last_updated.tzinfo is None:
                is_fresh = (datetime.datetime.now() - rating_rec.last_updated).total_seconds() < 86400
            else:
                is_fresh = (now - rating_rec.last_updated).total_seconds() < 86400
                
        if existing_scraped and is_fresh:
            print(f"[Scraper Cache] Bypassing scrapers. Returning {len(existing_scraped)} cached reviews.")
            return {
                "movie_id": movie_id,
                "movie_title": title,
                "reviews_scraped": len(existing_scraped),
                "reviews": [
                    {
                        "reviewer": r.author,
                        "scraped_rating": r.rating,
                        "review_text": r.review_text,
                        "sentiment_score": r.sentiment_score,
                        "sentiment_label": r.sentiment_label,
                        "source": "Cached Feed"
                    } for r in existing_scraped
                ]
            }
            
        # Cache miss - scrape reviews
        scraped_reviews = await movie_scraper.scrape_reviews_for_movie(title, imdb_id=movie.imdb_id if movie else None)
        
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
                    aspect_scores=r.get("aspect_scores"),
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
