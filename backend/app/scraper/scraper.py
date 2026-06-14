import asyncio
from typing import List, Dict, Any, Optional
from app.scraper.imdb import imdb_scraper
from app.scraper.reddit import reddit_scraper
from app.scraper.letterboxd import letterboxd_scraper
from app.scraper.rotten_tomatoes import rotten_tomatoes_scraper
from app.scraper.youtube import youtube_scraper
from app.sentiment.analyzer import sentiment_service

class UnifiedMovieScraper:
    """
    Orchestrates and aggregates scraped user/critic reviews from five major platforms:
    - IMDb (User reviews)
    - Reddit (Fan discussions comments)
    - Letterboxd (Cinephile star-rating reviews)
    - Rotten Tomatoes (Critic reviews quotes)
    - YouTube (Trailer comment reaction sentiment reviews)
    
    Grading all scraped materials with automated Hugging Face sentiment scores,
    and dynamically converting sentiment classifications into movie ratings (1-10) for unrated content.
    """
    async def scrape_reviews_for_movie(self, movie_title: str, imdb_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Gathers reviews from all five external platforms, runs sentiment analysis,
        and returns a unified aggregated list of reviews.
        """
        aggregated_reviews = []
        
        # Concurrently call all five scrapers in separate threads to avoid blocking the async loop
        imdb_task = asyncio.to_thread(imdb_scraper.scrape_reviews, movie_title, imdb_id)
        reddit_task = asyncio.to_thread(reddit_scraper.scrape_reviews, movie_title)
        letterboxd_task = asyncio.to_thread(letterboxd_scraper.scrape_reviews, movie_title)
        rt_task = asyncio.to_thread(rotten_tomatoes_scraper.scrape_reviews, movie_title)
        youtube_task = asyncio.to_thread(youtube_scraper.scrape_reviews, movie_title)
        
        results = await asyncio.gather(imdb_task, reddit_task, letterboxd_task, rt_task, youtube_task, return_exceptions=True)
        
        # 1. Fetch from IMDb
        if not isinstance(results[0], Exception):
            aggregated_reviews.extend(results[0])
        else:
            print(f"IMDb aggregator failed: {results[0]}")
            
        # 2. Fetch from Reddit
        if not isinstance(results[1], Exception):
            aggregated_reviews.extend(results[1])
        else:
            print(f"Reddit aggregator failed: {results[1]}")
            
        # 3. Fetch from Letterboxd
        if not isinstance(results[2], Exception):
            aggregated_reviews.extend(results[2])
        else:
            print(f"Letterboxd aggregator failed: {results[2]}")
            
        # 4. Fetch from Rotten Tomatoes
        if not isinstance(results[3], Exception):
            aggregated_reviews.extend(results[3])
        else:
            print(f"Rotten Tomatoes aggregator failed: {results[3]}")
            
        # 5. Fetch from YouTube
        if not isinstance(results[4], Exception):
            aggregated_reviews.extend(results[4])
        else:
            print(f"YouTube aggregator failed: {results[4]}")
            
        # 6. Process merged list and compute sentiment metrics concurrently in a thread pool
        async def process_review(review):
            sentiment = await asyncio.to_thread(sentiment_service.analyze_text, review["text"])
            scraped_rating = review.get("rating")
            if scraped_rating is None or review["source"] == "Reddit" or review["source"] == "YouTube":
                scraped_rating = sentiment_service.convert_sentiment_to_rating(sentiment)
                
            polarity = sentiment["positive_score"] - sentiment["negative_score"]
            return {
                "reviewer": review["author"],
                "scraped_rating": scraped_rating,
                "review_text": review["text"],
                "source": review["source"],
                "sentiment_score": round(float(polarity), 4),
                "sentiment_label": sentiment["final_sentiment"]
            }

        tasks = [process_review(r) for r in aggregated_reviews]
        unified_results = await asyncio.gather(*tasks)
        return list(unified_results)

# Instantiate service singleton
movie_scraper = UnifiedMovieScraper()
