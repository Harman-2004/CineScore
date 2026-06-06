from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.movie import Movie
from app.models.review import Review
from app.models.rating import Rating
from app.services.tmdb import tmdb_service
from app.routers.movies import _cache_movie_if_needed
from app.schemas.movie import MovieResponse, MovieListResponse
from typing import List, Dict, Any, Optional
from app.services.cache import cache_service

router = APIRouter(tags=["Standard REST API"])

@router.get("/movies", response_model=MovieListResponse)
async def list_movies(
    page: int = Query(1, ge=1, description="Page number"),
    query: Optional[str] = Query(None, description="Optional search query keyword"),
    db: Session = Depends(get_db)
):
    """
    List movies. If a query is provided, performs a search;
    otherwise, retrieves the current popular movies list.
    Uses Redis/memory cache with 24 hour TTL (popular) or 1 hour TTL (search).
    """
    cache_key = f"movies_search:{query}:{page}" if query else f"movies_popular:{page}"
    cached_val = cache_service.get(cache_key)
    if cached_val:
        return cached_val
        
    try:
        if query:
            data = await tmdb_service.search_movies(query=query, page=page)
            ttl = 3600  # 1 hour for search results
        else:
            data = await tmdb_service.get_popular_movies(page=page)
            ttl = 86400  # 24 hours for popular movies
            
        # Cache results in local database only for popular list, bypass for live search queries
        if not query:
            for m in data.get("results", []):
                try:
                    _cache_movie_if_needed(db, m)
                except Exception:
                    pass
        cache_service.set(cache_key, data, ttl_seconds=ttl)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing movies: {str(e)}"
        )

@router.get("/movie/{id}", response_model=MovieResponse)
async def movie_details(id: int, db: Session = Depends(get_db)):
    """
    Retrieve details for a specific movie by its TMDb ID.
    Checks SQLite database cache first to guarantee sub-10ms response times.
    """
    try:
        # Check SQLite database cache first
        db_movie = db.query(Movie).filter(Movie.id == id).first()
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

        # Cache miss - fetch details
        data = await tmdb_service.get_movie_details(movie_id=id)
        _cache_movie_if_needed(db, data, is_details=True)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID {id} could not be found: {str(e)}"
        )
@router.get("/reviews/{movie}")
def movie_reviews(movie: int, db: Session = Depends(get_db)):
    """
    Retrieve all stored reviews (user-submitted and scraped reviews)
    for a specific movie ID.
    """
    # Verify if movie exists in cache, if not try fetching details
    db_movie = db.query(Movie).filter(Movie.id == movie).first()
    if not db_movie:
        try:
            # Attempt to fetch details to populate cache
            import asyncio
            data = asyncio.run(tmdb_service.get_movie_details(movie_id=movie))
            _cache_movie_if_needed(db, data, is_details=True)
        except Exception:
            pass
            
    reviews = db.query(Review).filter(Review.movie_id == movie).order_by(Review.created_at.desc()).all()
    
    # Format response lists
    from app.sentiment.analyzer import sentiment_service
    from app.services.moderation import review_moderation_service
    
    # Run review pool moderation checks
    moderated_pool = review_moderation_service.analyze_review_pool(reviews)
    moderated_map = {item["id"]: item for item in moderated_pool}
    
    reviews_formatted = []
    for r in reviews:
        if r.aspect_scores:
            aspects = r.aspect_scores
        else:
            aspects = sentiment_service.analyze_aspects(r.review_text)
            r.aspect_scores = aspects
            db.add(r)
            db.commit()
        mod = moderated_map.get(r.id, {"is_spam": False, "is_bot": False, "spam_reasons": [], "spam_probability": 0.0})
        reviews_formatted.append({
            "id": r.id,
            "reviewer": r.author if r.is_scraped else (r.user.username if r.user else "Anonymous"),
            "rating": r.rating,
            "review_text": r.review_text,
            "sentiment_score": r.sentiment_score,
            "sentiment_label": r.sentiment_label,
            "is_scraped": r.is_scraped,
            "created_at": r.created_at,
            "aspect_scores": aspects,
            "moderation": {
                "is_spam": mod["is_spam"],
                "is_bot": mod["is_bot"],
                "spam_reasons": mod["spam_reasons"],
                "spam_probability": mod["spam_probability"]
            }
        })
        
    return {
        "movie_id": movie,
        "movie_title": db_movie.title if db_movie else f"Movie {movie}",
        "total_reviews": len(reviews_formatted),
        "reviews": reviews_formatted
    }

