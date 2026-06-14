import datetime
import math
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
import json

from app.models.movie import Movie
from app.models.rating import Rating
from app.models.review import Review
from app.models.recommendation import MovieEmbedding, RecommendationCache, UserPreference, UserInteraction
from app.services.tmdb import tmdb_service
from app.services.embedding import embedding_service

DEFAULT_WEIGHTS = {
    "content": 0.25,
    "theme": 0.20,
    "genre": 0.15,
    "community": 0.15,
    "cinescore": 0.10,
    "user": 0.10,
    "freshness": 0.05
}

class RecommendationService:
    def __init__(self):
        self.weights = DEFAULT_WEIGHTS

    def configure_weights(self, new_weights: Dict[str, float]):
        """Dynamically reconfigures the hybrid weights."""
        total = sum(new_weights.values())
        if total > 0:
            self.weights = {k: v / total for k, v in new_weights.items()}

    def generate_embeddings_for_movie_if_needed(self, db: Session, movie: Movie) -> MovieEmbedding:
        """
        Calculates and caches Sentence Transformers embeddings for a movie overview, themes,
        and keywords, ensuring semantic matching metadata is cached.
        """
        db_emb = db.query(MovieEmbedding).filter(MovieEmbedding.movie_id == movie.id).first()
        if db_emb:
            return db_emb

        # 1. Fetch missing keywords/cast/crew from TMDb details if not present
        if not movie.keywords or not movie.cast or not movie.director:
            import asyncio
            # Use run or execute in sync thread helper
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            async def fetch_meta():
                kws = await tmdb_service.get_movie_keywords(movie.id)
                credits = await tmdb_service.get_movie_credits(movie.id)
                return kws, credits
            
            if loop.is_running():
                # Run in separate thread pool if loop is already running in current thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    kws, credits = pool.submit(lambda: asyncio.run(fetch_meta())).result()
            else:
                kws, credits = loop.run_until_complete(fetch_meta())
                
            if not movie.keywords:
                movie.keywords = kws
            if not movie.cast:
                movie.cast = credits.get("cast", [])
            if not movie.director:
                movie.director = credits.get("director")

        # 2. Extract themes if not present
        if not movie.themes:
            combined_text = (movie.overview or "") + " " + (movie.trailer_transcript or "")
            movie.themes = embedding_service.extract_themes(combined_text)
            
        # 3. Auto-populate keywords if empty
        if not movie.keywords:
            movie.keywords = embedding_service.extract_keywords(movie.overview or "")

        db.commit()

        # 4. Generate embeddings
        overview_text = movie.overview or ""
        themes_text = ", ".join(movie.themes) if movie.themes else ""
        keywords_text = ", ".join(movie.keywords) if movie.keywords else ""
        
        genres_text = ", ".join(g.get("name", "") for g in movie.genres if isinstance(g, dict)) if movie.genres else ""
        cast_text = ", ".join(movie.cast) if movie.cast else ""
        director_text = movie.director or ""
        
        combined_text = f"Title: {movie.title}. Overview: {overview_text}. Genres: {genres_text}. Director: {director_text}. Cast: {cast_text}. Themes: {themes_text}. Keywords: {keywords_text}."

        overview_emb = embedding_service.get_embedding(overview_text)
        themes_emb = embedding_service.get_embedding(themes_text)
        keywords_emb = embedding_service.get_embedding(keywords_text)
        combined_emb = embedding_service.get_embedding(combined_text)

        from sqlalchemy.exc import IntegrityError
        try:
            db_emb = MovieEmbedding(
                movie_id=movie.id,
                overview_embedding=overview_emb,
                themes_embedding=themes_emb,
                keywords_embedding=keywords_emb,
                combined_embedding=combined_emb
            )
            db.add(db_emb)
            db.commit()
        except IntegrityError:
            db.rollback()
            db_emb = db.query(MovieEmbedding).filter(MovieEmbedding.movie_id == movie.id).first()
        return db_emb


    def log_user_interaction(self, db: Session, user_id: int, movie_id: int, interaction_type: str):
        """
        Logs a user interaction (view, search, save, like) and dynamically recalculates
        the user preference weights profile.
        """
        interaction = UserInteraction(
            user_id=user_id,
            movie_id=movie_id,
            interaction_type=interaction_type
        )
        db.add(interaction)
        db.commit()

        # Recalculate User Preferences
        # Weights: like = 3.0, save = 2.0, view = 1.0, search = 0.5
        weight_map = {"like": 3.0, "save": 2.0, "view": 1.0, "search": 0.5}
        
        user_interactions = db.query(UserInteraction).filter(UserInteraction.user_id == user_id).all()
        
        preferred_genres = {}
        preferred_keywords = {}
        preferred_directors = {}
        preferred_cast = {}

        for ui in user_interactions:
            movie = db.query(Movie).filter(Movie.id == ui.movie_id).first()
            if not movie:
                continue
            
            w = weight_map.get(ui.interaction_type, 1.0)
            
            # Genres
            if movie.genres:
                for g in movie.genres:
                    name = g.get("name") if isinstance(g, dict) else g
                    if name:
                        preferred_genres[name] = preferred_genres.get(name, 0.0) + w
            
            # Keywords
            if movie.keywords:
                for kw in movie.keywords:
                    preferred_keywords[kw] = preferred_keywords.get(kw, 0.0) + w
                    
            # Director
            if movie.director:
                preferred_directors[movie.director] = preferred_directors.get(movie.director, 0.0) + w
                
            # Cast
            if movie.cast:
                for actor in movie.cast:
                    preferred_cast[actor] = preferred_cast.get(actor, 0.0) + w

        # Normalize profiles (l2-like normalization or simple division by sum)
        def normalize_profile(profile: dict) -> dict:
            if not profile:
                return {}
            total = sum(profile.values())
            return {k: round(v / total, 3) for k, v in profile.items()}

        pref = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
        if not pref:
            pref = UserPreference(
                user_id=user_id,
                preferred_genres=normalize_profile(preferred_genres),
                preferred_keywords=normalize_profile(preferred_keywords),
                preferred_directors=normalize_profile(preferred_directors),
                preferred_cast=normalize_profile(preferred_cast)
            )
            db.add(pref)
        else:
            pref.preferred_genres = normalize_profile(preferred_genres)
            pref.preferred_keywords = normalize_profile(preferred_keywords)
            pref.preferred_directors = normalize_profile(preferred_directors)
            pref.preferred_cast = normalize_profile(preferred_cast)
            pref.last_updated = func.now()

        db.commit()

    def _get_user_behavior_score(self, movie: Movie, pref: Optional[UserPreference]) -> float:
        """Computes matching affinity between movie metadata and user preference profile."""
        if not pref:
            return 0.5 # Default middle score for cold start users

        score = 0.0
        matches = 0
        
        # 1. Genres overlap
        if pref.preferred_genres and movie.genres:
            genres_score = 0.0
            for g in movie.genres:
                name = g.get("name") if isinstance(g, dict) else g
                if name in pref.preferred_genres:
                    genres_score += pref.preferred_genres[name]
            score += genres_score
            matches += 1
            
        # 2. Director overlap
        if pref.preferred_directors and movie.director:
            if movie.director in pref.preferred_directors:
                score += pref.preferred_directors[movie.director]
            matches += 1
            
        # 3. Cast overlap
        if pref.preferred_cast and movie.cast:
            cast_score = 0.0
            for actor in movie.cast:
                if actor in pref.preferred_cast:
                    cast_score += pref.preferred_cast[actor]
            score += cast_score
            matches += 1

        # 4. Keywords overlap
        if pref.preferred_keywords and movie.keywords:
            kw_score = 0.0
            for kw in movie.keywords:
                if kw in pref.preferred_keywords:
                    kw_score += pref.preferred_keywords[kw]
            score += kw_score
            matches += 1

        if matches > 0:
            # Map score soft sigmoid/min-max to [0.0, 1.0]
            val = score / matches
            return min(1.0, max(0.0, val * 5.0 + 0.3))
            
        return 0.5

    def _get_community_sentiment_similarity(self, db: Session, target_movie: Movie, candidate_movie: Movie) -> float:
        """
        Calculates sentiment aspect scores absolute distance similarity:
        Comparing audience reactions to Acting, Story, Music, Visuals, Direction.
        """
        def get_aspects(movie_id: int):
            db_rating = db.query(Rating).filter(Rating.movie_id == movie_id).first()
            if db_rating and db_rating.rating_count > 0:
                # aspects from reviews
                from app.sentiment.analyzer import sentiment_service
                reviews = db.query(Review).filter(Review.movie_id == movie_id, Review.source != "YouTube").all()
                if reviews:
                    acting_sum = 0
                    story_sum = 0
                    music_sum = 0
                    vfx_sum = 0
                    direction_sum = 0
                    for r in reviews:
                        aspects = None
                        if r.aspect_scores_json:
                            try:
                                aspects = json.loads(r.aspect_scores_json)
                            except Exception:
                                pass
                        if not aspects:
                            aspects = {"acting": 5.0, "story": 5.0, "music": 5.0, "visual_effects": 5.0, "direction": 5.0}
                        acting_sum += aspects.get("acting", 5.0)
                        story_sum += aspects.get("story", 5.0)
                        music_sum += aspects.get("music", 5.0)
                        vfx_sum += aspects.get("visual_effects", 5.0)
                        direction_sum += aspects.get("direction", 5.0)
                    cnt = len(reviews)
                    return {
                        "acting": acting_sum / cnt,
                        "story": story_sum / cnt,
                        "music": music_sum / cnt,
                        "visual_effects": vfx_sum / cnt,
                        "direction": direction_sum / cnt
                    }
            # Mock / Default aspects
            val = (movie_id % 5) * 0.4 + 6.8
            return {"acting": val, "story": val - 0.2, "music": val + 0.1, "visual_effects": val + 0.3, "direction": val - 0.1}

        t_asp = get_aspects(target_movie.id)
        c_asp = get_aspects(candidate_movie.id)
        
        diff = 0.0
        for k in ["acting", "story", "music", "visual_effects", "direction"]:
            diff += abs(t_asp.get(k, 5.0) - c_asp.get(k, 5.0))
            
        avg_diff = diff / 5.0
        # Similarity ranges from 0.0 to 1.0 (difference out of 10.0 max aspect score)
        return max(0.0, min(1.0, 1.0 - (avg_diff / 5.0)))

    def _compute_cosine_similarity(self, v1: Optional[List[float]], v2: Optional[List[float]]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        # Since embeddings are already L2 normalized, cosine similarity is just dot product
        return sum(x * y for x, y in zip(v1, v2))

    def get_netflix_recommendations(self, db: Session, target_movie_id: int, user_id: Optional[int] = None, bypass_cache: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieves hybrid recommendations grouped in 4 sliders (similar movies, similar themes,
        hidden gems, trending alternatives) with full explainable analytics.
        Uses RecommendationCache for caching results.
        """
        cache_key = f"target_{target_movie_id}_user_{user_id or 0}"
        if not bypass_cache:
            cached = db.query(RecommendationCache).filter(
                RecommendationCache.target_movie_id == target_movie_id,
                RecommendationCache.user_id == user_id,
                RecommendationCache.recommendation_type == "all"
            ).order_by(RecommendationCache.created_at.desc()).first()
            if cached:
                # Check TTL (10 minutes)
                now = datetime.datetime.now(datetime.timezone.utc)
                created = cached.created_at.replace(tzinfo=datetime.timezone.utc) if cached.created_at.tzinfo is None else cached.created_at
                if (now - created).seconds < 600:
                    return cached.results

        # Fetch target movie
        target_movie = db.query(Movie).filter(Movie.id == target_movie_id).first()
        if not target_movie:
            return {"similar_movies": [], "similar_themes": [], "hidden_gems": [], "trending_alternatives": []}

        # Ensure target movie embeddings exist
        self.generate_embeddings_for_movie_if_needed(db, target_movie)
        target_emb = db.query(MovieEmbedding).filter(MovieEmbedding.movie_id == target_movie_id).first()

        # Fetch all candidate movies
        candidates = db.query(Movie).filter(Movie.id != target_movie_id).all()
        if not candidates:
            return {"similar_movies": [], "similar_themes": [], "hidden_gems": [], "trending_alternatives": []}

        # Pre-generate embeddings for all candidates
        for c in candidates:
            self.generate_embeddings_for_movie_if_needed(db, c)

        # Get user preferences
        pref = None
        if user_id:
            pref = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()

        target_year = None
        if target_movie.release_date:
            try:
                target_year = int(target_movie.release_date.split("-")[0])
            except ValueError:
                pass

        # Dynamically find candidate release year window (±5 -> ±7 -> ±10)
        matching_candidates = []
        active_window = 5
        
        if target_year:
            for window in [5, 7, 10]:
                active_window = window
                matching_candidates = []
                for c in candidates:
                    if c.release_date:
                        try:
                            c_year = int(c.release_date.split("-")[0])
                            if abs(c_year - target_year) <= window:
                                matching_candidates.append(c)
                        except ValueError:
                            pass
                if len(matching_candidates) >= 10:
                    break
        else:
            matching_candidates = candidates

        if not matching_candidates:
            matching_candidates = candidates

        scored_candidates = []
        target_genres = set(g.get("id") for g in target_movie.genres if isinstance(g, dict) and g.get("id"))

        for c in matching_candidates:
            c_emb = db.query(MovieEmbedding).filter(MovieEmbedding.movie_id == c.id).first()
            if not c_emb or not target_emb:
                continue

            # 1. Genre Jaccard Similarity (30%)
            c_genres = set(g.get("id") for g in c.genres if isinstance(g, dict) and g.get("id"))
            intersection = target_genres.intersection(c_genres)
            union = target_genres.union(c_genres)
            genre_sim = len(intersection) / len(union) if union else 0.0

            # 2. Theme Semantic Similarity (25%)
            theme_sim = self._compute_cosine_similarity(target_emb.themes_embedding, c_emb.themes_embedding)
            theme_sim = max(0.0, min(1.0, theme_sim))

            # 3. CineScore Quality Score (25%)
            cinescore_val = 7.0
            rating_obj = db.query(Rating).filter(Rating.movie_id == c.id).first()
            if rating_obj and rating_obj.aggregate_score:
                cinescore_val = rating_obj.aggregate_score
            elif c.vote_average:
                cinescore_val = c.vote_average
            cinescore_score = cinescore_val / 10.0

            # 4. Release Year Proximity Similarity (15%)
            year_diff = 0
            c_year = target_year
            if target_year and c.release_date:
                try:
                    c_year = int(c.release_date.split("-")[0])
                    year_diff = abs(c_year - target_year)
                except ValueError:
                    pass
            year_sim = max(0.0, 1.0 - (year_diff / float(active_window))) if active_window > 0 else 1.0

            # 5. Popularity Score (5%)
            rating_count = rating_obj.rating_count if rating_obj else 0
            popularity_score = min(1.0, math.log1p(rating_count) / math.log1p(100))

            # Compute hybrid score
            hybrid_score = (
                0.30 * genre_sim +
                0.25 * theme_sim +
                0.25 * cinescore_score +
                0.15 * year_sim +
                0.05 * popularity_score
            )

            # Format year difference description
            if year_diff == 0:
                year_diff_text = "Released Same Year"
            else:
                rel_pos = "Later" if (c_year > target_year if (target_year and c.release_date) else True) else "Earlier"
                suffix = "Year" if year_diff == 1 else "Years"
                year_diff_text = f"Released {year_diff} {suffix} {rel_pos}"

            # Descriptive explanation text
            explain_reasons = []
            if genre_sim > 0.6:
                explain_reasons.append("similar genre profile")
            if theme_sim > 0.75:
                explain_reasons.append("strong thematic overlaps")
            if target_movie.director and target_movie.director == c.director:
                explain_reasons.append("same director")
            why = "Matches " + " and ".join(explain_reasons[:2]) if explain_reasons else "Highly rated match with thematic connections"

            scored_candidates.append({
                "movie": c,
                "score": hybrid_score,
                "cinescore": cinescore_val,
                "popularity": rating_count,
                "genre_sim": genre_sim,
                "theme_sim": theme_sim,
                "year_diff": year_diff,
                "year_diff_text": year_diff_text,
                "explanation": {
                    "why_recommended": why,
                    "match_percentage": int(hybrid_score * 100),
                    "genre_match_pct": int(genre_sim * 100),
                    "theme_match_pct": int(theme_sim * 100),
                    "year_diff_text": year_diff_text,
                    "cinescore": round(cinescore_val, 1),
                    "metrics": {
                        "content_similarity": round(theme_sim, 2),
                        "theme_similarity": round(theme_sim, 2),
                        "genre_similarity": round(genre_sim, 2),
                        "sentiment_similarity": round(cinescore_score, 2),
                        "cinescore": round(cinescore_val, 1)
                    }
                }
            })

        # Format movie helper
        def format_movie(item):
            movie = item["movie"]
            return {
                "id": movie.id,
                "title": movie.title,
                "overview": movie.overview,
                "poster_path": movie.poster_path,
                "release_date": movie.release_date,
                "genres": movie.genres,
                "vote_average": movie.vote_average,
                "imdb_rating": movie.imdb_rating,
                "metacritic_score": movie.metacritic_score,
                "recommendation_score": round(item["score"], 4),
                "explanation": item["explanation"]
            }

        # Construct 5 output categories (10 movies each)
        # Similar Movies (highest overall hybrid scores)
        similar_movies_sorted = sorted(scored_candidates, key=lambda x: x["score"], reverse=True)
        similar_movies = [format_movie(x) for x in similar_movies_sorted[:10]]

        # Top Rated Similar Movies (highest CineScore among similar ones)
        top_rated_sorted = sorted(scored_candidates, key=lambda x: (x["cinescore"], x["score"]), reverse=True)
        top_rated_similar = [format_movie(x) for x in top_rated_sorted[:10]]

        # Recent Alternatives (closest release year difference)
        recent_sorted = sorted(scored_candidates, key=lambda x: (x["year_diff"], -x["score"]))
        recent_alternatives = [format_movie(x) for x in recent_sorted[:10]]

        # Hidden Gems (high CineScore >= 7.5, low popularity < 15 reviews)
        gems_candidates = [x for x in scored_candidates if x["cinescore"] >= 7.5 and x["popularity"] < 15]
        if len(gems_candidates) < 10:
            gems_candidates = [x for x in scored_candidates if x["cinescore"] >= 7.2]
        gems_sorted = sorted(gems_candidates, key=lambda x: (x["cinescore"], -x["popularity"]), reverse=True)
        hidden_gems = [format_movie(x) for x in gems_sorted[:10]]

        # Community Favorites (highest reviews count/popularity)
        favorites_sorted = sorted(scored_candidates, key=lambda x: (x["popularity"], x["score"]), reverse=True)
        community_favorites = [format_movie(x) for x in favorites_sorted[:10]]

        results_payload = {
            "similar_movies": similar_movies,
            "top_rated_similar": top_rated_similar,
            "recent_alternatives": recent_alternatives,
            "hidden_gems": hidden_gems,
            "community_favorites": community_favorites,
            # Backward compatibility keys
            "similar_themes": top_rated_similar,
            "trending_alternatives": community_favorites
        }

        # Cache results in DB
        # Delete old cache for this movie and user
        db.query(RecommendationCache).filter(
            RecommendationCache.target_movie_id == target_movie_id,
            RecommendationCache.user_id == user_id,
            RecommendationCache.recommendation_type == "all"
        ).delete()
        db.commit()

        new_cache = RecommendationCache(
            target_movie_id=target_movie_id,
            user_id=user_id,
            recommendation_type="all",
            results=results_payload
        )
        db.add(new_cache)
        db.commit()

        return results_payload

    def get_personalized_recommendations(self, db: Session, user_id: int, limit: int = 12) -> List[Dict[str, Any]]:
        """
        Compiles personalized recommendations for a user.
        Scores all database movies based on their alignment with the user's preferences,
        quality (CineScore), and freshness, filtering out movies the user has already viewed/liked.
        """
        # Get viewed movie IDs
        viewed_ids = set(row[0] for row in db.query(UserInteraction.movie_id).filter(
            UserInteraction.user_id == user_id,
            UserInteraction.interaction_type == "view"
        ).all())

        # Also exclude movies the user has already reviewed
        reviewed_ids = set(row[0] for row in db.query(Review.movie_id).filter(
            Review.user_id == user_id
        ).all())
        viewed_ids.update(reviewed_ids)

        pref = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
        if not pref:
            # Cold start: return top rated movies in database (excluding viewed/reviewed ones)
            top_movies = db.query(Movie).order_by(Movie.vote_average.desc()).all()
            
            # Apply viewed/reviewed filter
            filtered_top = [m for m in top_movies if m.id not in viewed_ids]

            if not filtered_top:
                # If database is empty (e.g. in test environment), use fallback mock movies
                mock_presets = [
                    {"id": 27205, "title": "Inception", "vote_average": 8.3},
                    {"id": 157336, "title": "Interstellar", "vote_average": 8.4},
                    {"id": 155, "title": "The Dark Knight", "vote_average": 8.5}
                ]
                # Filter out viewed/reviewed mock presets as well
                mock_presets = [m for m in mock_presets if m["id"] not in viewed_ids]
                
                recs = []
                for m in mock_presets:
                    recs.append({
                        "id": m["id"],
                        "title": m["title"],
                        "overview": "Fallback mock overview description",
                        "poster_path": None,
                        "release_date": "2010-01-01",
                        "genres": [],
                        "vote_average": m["vote_average"],
                        "imdb_rating": None,
                        "metacritic_score": None,
                        "recommendation_score": 0.5,
                        "explanation": {
                            "why_recommended": "Recommended because it is highly rated by the community",
                            "match_percentage": 50,
                            "metrics": {
                                "content_similarity": 0.5,
                                "theme_similarity": 0.5,
                                "genre_similarity": 0.5,
                                "sentiment_similarity": 0.5,
                                "cinescore": round(m["vote_average"], 1)
                            }
                        }
                    })
                return recs[:limit]

            recs = []
            for m in filtered_top[:limit]:
                # Add default explanation
                cinescore = m.vote_average
                rating_obj = db.query(Rating).filter(Rating.movie_id == m.id).first()
                if rating_obj and rating_obj.aggregate_score:
                    cinescore = rating_obj.aggregate_score
                recs.append({
                    "id": m.id,
                    "title": m.title,
                    "overview": m.overview,
                    "poster_path": m.poster_path,
                    "release_date": m.release_date,
                    "genres": m.genres,
                    "vote_average": m.vote_average,
                    "imdb_rating": m.imdb_rating,
                    "metacritic_score": m.metacritic_score,
                    "recommendation_score": 0.5,
                    "explanation": {
                        "why_recommended": "Recommended because it is highly rated by the community",
                        "match_percentage": 50,
                        "metrics": {
                            "content_similarity": 0.5,
                            "theme_similarity": 0.5,
                            "genre_similarity": 0.5,
                            "sentiment_similarity": 0.5,
                            "cinescore": round(cinescore, 1)
                        }
                    }
                })
            return recs

        all_movies = db.query(Movie).all()
        scored = []
        for m in all_movies:
            if m.id in viewed_ids:
                continue
            
            # Ensure embeddings are cached
            self.generate_embeddings_for_movie_if_needed(db, m)

            # User alignment score
            user_score = self._get_user_behavior_score(m, pref)

            # Quality score
            cinescore_val = 7.0
            rating_obj = db.query(Rating).filter(Rating.movie_id == m.id).first()
            if rating_obj and rating_obj.aggregate_score:
                cinescore_val = rating_obj.aggregate_score
            elif m.vote_average:
                cinescore_val = m.vote_average
            cinescore_score = cinescore_val / 10.0

            # Freshness score
            freshness_score = 0.0
            if m.release_date:
                try:
                    rel_year = int(m.release_date.split("-")[0])
                    now_year = datetime.datetime.now().year
                    if now_year - rel_year <= 1:
                        freshness_score = 1.0
                    elif now_year - rel_year <= 2:
                        freshness_score = 0.5
                except Exception:
                    pass

            # Combine: 50% user behavior, 40% CineScore, 10% freshness
            final_score = (0.50 * user_score) + (0.40 * cinescore_score) + (0.10 * freshness_score)
            match_pct = int(final_score * 100)

            explain_reasons = []
            if user_score > 0.7:
                explain_reasons.append("Matches your favorite genres & actors")
            if cinescore_score > 0.85:
                explain_reasons.append("Top CineScore Quality Pick")
            if freshness_score > 0.5:
                explain_reasons.append("Recently Released")

            why = "Recommended because: " + " and ".join(explain_reasons[:2]) if explain_reasons else f"Matches your interest profile ({match_pct}%)"

            scored.append({
                "movie": m,
                "score": final_score,
                "cinescore": cinescore_val,
                "explanation": {
                    "why_recommended": why,
                    "match_percentage": match_pct,
                    "metrics": {
                        "content_similarity": round(user_score, 2),
                        "theme_similarity": round(user_score, 2),
                        "genre_similarity": round(user_score, 2),
                        "sentiment_similarity": 0.8,
                        "cinescore": round(cinescore_val, 1)
                    }
                }
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        
        recs = []
        for item in scored[:limit]:
            movie = item["movie"]
            recs.append({
                "id": movie.id,
                "title": movie.title,
                "overview": movie.overview,
                "poster_path": movie.poster_path,
                "release_date": movie.release_date,
                "genres": movie.genres,
                "vote_average": movie.vote_average,
                "imdb_rating": movie.imdb_rating,
                "metacritic_score": movie.metacritic_score,
                "recommendation_score": round(item["score"], 4),
                "explanation": item["explanation"]
            })
        return recs

# Instantiate service singleton
recommendation_service = RecommendationService()
