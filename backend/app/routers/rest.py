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
    """
    import asyncio
    try:
        if query:
            data = await tmdb_service.search_movies(query=query, page=page)
        else:
            data = await tmdb_service.get_popular_movies(page=page)
            
        # Cache results in local database in a background thread
        def cache_movies_sync(db, movies):
            for m in movies:
                try:
                    _cache_movie_if_needed(db, m)
                except Exception:
                    pass
        await asyncio.to_thread(cache_movies_sync, db, data.get("results", []))
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
    """
    import asyncio
    db_movie = await asyncio.to_thread(
        lambda: db.query(Movie).filter(Movie.id == id).first()
    )
    if db_movie and db_movie.imdb_rating is not None:
        return {
            "id": db_movie.id,
            "title": db_movie.title,
            "overview": db_movie.overview,
            "poster_path": db_movie.poster_path,
            "release_date": db_movie.release_date,
            "genres": db_movie.genres,
            "vote_average": db_movie.vote_average,
            "imdb_rating": db_movie.imdb_rating,
            "metacritic_score": db_movie.metacritic_score
        }
    try:
        data = await tmdb_service.get_movie_details(movie_id=id)
        await asyncio.to_thread(_cache_movie_if_needed, db, data)
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
            _cache_movie_if_needed(db, data)
        except Exception:
            pass
            
    reviews = db.query(Review).filter(Review.movie_id == movie).order_by(Review.created_at.desc()).all()
    
    # Format response lists
    from app.sentiment.analyzer import sentiment_service
    from app.services.moderation import review_moderation_service
    import json
    
    # Run review pool moderation checks
    moderated_pool = review_moderation_service.analyze_review_pool(reviews)
    moderated_map = {item["id"]: item for item in moderated_pool}
    
    reviews_formatted = []
    has_new_aspects = False
    for r in reviews:
        aspects = None
        if r.aspect_scores_json:
            try:
                aspects = json.loads(r.aspect_scores_json)
            except Exception:
                aspects = None
                
        if not aspects:
            aspects = sentiment_service.analyze_aspects(r.review_text)
            try:
                r.aspect_scores_json = json.dumps(aspects)
                has_new_aspects = True
            except Exception:
                pass
                
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
            "source": r.source,
            "moderation": {
                "is_spam": mod["is_spam"],
                "is_bot": mod["is_bot"],
                "spam_reasons": mod["spam_reasons"],
                "spam_probability": mod["spam_probability"]
            }
        })
        
    if has_new_aspects:
        try:
            db.commit()
        except Exception:
            db.rollback()
        
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
    import json
    
    reviews = db.query(Review).filter(Review.movie_id == movie).all()
    general_reviews = [r for r in reviews if r.source != "YouTube"]
    if not general_reviews:
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
        
    pos_count = sum(1 for r in general_reviews if r.sentiment_label == "POSITIVE")
    neg_count = sum(1 for r in general_reviews if r.sentiment_label == "NEGATIVE")
    neu_count = sum(1 for r in general_reviews if r.sentiment_label == "NEUTRAL")
    
    sentiments = [r.sentiment_score for r in general_reviews if r.sentiment_score is not None]
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
    has_new_aspects = False
    
    for r in general_reviews:
        aspects = None
        if r.aspect_scores_json:
            try:
                aspects = json.loads(r.aspect_scores_json)
            except Exception:
                aspects = None
                
        if not aspects:
            aspects = sentiment_service.analyze_aspects(r.review_text)
            try:
                r.aspect_scores_json = json.dumps(aspects)
                has_new_aspects = True
            except Exception:
                pass
                
        acting_sum += aspects.get("acting", 5.0)
        story_sum += aspects.get("story", 5.0)
        music_sum += aspects.get("music", 5.0)
        vfx_sum += aspects.get("visual_effects", 5.0)
        direction_sum += aspects.get("direction", 5.0)
        
    if has_new_aspects:
        try:
            db.commit()
        except Exception:
            db.rollback()
        
    count = len(general_reviews)
    avg_aspects = {
        "acting": round(acting_sum / count, 1),
        "story": round(story_sum / count, 1),
        "music": round(music_sum / count, 1),
        "visual_effects": round(vfx_sum / count, 1),
        "direction": round(direction_sum / count, 1)
    }
    
    # Run pool moderation metrics
    moderated_pool = review_moderation_service.analyze_review_pool(general_reviews)
    spam_count = sum(1 for item in moderated_pool if item["is_spam"])
    bot_count = sum(1 for item in moderated_pool if item["is_bot"])
    duplicate_count = sum(1 for item in moderated_pool if "Duplicate review" in "".join(item["spam_reasons"]))
    
    integrity_score = round(((count - spam_count) / count) * 100, 1) if count > 0 else 100.0
        
    return {
        "movie_id": movie,
        "reviews_analyzed": count,
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
                })
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
    nlp_val = None
    if db_rating.rating_count > 0:
        nlp_val = 5.0 + (sentiment_avg * 5.0)
        nlp_val = max(0.0, min(10.0, nlp_val))
    
    score, effective_weights, available, missing = calculate_normalized_weights(
        db_rating.imdb_score,
        db_rating.tmdb_score,
        db_rating.metacritic_score,
        nlp_val,
        db_rating.youtube_score
    )
    
    return {
        "movie_id": movie,
        "movie_title": db_movie.title if db_movie else f"Movie {movie}",
        "imdb_score": db_rating.imdb_score,
        "tmdb_score": db_rating.tmdb_score,
        "metacritic_score": db_rating.metacritic_score,
        "youtube_score": db_rating.youtube_score,
        "sentiment_avg_polarity": db_rating.sentiment_avg,
        "reviews_count": db_rating.rating_count,
        "aggregate_hybrid_score": score,
        "formula": "FinalScore = 40% YouTube + 25% IMDb + 15% Web NLP + 10% TMDb + 10% Metacritic",
        "effective_weights": effective_weights,
        "available_sources": available,
        "missing_sources": missing
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
    Retrieve aggregated hybrid recommendation groups with full explainable analytics.
    """
    from app.services.recommendation import recommendation_service
    import asyncio
    
    recs = await asyncio.to_thread(
        recommendation_service.get_netflix_recommendations, db, id
    )
    return recs


@router.get("/movie/{id}/dashboard")
async def movie_dashboard(id: int, db: Session = Depends(get_db)):
    """
    Consolidated API endpoint that aggregates movie details, reviews, rating,
    sentiment, and recommendations in a single fast, concurrent JSON payload.
    """
    import asyncio
    import json

    # 1. Fetch details (async call to TMDb or local DB check in separate thread)
    db_movie = await asyncio.to_thread(
        lambda: db.query(Movie).filter(Movie.id == id).first()
    )
    
    def is_mock_movie(movie) -> bool:
        if not movie:
            return True
        if movie.title and movie.title.startswith("Mock Movie "):
            return True
        if movie.overview and "placeholder description for mock movie" in movie.overview:
            return True
        return False

    if not db_movie or db_movie.imdb_rating is None or is_mock_movie(db_movie):
        try:
            movie_data = await tmdb_service.get_movie_details(movie_id=id)
            await asyncio.to_thread(_cache_movie_if_needed, db, movie_data)
            db_movie = await asyncio.to_thread(
                lambda: db.query(Movie).filter(Movie.id == id).first()
            )
        except Exception:
            pass

    # 2. Fetch reviews from local DB in separate thread
    reviews = await asyncio.to_thread(
        lambda: db.query(Review).filter(Review.movie_id == id).order_by(Review.created_at.desc()).all()
    )
    
    # Format reviews and calculate aspects
    from app.sentiment.analyzer import sentiment_service
    
    # Concurrently analyze aspects for reviews that lack saved aspect scores
    reviews_needing_aspects = []
    for r in reviews:
        aspects = None
        if r.aspect_scores_json:
            try:
                aspects = json.loads(r.aspect_scores_json)
            except Exception:
                pass
        if not aspects:
            reviews_needing_aspects.append(r)
            
    if reviews_needing_aspects:
        # Run aspect analysis concurrently in a thread pool
        async def process_aspects(rev):
            asp = await asyncio.to_thread(sentiment_service.analyze_aspects, rev.review_text)
            return rev, asp
            
        tasks = [process_aspects(rev) for rev in reviews_needing_aspects]
        results = await asyncio.gather(*tasks)
        
        # Save calculated aspect scores to database in a background thread
        def save_aspects_sync(db, calculated_pairs):
            for rev, asp in calculated_pairs:
                rev.aspect_scores_json = json.dumps(asp)
            try:
                db.commit()
            except Exception:
                db.rollback()
        await asyncio.to_thread(save_aspects_sync, db, results)

    # Process reviews formatting and moderation checks in a separate background thread
    def process_reviews_and_moderation_sync(reviews_list):
        from app.services.moderation import review_moderation_service
        moderated_pool = review_moderation_service.analyze_review_pool(reviews_list)
        moderated_map = {item["id"]: item for item in moderated_pool}
        
        reviews_formatted = []
        pos_count = 0
        neg_count = 0
        neu_count = 0
        sentiments = []
        
        acting_sum = 0
        story_sum = 0
        music_sum = 0
        vfx_sum = 0
        direction_sum = 0
        
        # Build a map of review ID -> source
        review_sources = {r.id: r.source for r in reviews_list}

        for r in reviews_list:
            if r.source != "YouTube":
                if r.sentiment_label == "POSITIVE":
                    pos_count += 1
                elif r.sentiment_label == "NEGATIVE":
                    neg_count += 1
                else:
                    neu_count += 1
                    
                if r.sentiment_score is not None:
                    sentiments.append(r.sentiment_score)
                
            aspects = None
            if r.aspect_scores_json:
                try:
                    aspects = json.loads(r.aspect_scores_json)
                except Exception:
                    pass
            if not aspects:
                aspects = {"acting": 5.0, "story": 5.0, "music": 5.0, "visual_effects": 5.0, "direction": 5.0}
                
            if r.source != "YouTube":
                acting_sum += aspects.get("acting", 5.0)
                story_sum += aspects.get("story", 5.0)
                music_sum += aspects.get("music", 5.0)
                vfx_sum += aspects.get("visual_effects", 5.0)
                direction_sum += aspects.get("direction", 5.0)
            
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
                "source": r.source,
                "moderation": {
                    "is_spam": mod["is_spam"],
                    "is_bot": mod["is_bot"],
                    "spam_reasons": mod["spam_reasons"],
                    "spam_probability": mod["spam_probability"]
                }
            })
            
        spam_count = sum(1 for item in moderated_pool if item["is_spam"] and review_sources.get(item["id"]) != "YouTube")
        bot_count = sum(1 for item in moderated_pool if item["is_bot"] and review_sources.get(item["id"]) != "YouTube")
        duplicate_count = sum(1 for item in moderated_pool if "Duplicate review" in "".join(item["spam_reasons"]) and review_sources.get(item["id"]) != "YouTube")
        
        return {
            "reviews_formatted": reviews_formatted,
            "pos_count": pos_count,
            "neg_count": neg_count,
            "neu_count": neu_count,
            "sentiments": sentiments,
            "acting_sum": acting_sum,
            "story_sum": story_sum,
            "music_sum": music_sum,
            "vfx_sum": vfx_sum,
            "direction_sum": direction_sum,
            "spam_count": spam_count,
            "bot_count": bot_count,
            "duplicate_count": duplicate_count
        }

    proc_results = await asyncio.to_thread(process_reviews_and_moderation_sync, reviews)

    # Calculate sentiment polarity and overall stats
    sentiments = proc_results["sentiments"]
    avg_polarity = sum(sentiments) / len(sentiments) if sentiments else 0.0
    if avg_polarity > 0.15:
        overall_label = "POSITIVE"
    elif avg_polarity < -0.15:
        overall_label = "NEGATIVE"
    else:
        overall_label = "NEUTRAL"
        
    count = sum(1 for r in reviews if r.source != "YouTube")
    avg_aspects = {
        "acting": round(proc_results["acting_sum"] / count, 1) if count > 0 else 5.0,
        "story": round(proc_results["story_sum"] / count, 1) if count > 0 else 5.0,
        "music": round(proc_results["music_sum"] / count, 1) if count > 0 else 5.0,
        "visual_effects": round(proc_results["vfx_sum"] / count, 1) if count > 0 else 5.0,
        "direction": round(proc_results["direction_sum"] / count, 1) if count > 0 else 5.0
    }
    
    integrity_score = round(((count - proc_results["spam_count"]) / count) * 100, 1) if count > 0 else 100.0
    
    sentiment_report = {
        "movie_id": id,
        "reviews_analyzed": count,
        "positive_count": proc_results["pos_count"],
        "negative_count": proc_results["neg_count"],
        "neutral_count": proc_results["neu_count"],
        "average_sentiment_polarity": round(float(avg_polarity), 4),
        "overall_sentiment_label": overall_label,
        "average_aspect_scores": avg_aspects,
        "integrity_metrics": {
            "integrity_score": integrity_score,
            "spam_count": proc_results["spam_count"],
            "bot_flag_count": proc_results["bot_count"],
            "duplicate_count": proc_results["duplicate_count"]
        }
    }
    
    # 3. Calculate ratings/composite score in a separate thread
    db_rating = await asyncio.to_thread(
        lambda: db.query(Rating).filter(Rating.movie_id == id).first()
    )
    if not db_rating and db_movie:
        try:
            def upsert_rating_sync(db, db_movie):
                _cache_movie_if_needed(db, {
                    "id": db_movie.id,
                    "title": db_movie.title,
                    "overview": db_movie.overview,
                    "poster_path": db_movie.poster_path,
                    "release_date": db_movie.release_date,
                    "vote_average": db_movie.vote_average,
                    "imdb_rating": db_movie.imdb_rating,
                    "metacritic_score": db_movie.metacritic_score
                })
                return db.query(Rating).filter(Rating.movie_id == id).first()
            db_rating = await asyncio.to_thread(upsert_rating_sync, db, db_movie)
        except Exception:
            pass
            
    from app.services.scoring import calculate_normalized_weights
    
    imdb_score = db_rating.imdb_score if db_rating else (db_movie.imdb_rating if db_movie else None)
    tmdb_score = db_rating.tmdb_score if db_rating else (db_movie.vote_average if db_movie else None)
    metacritic_score = db_rating.metacritic_score if db_rating else (db_movie.metacritic_score if db_movie else None)
    sentiment_avg = db_rating.sentiment_avg if db_rating else avg_polarity
    rating_count = db_rating.rating_count if db_rating else count
    
    # NLP score is only available if the movie has actually been scraped and has reviews
    nlp_val = None
    if rating_count > 0 or len(reviews) > 0:
        nlp_val = 5.0 + (sentiment_avg * 5.0)
        nlp_val = max(0.0, min(10.0, nlp_val))
    
    yt_reviews = [r for r in reviews if r.source == "YouTube"]
    youtube_score = db_rating.youtube_score if db_rating else (sum(r.rating for r in yt_reviews) / len(yt_reviews) if yt_reviews else None)

    score, effective_weights, available, missing = calculate_normalized_weights(
        imdb_score,
        tmdb_score,
        metacritic_score,
        nlp_val,
        youtube_score
    )

    
    rating_report = {
        "movie_id": id,
        "imdb_score": imdb_score,
        "tmdb_score": tmdb_score,
        "metacritic_score": metacritic_score,
        "youtube_score": youtube_score,
        "sentiment_avg_polarity": sentiment_avg,
        "reviews_count": rating_count,
        "aggregate_hybrid_score": score,
        "effective_weights": effective_weights,
        "available_sources": available,
        "missing_sources": missing
    }
    
    # 4. Fetch aggregated recommendations
    from app.services.recommendation import recommendation_service
    recommendations_payload = await asyncio.to_thread(
        recommendation_service.get_netflix_recommendations, db, id
    )


    # 5. Build consolidated details object
    movie_details_data = {
        "id": db_movie.id if db_movie else id,
        "title": db_movie.title if db_movie else f"Movie {id}",
        "overview": db_movie.overview if db_movie else "",
        "poster_path": db_movie.poster_path if db_movie else None,
        "release_date": db_movie.release_date if db_movie else "",
        "genres": db_movie.genres if db_movie else [],
        "vote_average": db_movie.vote_average if db_movie else 0.0,
        "imdb_rating": db_movie.imdb_rating if db_movie else None,
        "metacritic_score": db_movie.metacritic_score if db_movie else None
    }

    return {
        "movie_details": movie_details_data,
        "reviews": {
            "movie_id": id,
            "movie_title": db_movie.title if db_movie else f"Movie {id}",
            "total_reviews": len(proc_results["reviews_formatted"]),
            "reviews": proc_results["reviews_formatted"]
        },
        "rating": rating_report,
        "sentiment": sentiment_report,
        "recommendations": recommendations_payload
    }

import os
import httpx
from fastapi import Response, HTTPException

# Shared global HTTPX client to pool connections, reuse sockets, and avoid handshake overhead
limits = httpx.Limits(max_keepalive_connections=50, max_connections=100)
http_client = httpx.AsyncClient(timeout=10.0, limits=limits)

# Persistent disk-based cache folder for proxied images
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "image_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

@router.get("/image-proxy")
async def image_proxy(path: str, size: str = "w300"):
    """
    Proxies TMDB image requests through the local backend to bypass ISP blocks
    on BunnyCDN (b-cdn.net) in certain regions, falling back to unblocked Amazon
    and Unsplash CDNs for local mock movies. Caches successfully fetched images on disk.
    """
    if not path:
        raise HTTPException(status_code=400, detail="Path parameter is required")

    if not path.startswith("/"):
        path = "/" + path

    path_lower = path.lower()
    is_backdrop = size in ["w780", "w1280", "original"]

    # Construct safe filename and check disk cache first
    safe_path = path_lower.replace("/", "_").replace("\\", "_")
    cache_filepath = os.path.join(CACHE_DIR, f"{size}_{safe_path}")
    
    if os.path.exists(cache_filepath):
        try:
            with open(cache_filepath, "rb") as f:
                content = f.read()
            content_type = "image/png" if cache_filepath.endswith(".png") else "image/jpeg"
            return Response(content=content, media_type=content_type)
        except Exception as cache_err:
            print(f"[Image Proxy] Disk cache read failed: {cache_err}")

    # Corrected high-quality unblocked poster mappings (Amazon and Unsplash CDNs)
    mock_posters = {
        "/geu2qvh353ego3t8voie6qi4tju.jpg": "https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg",
        "/o062xtc3n4c73njgf95si6tas2t.jpg": "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg",
        "/9gk7adhyezcewtvfsh5ttjzqbci.jpg": "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg",
        "/qj2twgbcqb6tsv1wy3nfkvvsm4c.jpg": "https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg",
        "/d5i2fs3hsyrv2jifdugzakp9t8.jpg": "https://m.media-amazon.com/images/M/MV5BMzc2MjM0NTMtOGY4NC00NzY1LWE2ODUtZjMzY2RhNGNkZDAyXkEyXkFqcGc@._V1_SX300.jpg",
        "/d5i2fs3hsyrv2jifdugza6kp9t8.jpg": "https://m.media-amazon.com/images/M/MV5BMzc2MjM0NTMtOGY4NC00NzY1LWE2ODUtZjMzY2RhNGNkZDAyXkEyXkFqcGc@._V1_SX300.jpg",
        "/f89uwz6v2jbnrfsx74j0jqrpe9.jpg": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=500",
        "/arw27qpwzwcyvtdjs7gib0wlhqa.jpg": "https://m.media-amazon.com/images/M/MV5BNWIwODRlZTUtY2U3ZS00Yzg1LWJhNzYtMmZiYmEyNmU1NjMzXkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1_SX300.jpg",
        "/3bhkrj6pjoqabnmr42gkxycjggj.jpg": "https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmUtYTAwNi00MTYxLWJmNWYtYzZlODY3ZTk3OTFlXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_.jpg",
        "/o0o0qq0unzgzs2e5vpuq875ndr2.jpg": "https://m.media-amazon.com/images/M/MV5BMTUxMzQyNjA5MF5BMl5BanBnXkFtZTYwOTU2NTY3._V1_.jpg",
        "/x2fiacr26zbgd2w2o20v2sau6r0.jpg": "https://images.unsplash.com/photo-1454789548928-9efd52dc4031?q=80&w=500",
        "/f89u3wz6v2jbnrfsx74j0jqrpe9.jpg": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=500",
    }

    # Corrected high-quality unblocked backdrop mappings (Unsplash CDN)
    mock_backdrops = {
        "/geu2qvh353ego3t8voie6qi4tju.jpg": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1280",
        "/o062xtc3n4c73njgf95si6tas2t.jpg": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?q=80&w=1280",
        "/9gk7adhyezcewtvfsh5ttjzqbci.jpg": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?q=80&w=1280",
        "/qj2twgbcqb6tsv1wy3nfkvvsm4c.jpg": "https://images.unsplash.com/photo-1509248961158-e54f6934749c?q=80&w=1280",
        "/d5i2fs3hsyrv2jifdugzakp9t8.jpg": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1280",
        "/d5i2fs3hsyrv2jifdugza6kp9t8.jpg": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1280",
        "/f89uwz6v2jbnrfsx74j0jqrpe9.jpg": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=1280",
        "/arw27qpwzwcyvtdjs7gib0wlhqa.jpg": "https://images.unsplash.com/photo-1448375240586-882707db888b?q=80&w=1280",
        "/3bhkrj6pjoqabnmr42gkxycjggj.jpg": "https://images.unsplash.com/photo-1543536448-d209d2d13a1c?q=80&w=1280",
        "/o0o0qq0unzgzs2e5vpuq875ndr2.jpg": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=1280",
        "/x2fiacr26zbgd2w2o20v2sau6r0.jpg": "https://images.unsplash.com/photo-1454789548928-9efd52dc4031?q=80&w=1280",
        "/f89u3wz6v2jbnrfsx74j0jqrpe9.jpg": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=1280",
    }

    url = f"https://image.tmdb.org/t/p/{size}{path}"
    
    # Try fetching from mapped unblocked URLs first
    target_url = None
    if is_backdrop and path_lower in mock_backdrops:
        target_url = mock_backdrops[path_lower]
    elif path_lower in mock_posters:
        target_url = mock_posters[path_lower]

    if target_url:
        try:
            # Fetch using shared AsyncClient connection pool
            response = await http_client.get(target_url)
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "image/jpeg")
                # Store in disk cache
                try:
                    with open(cache_filepath, "wb") as f:
                        f.write(response.content)
                except Exception as cache_err:
                    print(f"[Image Proxy] Disk cache write failed: {cache_err}")
                return Response(content=response.content, media_type=content_type)
            else:
                print(f"[Image Proxy] Mapped url returned {response.status_code} for {target_url}")
        except Exception as ex:
            print(f"[Image Proxy] Mapped fetch failed for {target_url}: {ex}")
            
        raise HTTPException(status_code=404, detail="Mock image source not reachable")

    # Fallback to standard TMDb request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        # Fetch using shared AsyncClient connection pool
        response = await http_client.get(url, headers=headers)
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "image/jpeg")
            # Store in disk cache
            try:
                with open(cache_filepath, "wb") as f:
                    f.write(response.content)
            except Exception as cache_err:
                print(f"[Image Proxy] Disk cache write failed: {cache_err}")
            return Response(content=response.content, media_type=content_type)
        else:
            raise HTTPException(status_code=response.status_code, detail="TMDb image not found")
    except Exception as e:
        print(f"[Image Proxy] Error fetching image {url}: {e}")
        raise HTTPException(status_code=502, detail="Failed to fetch image from TMDb CDN")


