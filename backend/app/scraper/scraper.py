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
        aggregated_reviews = []
        
        # 1. Fetch from IMDb
        try:
            imdb_reviews = imdb_scraper.scrape_reviews(movie_title, imdb_id)
            aggregated_reviews.extend(imdb_reviews)
        except Exception as e:
            print(f"IMDb aggregator failed: {e}")
            
        # 2. Fetch from Reddit
        try:
            reddit_reviews = reddit_scraper.scrape_reviews(movie_title)
            aggregated_reviews.extend(reddit_reviews)
        except Exception as e:
            print(f"Reddit aggregator failed: {e}")
            
        # 3. Fetch from Letterboxd
        try:
            letterboxd_reviews = letterboxd_scraper.scrape_reviews(movie_title)
            aggregated_reviews.extend(letterboxd_reviews)
        except Exception as e:
            print(f"Letterboxd aggregator failed: {e}")
            
        # 4. Fetch from Rotten Tomatoes
        try:
            rt_reviews = rotten_tomatoes_scraper.scrape_reviews(movie_title)
            aggregated_reviews.extend(rt_reviews)
        except Exception as e:
            print(f"Rotten Tomatoes aggregator failed: {e}")
            
        # 5. Process merged list and compute sentiment metrics
        unified_results = []
        for review in aggregated_reviews:
            sentiment = sentiment_service.analyze_text(review["text"])
            
            # If the source is Reddit (lacks explicit ratings), dynamically convert sentiment to a rating!
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
                "sentiment_label": sentiment["final_sentiment"]
            })
            
        return unified_results

# Instantiate service singleton
movie_scraper = UnifiedMovieScraper()
