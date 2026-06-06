from typing import List, Dict, Any, Optional
from app.scraper.imdb import imdb_scraper
from app.scraper.reddit import reddit_scraper
from app.scraper.letterboxd import letterboxd_scraper
from app.scraper.rotten_tomatoes import rotten_tomatoes_scraper
from app.sentiment.analyzer import sentiment_service

class UnifiedMovieScraper:
    """
    Orchestrates and aggregates scraped user/critic reviews from four major platforms:
    - IMDb (User reviews)
    - Reddit (Fan discussions comments)
    - Letterboxd (Cinephile star-rating reviews)
    - Rotten Tomatoes (Critic reviews quotes)
    
    Grading all scraped materials with automated Hugging Face sentiment scores,
    and dynamically converting sentiment classifications into movie ratings (1-10) for unrated content.
    """
    async def scrape_reviews_for_movie(self, movie_title: str, imdb_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Gathers reviews from all four external platforms, runs sentiment analysis,
        and returns a unified aggregated list of reviews.
        """
        import asyncio
        
        # Gather reviews concurrently from all scrapers
        tasks = [
            imdb_scraper.scrape_reviews(movie_title, imdb_id),
            reddit_scraper.scrape_reviews(movie_title),
            letterboxd_scraper.scrape_reviews(movie_title),
            rotten_tomatoes_scraper.scrape_reviews(movie_title)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        imdb_res = results[0] if not isinstance(results[0], Exception) else []
        reddit_res = results[1] if not isinstance(results[1], Exception) else []
        letterboxd_res = results[2] if not isinstance(results[2], Exception) else []
        rt_res = results[3] if not isinstance(results[3], Exception) else []
        
        aggregated_reviews = []
        if imdb_res: aggregated_reviews.extend(imdb_res)
        if reddit_res: aggregated_reviews.extend(reddit_res)
        if letterboxd_res: aggregated_reviews.extend(letterboxd_res)
        if rt_res: aggregated_reviews.extend(rt_res)
            
        # Process merged list and compute sentiment metrics
        unified_results = []
        for review in aggregated_reviews:
            sentiment = sentiment_service.analyze_text(review["text"])
            aspects = sentiment_service.analyze_aspects(review["text"])
            
            # If the source is Reddit (lacks explicit ratings), dynamically convert sentiment to a rating
            scraped_rating = review.get("rating")
            if scraped_rating is None or review["source"] == "Reddit":
                scraped_rating = sentiment_service.convert_sentiment_to_rating(sentiment)
                
            polarity = sentiment["positive_score"] - sentiment["negative_score"]
            unified_results.append({
                "reviewer": review["author"],
                "scraped_rating": scraped_rating,
                "review_text": review["text"],
                "source": review["source"],
                "sentiment_score": round(float(polarity), 4),
                "sentiment_label": sentiment["final_sentiment"],
                "aspect_scores": aspects
            })
            
        return unified_results
# Instantiate service singleton
movie_scraper = UnifiedMovieScraper()