@router.get("/sentiment/{movie}")
def movie_sentiment_analysis(movie: int, db: Session = Depends(get_db)):
    """
    Retrieve a comprehensive NLP sentiment analysis report for all stored
    reviews of a specific movie.
    """
    from app.sentiment.analyzer import sentiment_service
    from app.services.moderation import review_moderation_service
    
    reviews = db.query(Review).filter(Review.movie_id == movie).all()
    if not reviews:
        return {
            "movie_id": movie,
            "reviews_analyzed": 0,
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0,
            "average_sentiment_polarity": 0.0,
            "overall_sentiment_label": "NEUTRAL",
            "average_aspect_scores": {
                "acting": 5.0,
                "story": 5.0,
                "music": 5.0,
                "visual_effects": 5.0,
                "direction": 5.0
            },
            "integrity_metrics": {
                "integrity_score": 100.0,
                "spam_count": 0,
                "bot_flag_count": 0,
                "duplicate_count": 0
            }
        }
        
    pos_count = sum(1 for r in reviews if r.sentiment_label == "POSITIVE")
    neg_count = sum(1 for r in reviews if r.sentiment_label == "NEGATIVE")
    neu_count = sum(1 for r in reviews if r.sentiment_label == "NEUTRAL")
    
    sentiments = [r.sentiment_score for r in reviews if r.sentiment_score is not None]
    avg_polarity = sum(sentiments) / len(sentiments) if sentiments else 0.0
    
    if avg_polarity > 0.15:
        overall_label = "POSITIVE"
    elif avg_polarity < -0.15:
        overall_label = "NEGATIVE"
    else:
        overall_label = "NEUTRAL"
        
    # Calculate average aspect scores
    acting_sum = 0
    story_sum = 0
    music_sum = 0
    vfx_sum = 0
    direction_sum = 0
    
    for r in reviews:
        if r.aspect_scores:
            aspects = r.aspect_scores
        else:
            aspects = sentiment_service.analyze_aspects(r.review_text)
            r.aspect_scores = aspects
            db.add(r)
            db.commit()
        acting_sum += aspects.get("acting", 5.0)
        story_sum += aspects.get("story", 5.0)
        music_sum += aspects.get("music", 5.0)
        vfx_sum += aspects.get("visual_effects", 5.0)
        direction_sum += aspects.get("direction", 5.0)
    count = len(reviews)
    avg_aspects = {
        "acting": round(acting_sum / count, 1),
        "story": round(story_sum / count, 1),
        "music": round(music_sum / count, 1),
        "visual_effects": round(vfx_sum / count, 1),
        "direction": round(direction_sum / count, 1)
    }
    
    # Run pool moderation metrics
    moderated_pool = review_moderation_service.analyze_review_pool(reviews)
    spam_count = sum(1 for item in moderated_pool if item["is_spam"])
    bot_count = sum(1 for item in moderated_pool if item["is_bot"])
    duplicate_count = sum(1 for item in moderated_pool if "Duplicate review" in "".join(item["spam_reasons"]))
    
    integrity_score = round(((count - spam_count) / count) * 100, 1) if count > 0 else 100.0
        
    return {
        "movie_id": movie,
        "reviews_analyzed": len(reviews),
        "positive_count": pos_count,
        "negative_count": neg_count,
        "neutral_count": neu_count,
        "average_sentiment_polarity": round(float(avg_polarity), 4),
        "overall_sentiment_label": overall_label,
        "average_aspect_scores": avg_aspects,
        "integrity_metrics": {
            "integrity_score": integrity_score,
            "spam_count": spam_count,
            "bot_flag_count": bot_count,
            "duplicate_count": duplicate_count
        }
    }

