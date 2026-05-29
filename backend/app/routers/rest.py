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
    try:
        if query:
            data = await tmdb_service.search_movies(query=query, page=page)
        else:
            data = await tmdb_service.get_popular_movies(page=page)
            
        # Cache results in local database
        for m in data.get("results", []):
            try:
                _cache_movie_if_needed(db, m)
            except Exception:
                pass
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
    try:
        data = await tmdb_service.get_movie_details(movie_id=id)
        _cache_movie_if_needed(db, data)
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
    
    # Run review pool moderation checks
    moderated_pool = review_moderation_service.analyze_review_pool(reviews)
    moderated_map = {item["id"]: item for item in moderated_pool}
    
    reviews_formatted = []
    for r in reviews:
        aspects = sentiment_service.analyze_aspects(r.review_text)
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
        aspects = sentiment_service.analyze_aspects(r.review_text)
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
                })
                db_rating = db.query(Rating).filter(Rating.movie_id == movie).first()
            except Exception:
                pass
                
    if not db_rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rating score metrics could not be resolved for movie ID {movie}"
        )
        
    return {
        "movie_id": movie,
        "movie_title": db_movie.title if db_movie else f"Movie {movie}",
        "imdb_score": db_rating.imdb_score,
        "tmdb_score": db_rating.tmdb_score,
        "metacritic_score": db_rating.metacritic_score,
        "sentiment_avg_polarity": db_rating.sentiment_avg,
        "reviews_count": db_rating.rating_count,
        "aggregate_hybrid_score": db_rating.aggregate_score,
        "formula": "FinalScore = 0.4(IMDb) + 0.2(TMDb) + 0.1(Metacritic) + 0.3(NLPReviewScore)"
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


