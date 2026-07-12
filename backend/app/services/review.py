# review.py
# Service layer module encapsulating business logic operations for reviews and rating aggregates.

import json
from sqlalchemy.orm import Session
from app.models.review import Review
from app.models.rating import Rating
from app.schemas.review import ReviewCreate, ReviewUpdate
from app.repositories import ReviewRepository, RatingRepository, MovieRepository
from app.sentiment.analyzer import sentiment_service
from fastapi import HTTPException, status

class ReviewService:
    @staticmethod
    def update_rating_statistics(db: Session, movie_id: int):
        """
        Recalculates review count and sentiment averages in the ratings table,
        generating a dynamic weighted aggregate score.
        """
        from app.services.scoring import calculate_normalized_weights
        
        all_reviews = ReviewRepository.get_by_movie(db, movie_id)
        count = len(all_reviews)
        
        # Exclude YouTube comments from general web sentiment to prevent double-counting
        general_reviews = [r for r in all_reviews if r.source != "YouTube"]
        sentiments = [r.sentiment_score for r in general_reviews if r.sentiment_score is not None]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
        
        db_rating = RatingRepository.get_by_movie_id(db, movie_id)
        movie_record = MovieRepository.get_by_id(db, movie_id)
        
        # Calculate YouTube rating from YouTube source comments
        yt_reviews = [r for r in all_reviews if r.source == "YouTube"]
        youtube_score = sum(r.rating for r in yt_reviews) / len(yt_reviews) if yt_reviews else (db_rating.youtube_score if db_rating else None)
        
        tmdb_val = movie_record.vote_average if movie_record else 0.0
        imdb_val = movie_record.imdb_rating if movie_record else None
        metacritic_val = movie_record.metacritic_score if movie_record else None
        
        nlp_rating = 5.0 + (avg_sentiment * 5.0)
        nlp_rating = max(0.0, min(10.0, nlp_rating))
        
        aggregate, _, _, _ = calculate_normalized_weights(imdb_val, tmdb_val, metacritic_val, nlp_rating, youtube_score)
        
        if not db_rating:
            db_rating = Rating(
                movie_id=movie_id,
                imdb_score=imdb_val,
                tmdb_score=tmdb_val,
                metacritic_score=metacritic_val,
                youtube_score=youtube_score,
                aggregate_score=aggregate,
                sentiment_avg=round(float(avg_sentiment), 4),
                rating_count=count
            )
            RatingRepository.create(db, db_rating)
        else:
            db_rating.imdb_score = imdb_val
            db_rating.tmdb_score = tmdb_val
            db_rating.metacritic_score = metacritic_val
            db_rating.youtube_score = youtube_score
            db_rating.sentiment_avg = round(float(avg_sentiment), 4)
            db_rating.rating_count = count
            db_rating.aggregate_score = aggregate
            RatingRepository.commit(db)

    @staticmethod
    def create_review(db: Session, user_id: int, review_in: ReviewCreate) -> Review:
        """
        Creates a new review, runs NLP sentiment analysis, and updates rating stats.
        """
        existing_review = ReviewRepository.get_by_user_and_movie(db, user_id, review_in.movie_id)
        if existing_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already submitted a review for this movie. Use PUT to edit it."
            )
            
        sentiment = sentiment_service.analyze_text(review_in.review_text)
        polarity = sentiment["positive_score"] - sentiment["negative_score"]
        aspects = sentiment_service.analyze_aspects(review_in.review_text)
        
        db_review = Review(
            user_id=user_id,
            movie_id=review_in.movie_id,
            rating=review_in.rating,
            review_text=review_in.review_text,
            sentiment_score=round(float(polarity), 4),
            sentiment_label=sentiment["final_sentiment"],
            aspect_scores_json=json.dumps(aspects)
        )
        ReviewRepository.create(db, db_review)
        
        try:
            ReviewService.update_rating_statistics(db, review_in.movie_id)
        except Exception:
            pass
            
        try:
            from app.services.recommendation import recommendation_service
            int_type = "like" if review_in.rating >= 7.0 else "view"
            recommendation_service.log_user_interaction(db, user_id, review_in.movie_id, int_type)
        except Exception:
            pass
            
        return db_review

    @staticmethod
    def update_review(db: Session, review_id: int, user_id: int, review_in: ReviewUpdate) -> Review:
        """
        Modifies an existing review's comments and rating, recalculating sentiment.
        """
        db_review = ReviewRepository.get_by_id(db, review_id)
        if not db_review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )
        if db_review.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update this review"
            )
            
        if review_in.rating is not None:
            db_review.rating = review_in.rating
        if review_in.review_text is not None:
            db_review.review_text = review_in.review_text
            sentiment = sentiment_service.analyze_text(review_in.review_text)
            polarity = sentiment["positive_score"] - sentiment["negative_score"]
            db_review.sentiment_score = round(float(polarity), 4)
            db_review.sentiment_label = sentiment["final_sentiment"]
            
        ReviewRepository.commit(db)
        
        try:
            ReviewService.update_rating_statistics(db, db_review.movie_id)
        except Exception:
            pass
            
        return db_review

    @staticmethod
    def delete_review(db: Session, review_id: int, user_id: int):
        """
        Removes a review and updates movie rating averages.
        """
        db_review = ReviewRepository.get_by_id(db, review_id)
        if not db_review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )
        if db_review.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to delete this review"
            )
            
        movie_id = db_review.movie_id
        ReviewRepository.delete(db, db_review)
        
        try:
            ReviewService.update_rating_statistics(db, movie_id)
        except Exception:
            pass