@router.get("/rating/{movie}")
def movie_composite_rating(movie: int, db: Session = Depends(get_db)):
    """
    Retrieve the consolidated hybrid composite scores and metrics
    from the 'ratings' table for a specific movie.
    """
    db_rating = db.query(Rating).filter(Rating.movie_id == movie).first()
    db_movie = db.query(Movie).filter(Movie.id == movie).first()
    
    if not db_rating:
        # If no rating entry exists, attempt to pull details and create one
        if db_movie:
            try:
                from app.routers.movies import _cache_movie_if_needed
                # Force refresh/upsert
                _cache_movie_if_needed(db, {
                    "id": db_movie.id,
                    "title": db_movie.title,
                    "overview": db_movie.overview,
                    "poster_path": db_movie.poster_path,
                    "release_date": db_movie.release_date,
                    "vote_average": db_movie.vote_average,
                    "imdb_rating": db_movie.imdb_rating,
                    "metacritic_score": db_movie.metacritic_score
                }, is_details=db_movie.is_details_loaded)
                db_rating = db.query(Rating).filter(Rating.movie_id == movie).first()
            except Exception:
                pass
                
    if not db_rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rating score metrics could not be resolved for movie ID {movie}"
        )
        
    from app.services.scoring import calculate_normalized_weights
    
    sentiment_avg = db_rating.sentiment_avg if db_rating.sentiment_avg is not None else 0.0
    nlp_val = 5.0 + (sentiment_avg * 5.0)
    nlp_val = max(0.0, min(10.0, nlp_val))
    
    score, effective_weights, available, missing = calculate_normalized_weights(
        db_rating.imdb_score,
        db_rating.tmdb_score,
        db_rating.metacritic_score,
        nlp_val
    )
    
    imdb_status_detail = None
    if effective_weights.get("imdb", 0.0) == 0.0:
        from app.config import settings
        if not settings.OMDB_API_KEY or settings.OMDB_API_KEY.startswith("your_omdb_api_key"):
            imdb_status_detail = "OMDb API Key is unconfigured in .env"
        elif not db_movie or not db_movie.imdb_id:
            imdb_status_detail = "IMDb ID is not available for this movie"
        else:
            imdb_status_detail = "OMDb limits exceeded/scraper blocked or movie not found"
    else:
        imdb_status_detail = "Rating successfully resolved."
        
    return {
        "movie_id": movie,
        "movie_title": db_movie.title if db_movie else f"Movie {movie}",
        "imdb_id": db_movie.imdb_id if db_movie else None,
        "imdb_score": db_rating.imdb_score,
        "imdb_rating": db_rating.imdb_score,
        "tmdb_score": db_rating.tmdb_score,
        "metacritic_score": db_rating.metacritic_score,
        "sentiment_avg_polarity": db_rating.sentiment_avg,
        "reviews_count": db_rating.rating_count,
        "aggregate_hybrid_score": score,
        "formula": "FinalScore = 0.4(IMDb) + 0.2(TMDb) + 0.1(Metacritic) + 0.3(NLPReviewScore)",
        "effective_weights": effective_weights,
        "available_sources": available,
        "missing_sources": missing,
        "imdb_status_detail": imdb_status_detail,
        "omdb_status": db_movie.omdb_status if db_movie else None,
        "omdb_error": db_movie.omdb_error if db_movie else None
    }

@router.get("/movies/{movie_id}/scraped-reviews")
async def trigger_scraped_reviews_root(movie_id: int, db: Session = Depends(get_db)):
    """
    Trigger live BeautifulSoup scraping across external web reviews sources
    at the root standard REST API level.
    """
    from app.routers.movies import get_scraped_reviews
    return await get_scraped_reviews(movie_id=movie_id, db=db)

@router.get("/movie/{id}/recommendations")
async def get_movie_recommendations_root(id: int, db: Session = Depends(get_db)):
    """
    Retrieve similar content-based movie recommendations (using TF-IDF,
    overview embeddings, and Cosine Similarity) for a given movie ID.
    """
    from app.services.recommendation import recommendation_service
    return await recommendation_service.get_content_recommendations(db=db, target_movie_id=id)

