# movie.py
# Service layer module encapsulating core movie metadata lifecycle and scrapers execution.

import asyncio
from sqlalchemy.orm import Session
from app.models.movie import Movie
from app.models.rating import Rating
from app.models.review import Review
from app.repositories import MovieRepository, RatingRepository, ReviewRepository
from app.services.tmdb import tmdb_service, GENRE_MAP
from app.scraper.scraper import movie_scraper
from fastapi import HTTPException, status
import json

class MovieService:
    @staticmethod
    def calculate_hybrid_score(imdb: float, tmdb: float, metacritic: float, sentiment_avg: float, youtube_score: float = None) -> float:
        """
        Dynamically calculates composite ratings using weighting algorithms.
        """
        from app.routers.movies import _calculate_hybrid_score
        return _calculate_hybrid_score(imdb, tmdb, metacritic, sentiment_avg, youtube_score)

    @staticmethod
    def cache_movie_if_needed(db: Session, movie_details: dict, fetch_transcript: bool = False) -> Movie:
        """
        Caches raw API payload metadata persistently into local schemas.
        """
        movie_id = movie_details.get("id")
        if not movie_id:
            return None
            
        db_movie = MovieRepository.get_by_id(db, movie_id)
        
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

        video_key = movie_details.get("youtube_video_key")
        transcript_val = movie_details.get("trailer_transcript")
        if transcript_val is None:
            if db_movie and db_movie.trailer_transcript:
                transcript_val = db_movie.trailer_transcript
            elif fetch_transcript:
                from app.scraper.youtube import youtube_scraper
                transcript_val = youtube_scraper.fetch_trailer_transcript(video_key, movie_details.get("title"))

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
                metacritic_score=metacritic_val,
                trailer_transcript=transcript_val
            )
            MovieRepository.create(db, db_movie)
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
            if transcript_val is not None:
                db_movie.trailer_transcript = transcript_val
            MovieRepository.commit(db)

        # Upsert 'ratings' table record
        db_rating = RatingRepository.get_by_movie_id(db, movie_id)
        
        tmdb_score = db_movie.vote_average
        imdb_score = db_movie.imdb_rating
        metacritic_score = db_movie.metacritic_score
        
        sentiment_avg = db_rating.sentiment_avg if db_rating else 0.0
        rating_count = db_rating.rating_count if db_rating else 0
        
        youtube_val = movie_details.get("youtube_score")
        youtube_score = youtube_val if youtube_val is not None else (db_rating.youtube_score if db_rating else None)
        if youtube_score is not None:
            youtube_score = float(youtube_score)
            
        aggregate = MovieService.calculate_hybrid_score(imdb_score, tmdb_score, metacritic_score, sentiment_avg, youtube_score)

        if not db_rating:
            db_rating = Rating(
                movie_id=movie_id,
                imdb_score=imdb_score,
                tmdb_score=tmdb_score,
                metacritic_score=metacritic_score,
                youtube_score=youtube_score,
                aggregate_score=aggregate,
                rating_count=rating_count,
                sentiment_avg=sentiment_avg
            )
            RatingRepository.create(db, db_rating)
        else:
            db_rating.imdb_score = imdb_score
            db_rating.tmdb_score = tmdb_score
            db_rating.metacritic_score = metacritic_score
            db_rating.youtube_score = youtube_score
            db_rating.aggregate_score = aggregate
            RatingRepository.commit(db)
            
        try:
            from app.services.recommendation import recommendation_service
            recommendation_service.generate_embeddings_for_movie_if_needed(db, db_movie)
        except Exception as emb_error:
            print(f"[MovieService] Failed to generate embeddings for movie {movie_id}: {emb_error}")
            
        return db_movie

    @staticmethod
    async def get_popular_movies(db: Session, page: int = 1) -> dict:
        """
        Retrieves a paginated list of popular movies from TMDb and caches them.
        """
        try:
            data = await tmdb_service.get_popular_movies(page=page)
            def cache_movies_sync(db, movies):
                for m in movies:
                    try:
                        MovieService.cache_movie_if_needed(db, m)
                    except Exception:
                        pass
            await asyncio.to_thread(cache_movies_sync, db, data.get("results", []))
            return data
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching popular movies: {str(e)}"
            )

    @staticmethod
    async def search_movies(db: Session, query: str, page: int = 1) -> dict:
        """
        Searches movies matching query from TMDb and caches results.
        """
        try:
            data = await tmdb_service.search_movies(query=query, page=page)
            def cache_movies_sync(db, movies):
                for m in movies:
                    try:
                        MovieService.cache_movie_if_needed(db, m)
                    except Exception:
                        pass
            await asyncio.to_thread(cache_movies_sync, db, data.get("results", []))
            return data
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error searching movies: {str(e)}"
            )

    @staticmethod
    async def get_movie_details(db: Session, movie_id: int) -> dict:
        """
        Retrieves detailed movie metadata. Checks database cache first, falling back to TMDb API.
        """
        db_movie = await asyncio.to_thread(MovieRepository.get_by_id, db, movie_id)
        
        def is_mock_movie(movie) -> bool:
            if not movie:
                return True
            if movie.title and movie.title.startswith("Mock Movie "):
                return True
            if movie.overview and "placeholder description for mock movie" in movie.overview:
                return True
            return False

        if db_movie and db_movie.imdb_rating is not None and not is_mock_movie(db_movie):
            if not db_movie.trailer_transcript:
                def fetch_and_save_transcript(db, movie):
                    from app.scraper.youtube import youtube_scraper
                    movie.trailer_transcript = youtube_scraper.fetch_trailer_transcript(None, movie.title)
                    db.commit()
                await asyncio.to_thread(fetch_and_save_transcript, db, db_movie)
                
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
            data = await tmdb_service.get_movie_details(movie_id=movie_id)
            await asyncio.to_thread(MovieService.cache_movie_if_needed, db, data, True)
            return data
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Movie with ID {movie_id} could not be found: {str(e)}"
            )

    @staticmethod
    async def get_scraped_reviews(db: Session, movie_id: int) -> dict:
        """
        Triggers unified reviews scrapers across social media sites, running NLP sentiment.
        """
        movie = await asyncio.to_thread(MovieRepository.get_by_id, db, movie_id)
        if not movie:
            try:
                movie_data = await tmdb_service.get_movie_details(movie_id=movie_id)
                await asyncio.to_thread(MovieService.cache_movie_if_needed, db, movie_data, True)
                title = movie_data["title"]
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Movie details not cached and could not be fetched for ID {movie_id}"
                )
        else:
            title = movie.title
            if not movie.trailer_transcript:
                def fetch_and_save_transcript(db, movie):
                    from app.scraper.youtube import youtube_scraper
                    movie.trailer_transcript = youtube_scraper.fetch_trailer_transcript(None, movie.title)
                    db.commit()
                await asyncio.to_thread(fetch_and_save_transcript, db, movie)
                
        scraped_reviews = await movie_scraper.scrape_reviews_for_movie(title)
        
        def fetch_existing_reviewers(db, movie_id):
            return set(
                row[0] for row in db.query(Review.author).filter(
                    Review.movie_id == movie_id,
                    Review.is_scraped == True,
                    Review.source != "YouTube"
                ).all()
            )
        existing_reviewers = await asyncio.to_thread(fetch_existing_reviewers, db, movie_id)
        
        new_reviews = [r for r in scraped_reviews if r["reviewer"] not in existing_reviewers]
        
        if new_reviews:
            from app.sentiment.analyzer import sentiment_service
            
            async def process_new_review(r):
                aspects = await asyncio.to_thread(sentiment_service.analyze_aspects, r["review_text"])
                return r, aspects

            tasks = [process_new_review(r) for r in new_reviews]
            results = await asyncio.gather(*tasks)
            
            def save_reviews_and_update_stats(db, movie_id, results):
                db.query(Review).filter(
                    Review.movie_id == movie_id,
                    Review.source == "YouTube"
                ).delete()
                db.commit()
                
                for r, aspects in results:
                    db_review = Review(
                        movie_id=movie_id,
                        rating=r["scraped_rating"],
                        review_text=r["review_text"],
                        sentiment_score=r["sentiment_score"],
                        sentiment_label=r["sentiment_label"],
                        is_scraped=True,
                        author=r["reviewer"],
                        source=r["source"],
                        aspect_scores_json=json.dumps(aspects)
                    )
                    db.add(db_review)
                db.commit()
                
                from app.services.review import ReviewService
                try:
                    ReviewService.update_rating_statistics(db, movie_id)
                except Exception:
                    pass
            await asyncio.to_thread(save_reviews_and_update_stats, db, movie_id, results)
            
        return {
            "movie_id": movie_id,
            "movie_title": title,
            "reviews_scraped": len(scraped_reviews),
            "reviews": scraped_reviews
        }