@router.get("/debug/imdb/{movie_id}")
async def debug_imdb_retrieval(movie_id: int, db: Session = Depends(get_db)):
    """
    Diagnostic endpoint to perform live OMDb API query and trace IMDb rating retrieval step-by-step.
    """
    try:
        from app.services.tmdb import tmdb_service
        # Step 1: TMDb external IDs
        ext_ids = await tmdb_service.get_movie_external_ids(movie_id)
        imdb_id = ext_ids.get("imdb_id")
        
        # Step 2: Get movie title from TMDb details
        title = f"Movie {movie_id}"
        if tmdb_service._is_configured():
            details_url = f"{tmdb_service.base_url}/movie/{movie_id}"
            details_params = {"api_key": tmdb_service.api_key, "language": "en-US"}
            import httpx
            async with httpx.AsyncClient() as client:
                res = await client.get(details_url, params=details_params, headers=tmdb_service.headers, timeout=5.0)
                if res.status_code == 200:
                    title = res.json().get("title", title)
                    
        omdb_response = {}
        scraper_response = {}
        final_rating = None
        failure_reason = None
        
        if imdb_id:
            # Step 3: Run OMDb rating lookup first
            omdb_res = await tmdb_service._fetch_omdb_ratings(imdb_id, movie_id=movie_id)
            omdb_response = omdb_res.get("raw_response") or {}
            
            if omdb_res.get("imdb_rating") is not None:
                # OMDb succeeded
                final_rating = omdb_res.get("imdb_rating")
                scraper_response = {"status": "skipped", "reason": "OMDb lookup succeeded"}
            else:
                # OMDb failed, run the web scraper
                failure_reason = omdb_res.get("omdb_error") or "OMDb lookup returned empty rating"
                scraper_res = await tmdb_service._scrape_imdb_rating(imdb_id, movie_title=title)
                scraper_response = scraper_res
                
                if scraper_res.get("status") == "success":
                    final_rating = scraper_res.get("rating")
                    failure_reason = None
                else:
                    final_rating = None
                    failure_reason = scraper_res.get("reason") or "Scraper failed to parse rating"
        else:
            failure_reason = "No IMDb ID resolved from TMDb"
            
        return {
            "movie_title": title,
            "tmdb_id": str(movie_id),
            "imdb_id": imdb_id,
            "omdb_response": omdb_response,
            "scraper_response": scraper_response,
            "final_rating": str(final_rating) if final_rating is not None else None,
            "failure_reason": failure_reason
        }
    except Exception as e:
        return {
            "movie_title": f"Movie {movie_id}",
            "tmdb_id": str(movie_id),
            "imdb_id": None,
            "omdb_response": {"error": f"Exception in diagnostic route: {str(e)}"},
            "scraper_response": {},
            "final_rating": None,
            "failure_reason": f"System exception: {str(e)}"
        }

@router.get("/debug/movie/{tmdb_id}")
async def debug_movie_details(tmdb_id: int, db: Session = Depends(get_db)):
    """
    Debug endpoint to trace TMDb -> IMDb ID resolution, media type classification, and rating lookup.
    """
    try:
        from app.services.tmdb import tmdb_service
        # Get details from TMDb service (triggers fallback resolver and media type classification)
        details = await tmdb_service.get_movie_details(tmdb_id)
        
        # Get external IDs for the specific media type
        is_tv = details.get("media_type") in ["TV Show", "Mini-Series", "Anime"]
        if is_tv:
            external_ids = await tmdb_service.get_tv_external_ids(tmdb_id)
        else:
            external_ids = await tmdb_service.get_movie_external_ids(tmdb_id)
            
        # Perform data quality checks
        missing_fields = []
        if details.get("vote_average") is None:
            missing_fields.append("tmdb_score")
        if not details.get("imdb_id"):
            missing_fields.append("imdb_id")
        if details.get("omdb_status") != "success":
            missing_fields.append("omdb_status")
        if details.get("metacritic_score") is None:
            missing_fields.append("metacritic_score")
            
        quality_check = {
            "tmdb_score_exists": details.get("vote_average") is not None,
            "imdb_id_exists": bool(details.get("imdb_id")),
            "omdb_lookup_succeeded": details.get("omdb_status") == "success",
            "metacritic_score_exists": details.get("metacritic_score") is not None
        }
        
        return {
            "title": details.get("title"),
            "tmdb_id": tmdb_id,
            "media_type": details.get("media_type"),
            "external_ids": external_ids,
            "imdb_id": details.get("imdb_id"),
            "omdb_status": details.get("omdb_status"),
            "omdb_error": details.get("omdb_error"),
            "imdb_rating": details.get("imdb_rating"),
            "metacritic_score": details.get("metacritic_score"),
            "tmdb_score": details.get("vote_average"),
            "missing_fields": missing_fields,
            "quality_check": quality_check
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to debug movie {tmdb_id}: {str(e)}"
        )


