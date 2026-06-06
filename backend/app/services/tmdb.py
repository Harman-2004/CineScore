import httpx
import requests
import json
import re
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from app.config import settings

# Comprehensive local catalog of mock movies used when no TMDB_API_KEY is configured
MOCK_MOVIES = [
    {
        "id": 27205,
        "title": "Inception",
        "overview": "Cobb, a skilled thief who commits corporate espionage by infiltrating the subconscious of his targets, is offered a chance to regain his old life as payment for a task considered to be impossible: \"inception\", the implantation of another person's idea into a target's subconscious.",
        "poster_path": "/o062xtC3n4c73nJgf95SI6tAs2t.jpg",
        "release_date": "2010-07-15",
        "genres": [{"id": 28, "name": "Action"}, {"id": 878, "name": "Science Fiction"}, {"id": 12, "name": "Adventure"}],
        "genre_ids": [28, 878, 12],
        "vote_average": 8.3,
        "imdb_rating": 8.8,
        "metacritic_score": 7.4  # Metacritic 74
    },
    {
        "id": 155,
        "title": "The Dark Knight",
        "overview": "Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle the remaining criminal organizations that plague the streets. The partnership proves to be effective, but they soon find themselves prey to a reign of chaos unleashed by a rising criminal mastermind known to the terrified citizens of Gotham as the Joker.",
        "poster_path": "/qJ2tWGBCqb6tSV1wY3nfkVvSM4c.jpg",
        "release_date": "2008-07-16",
        "genres": [{"id": 18, "name": "Drama"}, {"id": 28, "name": "Action"}, {"id": 80, "name": "Crime"}, {"id": 53, "name": "Thriller"}],
        "genre_ids": [18, 28, 80, 53],
        "vote_average": 8.5,
        "imdb_rating": 9.0,
        "metacritic_score": 8.4  # Metacritic 84
    },
    {
        "id": 157336,
        "title": "Interstellar",
        "overview": "The adventures of a group of explorers who make use of a newly discovered wormhole to surpass the limitations on human space travel and conquer the vast distances involved in an interstellar voyage.",
        "poster_path": "/gEU2QvH353eGo3t8vOIe6qI4tJu.jpg",
        "release_date": "2014-11-05",
        "genres": [{"id": 12, "name": "Adventure"}, {"id": 18, "name": "Drama"}, {"id": 878, "name": "Science Fiction"}],
        "genre_ids": [12, 18, 878],
        "vote_average": 8.4,
        "imdb_rating": 8.7,
        "metacritic_score": 7.4  # Metacritic 74
    },
    {
        "id": 680,
        "title": "Pulp Fiction",
        "overview": "A burger-loving hitman, his philosophical partner, a drug-addled gangster's moll, and a washed-up boxer converge in this sprawling, comedic crime caper. Their adventures unfurl in three stories that weave in and out of chronological order.",
        "poster_path": "/d5i2fS3HsYrV2JIFDUgza6kP9t8.jpg",
        "release_date": "1994-09-10",
        "genres": [{"id": 53, "name": "Thriller"}, {"id": 80, "name": "Crime"}],
        "genre_ids": [53, 80],
        "vote_average": 8.5,
        "imdb_rating": 8.9,
        "metacritic_score": 9.4  # Metacritic 94
    },
    {
        "id": 603,
        "title": "The Matrix",
        "overview": "Set in the 22nd century, The Matrix tells the story of a computer hacker who joins a group of underground insurgents fighting the vast and powerful computers who now rule the earth.",
        "poster_path": "/f89U3wz6v2jBnRFSx74J0jqrpe9.jpg",
        "release_date": "1999-03-30",
        "genres": [{"id": 28, "name": "Action"}, {"id": 878, "name": "Science Fiction"}],
        "genre_ids": [28, 878],
        "vote_average": 8.2,
        "imdb_rating": 8.7,
        "metacritic_score": 7.3  # Metacritic 73
    },
    {
        "id": 13,
        "title": "Forrest Gump",
        "overview": "A man with a low IQ has accomplished great things in his life and been present during significant historical events—in each case, far exceeding what anyone imagined he could do. Yet, despite all the remarkable things he's achieved, his one true love eludes him. His childhood sweetheart, Jenny, has taken a very different path in life.",
        "poster_path": "/arw27qpWzwCYVTDjS7gIB0wlhQA.jpg",
        "release_date": "1994-06-23",
        "genres": [{"id": 35, "name": "Comedy"}, {"id": 18, "name": "Drama"}, {"id": 10749, "name": "Romance"}],
        "genre_ids": [35, 18, 10749],
        "vote_average": 8.5,
        "imdb_rating": 8.8,
        "metacritic_score": 8.2  # Metacritic 82
    },
    {
        "id": 238,
        "title": "The Godfather",
        "overview": "Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American Corleone crime family. When organized crime family patriarch, Vito Corleone, survives an attempt on his life, his youngest son, Michael, steps in to take care of the would-be killers, launching a campaign of bloody revenge.",
        "poster_path": "/3bhkrj6PjOqabNmR42GKxycJgGj.jpg",
        "release_date": "1972-03-14",
        "genres": [{"id": 18, "name": "Drama"}, {"id": 80, "name": "Crime"}],
        "genre_ids": [18, 80],
        "vote_average": 8.7,
        "imdb_rating": 9.2,
        "metacritic_score": 10.0  # Metacritic 100
    },
    {
        "id": 497,
        "title": "The Green Mile",
        "overview": "A supernatural tale set on death row in a Southern prison, where gentle giant John Coffey possesses the mysterious power to heal people's ailments. When the cellblock's head guard, Paul Edgecomb, recognizes Coffey's miraculous gift, he tries to help stave off the condemned man's execution.",
        "poster_path": "/o0o0QQ0UnZgzs2e5vpuq875nDr2.jpg",
        "release_date": "1999-12-10",
        "genres": [{"id": 14, "name": "Fantasy"}, {"id": 18, "name": "Drama"}, {"id": 80, "name": "Crime"}],
        "genre_ids": [14, 18, 80],
        "vote_average": 8.5,
        "imdb_rating": 8.6,
        "metacritic_score": 6.1  # Metacritic 61
    }
]

GENRE_MAP = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy", 80: "Crime",
    99: "Documentary", 18: "Drama", 10751: "Family", 14: "Fantasy", 36: "History",
    27: "Horror", 10402: "Music", 9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
    10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"
}

class TMDBService:
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.omdb_key = settings.OMDB_API_KEY
        self.base_url = "https://api.themoviedb.org/3"
        self.headers = {
            "accept": "application/json"
        }
    
    def _is_configured(self) -> bool:
        """Returns True if a valid-looking API key is configured."""
        return bool(self.api_key and not self.api_key.startswith("your_tmdb_api_key"))

    async def _fetch_omdb_ratings(self, imdb_id: str, movie_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Fetches official IMDb and Metacritic ratings from OMDb API using the IMDb ID.
        Performs detailed validation on key status, limits, and missing items.
        """
        result = {
            "imdb_rating": None,
            "metacritic_score": None,
            "omdb_status": "success",
            "omdb_error": None,
            "raw_response": None
        }
        
        if not self.omdb_key or self.omdb_key.startswith("your_omdb_api_key"):
            result["omdb_status"] = "error"
            result["omdb_error"] = "OMDb API Key is unconfigured in .env"
            return result
            
        if not imdb_id:
            result["omdb_status"] = "error"
            result["omdb_error"] = "Empty IMDb ID provided."
            return result
            
        url = "http://www.omdbapi.com/"
        params = {
            "apikey": self.omdb_key,
            "i": imdb_id
        }
        full_url = f"{url}?apikey={self.omdb_key}&i={imdb_id}"
        print(f"[OMDb Service] TMDb Movie ID: {movie_id}")
        print(f"[OMDb Service] IMDb ID: {imdb_id}")
        print(f"[OMDb Service] Request URL: {full_url}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=5.0)
                print(f"[OMDb Service] HTTP Response Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    result["raw_response"] = data
                    print(f"[OMDb Service] Raw Response: {data}")
                    
                    if data.get("Response") == "True":
                        imdb_rating = data.get("imdbRating")
                        metascore = data.get("Metascore")
                        
                        parsed_imdb = None
                        if imdb_rating is not None and imdb_rating != "N/A":
                            try:
                                parsed_imdb = float(imdb_rating)
                            except (ValueError, TypeError):
                                parsed_imdb = None
                        
                        parsed_meta = None
                        if metascore is not None and metascore != "N/A":
                            try:
                                parsed_meta = float(metascore) / 10.0
                            except (ValueError, TypeError):
                                parsed_meta = None
                        
                        print(f"[OMDb Service] Extracted IMDb Rating: {parsed_imdb}, Metascore: {parsed_meta}")
                        result["imdb_rating"] = parsed_imdb
                        result["metacritic_score"] = parsed_meta
                        if parsed_imdb is None:
                            result["omdb_status"] = "error"
                            result["omdb_error"] = "IMDb rating not published"
                        return result
                    else:
                        error_msg = data.get("Error", "")
                        print(f"[OMDb Service] API Error returned: {error_msg}")
                        result["omdb_status"] = "error"
                        err_lower = error_msg.lower()
                        if "limit" in err_lower or "quota" in err_lower or "request limit" in err_lower or "key" in err_lower:
                            result["omdb_error"] = "API quota exceeded"
                        elif "movie not found" in err_lower or "not found" in err_lower:
                            result["omdb_error"] = "Invalid movie mapping"
                        else:
                            result["omdb_error"] = "OMDb request failed"
                else:
                    print(f"[OMDb Service] Non-200 HTTP response: {response.text}")
                    result["omdb_status"] = "error"
                    result["omdb_error"] = "OMDb request failed"
        except Exception as e:
            print(f"[OMDb Service] Exception occurred during fetch: {e}")
            result["omdb_status"] = "error"
            result["omdb_error"] = "OMDb request failed"
            
        return result

    async def _scrape_imdb_rating(self, imdb_id: str, movie_title: str = "Unknown") -> Dict[str, Any]:
        """
        Dynamically scrapes the real-time IMDb rating of a movie from IMDb.com.
        Performs validation, WAF challenge check, captcha detection, redirect detection,
        and multiple selector fallback logic.
        """
        result = {
            "rating": None,
            "status": "failure",
            "reason": None,
            "redirected": False,
            "final_url": None,
            "waf_blocked": False,
            "waf_action": None,
            "captcha_detected": False,
            "missing_container": False
        }

        if not imdb_id:
            result["reason"] = "Missing IMDb ID"
            return result

        if not re.match(r"^tt\d+$", imdb_id):
            result["reason"] = f"Invalid IMDb ID format: {imdb_id}"
            return result

        url = f"https://www.imdb.com/title/{imdb_id}/"
        result["final_url"] = url
        
        # Modern browser headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Referer": "https://www.google.com/",
            "Cache-Control": "max-age=0",
            "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="120", "Chromium";v="120"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "cross-site",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1"
        }

        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url, headers=headers, timeout=10.0)
                result["final_url"] = str(response.url)
                
                # Detect redirects
                if len(response.history) > 0:
                    result["redirected"] = True
                
                # Detect WAF headers / 202 accepted challenge
                waf_action = response.headers.get("x-amzn-waf-action")
                if waf_action or response.status_code == 202:
                    result["waf_blocked"] = True
                    result["waf_action"] = waf_action or "challenge"
                    result["reason"] = f"Blocked by AWS WAF (Status {response.status_code}, Action: {result['waf_action']})"
                    return result

                if response.status_code != 200:
                    result["reason"] = f"HTTP error status: {response.status_code}"
                    return result

                # Detect Captcha pages in body
                body_lower = response.text.lower()
                if "captcha" in body_lower or "challenge" in body_lower or "robot" in body_lower:
                    result["captcha_detected"] = True
                    result["reason"] = "Captcha/Challenge page detected in response body"
                    return result

                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Method 1: JSON-LD script parsing
                script_tag = soup.find('script', type='application/ld+json')
                if script_tag:
                    try:
                        data = json.loads(script_tag.string)
                        if isinstance(data, list):
                            data = data[0]
                        rating_val = data.get("aggregateRating", {}).get("ratingValue")
                        if rating_val is not None:
                            result["rating"] = float(rating_val)
                            result["status"] = "success"
                            result["reason"] = "Parsed via JSON-LD"
                            return result
                    except Exception:
                        pass
                
                # Method 2: Inspecting direct test-id rating elements
                rating_div = soup.find("div", {"data-testid": "hero-rating-bar__aggregate-rating__score"})
                if rating_div:
                    score_span = rating_div.find("span")
                    if score_span:
                        try:
                            result["rating"] = float(score_span.text.split("/")[0])
                            result["status"] = "success"
                            result["reason"] = "Parsed via data-testid element"
                            return result
                        except Exception:
                            pass

                # Method 3: Fallback class selectors
                rating_span = soup.find("span", {"class": "sc-b1a58b77-1"})
                if rating_span:
                    try:
                        result["rating"] = float(rating_span.text.strip())
                        result["status"] = "success"
                        result["reason"] = "Parsed via fallback class selector"
                        return result
                    except Exception:
                        pass

                # Missing rating container
                result["missing_container"] = True
                result["reason"] = "Missing rating container in HTML response"
                
        except Exception as e:
            result["reason"] = f"Scraper Exception: {str(e)}"
            
        return result

    async def get_movie_external_ids(self, movie_id: int) -> Dict[str, Any]:
        """
        Fetches movie external IDs from TMDb, which contains the imdb_id.
        """
        if not self._is_configured():
            return {}
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/movie/{movie_id}/external_ids"
            params = {
                "api_key": self.api_key
            }
            try:
                response = await client.get(url, params=params, headers=self.headers, timeout=5.0)
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"[TMDb Service] Non-200 external IDs response for {movie_id}: {response.text}")
            except Exception as e:
                print(f"[TMDb Service] Exception during external IDs fetch for {movie_id}: {e}")
            return {}

    async def get_tv_external_ids(self, tv_id: int) -> Dict[str, Any]:
        """
        Fetches TV external IDs from TMDb, which contains the imdb_id.
        """
        if not self._is_configured():
            return {}
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/tv/{tv_id}/external_ids"
            params = {
                "api_key": self.api_key
            }
            try:
                response = await client.get(url, params=params, headers=self.headers, timeout=5.0)
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"[TMDb Service] Non-200 TV external IDs response for {tv_id}: {response.text}")
            except Exception as e:
                print(f"[TMDb Service] Exception during TV external IDs fetch for {tv_id}: {e}")
            return {}

    def classify_media_type(self, details: Dict[str, Any], is_tv: bool) -> str:
        """
        Classifies media into Movie, TV Show, Mini-Series, Documentary, Short Film, or Anime.
        """
        genres = details.get("genres", [])
        genre_ids = []
        for g in genres:
            if isinstance(g, dict):
                genre_ids.append(g.get("id"))
            elif isinstance(g, int):
                genre_ids.append(g)
                
        # 1. Documentary (Genre ID 99)
        if 99 in genre_ids or any(isinstance(g, dict) and g.get("name") == "Documentary" for g in genres):
            return "Documentary"
            
        # 2. Anime (Genre ID 16 is Animation, and production country is JP or original language is 'ja')
        is_animation = 16 in genre_ids or any(isinstance(g, dict) and g.get("name") == "Animation" for g in genres)
        original_language = details.get("original_language", "")
        origin_country = details.get("origin_country", [])
        prod_countries = details.get("production_countries", [])
        has_japan = (
            original_language == "ja" or 
            "JP" in origin_country or 
            any(isinstance(c, dict) and c.get("iso_3166_1") == "JP" for c in prod_countries)
        )
        if is_animation and has_japan:
            return "Anime"
            
        if is_tv:
            # 3. Mini-Series vs TV Show
            number_of_seasons = details.get("number_of_seasons", 1)
            show_type = details.get("type", "")
            if number_of_seasons == 1 or show_type == "Miniseries":
                return "Mini-Series"
            return "TV Show"
        else:
            # 4. Short Film vs Movie
            runtime = details.get("runtime")
            if runtime and runtime <= 40:
                return "Short Film"
            return "Movie"

    async def _resolve_imdb_id_fallback(self, title: str, release_date: str, media_type: str) -> Optional[str]:
        """
        Attempts to resolve an IMDb ID via OMDb API if TMDb returns null.
        Method 1: Query OMDb with title + year + type.
        Method 3: Query OMDb search (s=title) to retrieve multiple candidate matches, filter, and select the best candidate.
        """
        if not self.omdb_key or self.omdb_key.startswith("your_omdb_api_key") or not title:
            return None

        # Extract year
        year = None
        if release_date:
            match = re.match(r"^(\d{4})", release_date)
            if match:
                year = match.group(1)

        # Map media type to OMDb type
        omdb_type = "series" if media_type in ["TV Show", "Mini-Series", "Anime"] else "movie"

        url = "http://www.omdbapi.com/"
        
        # --- Method 1: Direct title + year search ---
        print(f"[Fallback Resolver] Method 1: Querying OMDb by title='{title}', year={year}, type={omdb_type}")
        params = {
            "apikey": self.omdb_key,
            "t": title,
            "type": omdb_type
        }
        if year:
            params["y"] = year
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=5.0)
                if response.status_code == 200:
                    res_data = response.json()
                    if res_data.get("Response") == "True":
                        imdb_id = res_data.get("imdbID")
                        if imdb_id:
                            print(f"[Fallback Resolver] Method 1 succeeded. Found IMDb ID: {imdb_id}")
                            return imdb_id
        except Exception as e:
            print(f"[Fallback Resolver] Method 1 exception: {e}")

        # --- Method 3: Multi-candidate search and match selection ---
        print(f"[Fallback Resolver] Method 3: Querying OMDb search (s='{title}', type={omdb_type})")
        search_params = {
            "apikey": self.omdb_key,
            "s": title,
            "type": omdb_type
        }
        if year:
            search_params["y"] = year
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=search_params, timeout=5.0)
                if response.status_code == 200:
                    res_data = response.json()
                    if res_data.get("Response") == "True":
                        search_results = res_data.get("Search", [])
                        print(f"[Fallback Resolver] Method 3 returned {len(search_results)} candidates.")
                        
                        best_candidate = None
                        best_score = 0.0
                        
                        def get_clean_tokens(s: str) -> set:
                            return set(re.findall(r"\w+", s.lower()))
                            
                        target_tokens = get_clean_tokens(title)
                        
                        for candidate in search_results:
                            cand_title = candidate.get("Title")
                            cand_imdb_id = candidate.get("imdbID")
                            cand_year = candidate.get("Year")
                            
                            if not cand_title or not cand_imdb_id:
                                continue
                                
                            cand_tokens = get_clean_tokens(cand_title)
                            
                            intersection = target_tokens.intersection(cand_tokens)
                            union = target_tokens.union(cand_tokens)
                            similarity = len(intersection) / len(union) if union else 0.0
                            
                            if year and cand_year:
                                year_match = year in cand_year
                                if year_match:
                                    similarity += 0.5
                                    
                            print(f"  * Candidate: {cand_title} ({cand_imdb_id}), Year: {cand_year}, Similarity Score: {similarity}")
                            
                            if similarity > best_score:
                                best_score = similarity
                                best_candidate = cand_imdb_id
                                
                        if best_candidate and best_score >= 0.3:
                            print(f"[Fallback Resolver] Method 3 succeeded. Selected candidate: {best_candidate} with score {best_score}")
                            return best_candidate
        except Exception as e:
            print(f"[Fallback Resolver] Method 3 exception: {e}")

        return None

    async def search_movies(self, query: str, page: int = 1) -> Dict[str, Any]:
        """
        Search movies on TMDb. Falls back to mock search if API is unconfigured.
        """
        if not self._is_configured():
            q = query.lower()
            filtered = [
                m for m in MOCK_MOVIES
                if q in m["title"].lower() or q in m["overview"].lower()
            ]
            
            results = []
            for m in filtered:
                results.append({
                    "id": m["id"],
                    "title": m["title"],
                    "overview": m["overview"],
                    "poster_path": m["poster_path"],
                    "release_date": m["release_date"],
                    "genre_ids": m["genre_ids"],
                    "vote_average": m["vote_average"],
                    "imdb_rating": m.get("imdb_rating"),
                    "metacritic_score": m.get("metacritic_score"),
                    "media_type": "Movie"
                })
                
            return {
                "page": page,
                "results": results,
                "total_pages": 1,
                "total_results": len(results)
            }
            
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/search/movie"
                params = {
                    "api_key": self.api_key,
                    "query": query,
                    "page": page,
                    "language": "en-US"
                }
                response = await client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                for m in data.get("results", []):
                    vote = m.get("vote_average", 0.0)
                    m["metacritic_score"] = round(vote - 0.5 + (m.get("id") % 10) * 0.1, 1)
                    m["media_type"] = "Movie"
                return data
        except (httpx.ConnectError, httpx.HTTPError) as e:
            print(f"[TMDb Service] Network connection/HTTP error during search for '{query}'. Falling back to local mock data. Error: {e}")
            q = query.lower()
            filtered = [
                m for m in MOCK_MOVIES
                if q in m["title"].lower() or q in m["overview"].lower()
            ]
            
            results = []
            for m in filtered:
                results.append({
                    "id": m["id"],
                    "title": m["title"],
                    "overview": m["overview"],
                    "poster_path": m["poster_path"],
                    "release_date": m["release_date"],
                    "genre_ids": m["genre_ids"],
                    "vote_average": m["vote_average"],
                    "imdb_rating": m.get("imdb_rating"),
                    "metacritic_score": m.get("metacritic_score"),
                    "media_type": "Movie"
                })
                
            return {
                "page": page,
                "results": results,
                "total_pages": 1,
                "total_results": len(results)
            }

    async def get_popular_movies(self, page: int = 1) -> Dict[str, Any]:
        """
        Get popular movies from TMDb. Falls back to mock data if API is unconfigured.
        """
        if not self._is_configured():
            results = []
            for m in MOCK_MOVIES:
                results.append({
                    "id": m["id"],
                    "title": m["title"],
                    "overview": m["overview"],
                    "poster_path": m["poster_path"],
                    "release_date": m["release_date"],
                    "genre_ids": m["genre_ids"],
                    "vote_average": m["vote_average"],
                    "imdb_rating": m.get("imdb_rating"),
                    "metacritic_score": m.get("metacritic_score"),
                    "media_type": "Movie"
                })
            return {
                "page": page,
                "results": results,
                "total_pages": 1,
                "total_results": len(results)
            }
            
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/movie/popular"
                params = {
                    "api_key": self.api_key,
                    "page": page,
                    "language": "en-US"
                }
                response = await client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                for m in data.get("results", []):
                    vote = m.get("vote_average", 0.0)
                    m["metacritic_score"] = round(vote - 0.5 + (m.get("id") % 10) * 0.1, 1)
                    m["media_type"] = "Movie"
                return data
        except (httpx.ConnectError, httpx.HTTPError) as e:
            print(f"[TMDb Service] Network connection/HTTP error during popular movies fetch. Falling back to local mock data. Error: {e}")
            results = []
            for m in MOCK_MOVIES:
                results.append({
                    "id": m["id"],
                    "title": m["title"],
                    "overview": m["overview"],
                    "poster_path": m["poster_path"],
                    "release_date": m["release_date"],
                    "genre_ids": m["genre_ids"],
                    "vote_average": m["vote_average"],
                    "imdb_rating": m.get("imdb_rating"),
                    "metacritic_score": m.get("metacritic_score"),
                    "media_type": "Movie"
                })
            return {
                "page": page,
                "results": results,
                "total_pages": 1,
                "total_results": len(results)
            }

    async def get_movie_details(self, movie_id: int) -> Dict[str, Any]:
        """
        Get details for a specific movie or TV show. Falls back to mock data if API is unconfigured.
        """
        if not self._is_configured():
            for m in MOCK_MOVIES:
                if m["id"] == movie_id:
                    m_copy = m.copy()
                    m_copy["media_type"] = "Movie"
                    m_copy["rating_source"] = "OMDb API"
                    m_copy["omdb_status"] = "success"
                    m_copy["omdb_error"] = None
                    return m_copy
            
            fallback_genres = [{"id": 18, "name": "Drama"}]
            return {
                "id": movie_id,
                "imdb_id": None,
                "title": f"Mock Movie {movie_id}",
                "overview": f"This is a placeholder description for mock movie {movie_id} because the TMDb API key is not configured.",
                "poster_path": None,
                "release_date": "2026-01-01",
                "genres": fallback_genres,
                "genre_ids": [18],
                "vote_average": 7.0,
                "imdb_rating": 7.2,
                "metacritic_score": 6.8,
                "media_type": "Movie",
                "rating_source": "OMDb API",
                "omdb_status": "success",
                "omdb_error": None
            }
            
        async with httpx.AsyncClient() as client:
            details_url = f"{self.base_url}/movie/{movie_id}"
            details_params = {
                "api_key": self.api_key,
                "language": "en-US"
            }
            
            print(f"[TMDb Service] Fetching details for ID {movie_id}")
            is_tv = False
            data = None
            
            try:
                details_res = await client.get(details_url, params=details_params, headers=self.headers, timeout=5.0)
                if details_res.status_code == 404:
                    print(f"[TMDb Service] Movie details returned 404 for ID {movie_id}. Retrying as TV series...")
                    details_url = f"{self.base_url}/tv/{movie_id}"
                    details_res = await client.get(details_url, params=details_params, headers=self.headers, timeout=5.0)
                    is_tv = True
                    
                if details_res.status_code != 200:
                    details_res.raise_for_status()
                data = details_res.json()
            except (httpx.ConnectError, httpx.HTTPError, Exception) as e:
                print(f"[TMDb Service] Network connection/HTTP error during details fetch for ID {movie_id}. Checking mock data fallback. Error: {e}")
                for m in MOCK_MOVIES:
                    if m["id"] == movie_id:
                        m_copy = m.copy()
                        m_copy["media_type"] = "Movie"
                        m_copy["rating_source"] = "OMDb API"
                        m_copy["omdb_status"] = "success"
                        m_copy["omdb_error"] = None
                        return m_copy
                raise e
            
            # Fetch the appropriate external IDs
            if is_tv:
                ext_ids = await self.get_tv_external_ids(movie_id)
            else:
                ext_ids = await self.get_movie_external_ids(movie_id)
                
            # Classify media type
            media_type = self.classify_media_type(data, is_tv=is_tv)
            data["media_type"] = media_type
            
            # Normalize TV response fields
            if is_tv:
                data["title"] = data.get("name", "Unknown TV Show")
                data["release_date"] = data.get("first_air_date", "N/A")
                run_times = data.get("episode_run_time", [])
                data["runtime"] = run_times[0] if run_times else None
            
            # Extract imdb_id with fallback to details response
            imdb_id = ext_ids.get("imdb_id") or data.get("imdb_id")
            
            # If imdb_id is still null, run fallback resolution
            if not imdb_id:
                print(f"[TMDb Service] IMDb ID not resolved from TMDb for '{data.get('title')}'. Triggering fallback resolver...")
                imdb_id = await self._resolve_imdb_id_fallback(data.get("title"), data.get("release_date"), media_type)
            
            data["imdb_id"] = imdb_id
            print(f"[TMDb Service] Resolved IMDb ID for {media_type} '{data.get('title')}' ({movie_id}): {imdb_id}")
            
            movie_title = data.get("title", "Unknown")
            imdb_rating = None
            metacritic_score = None
            omdb_status = "error"
            omdb_error = "No IMDb ID resolved from TMDb"
            fallback_path_used = "None"
            omdb_res = {}
            scraper_res = {}
            
            if imdb_id:
                # 1. Fetch OMDb rating first (sequential flow)
                omdb_res = await self._fetch_omdb_ratings(imdb_id, movie_id=movie_id)
                print(f"[IMDb Pipeline Audit] Movie: {movie_title}, TMDb ID: {movie_id}, IMDb ID: {imdb_id}, OMDb Result: {omdb_res}")
                
                if omdb_res.get("imdb_rating") is not None:
                    # OMDb succeeded
                    imdb_rating = omdb_res.get("imdb_rating")
                    metacritic_score = omdb_res.get("metacritic_score")
                    omdb_status = "success"
                    omdb_error = None
                    fallback_path_used = "OMDb API"
                    print(f"[IMDb Pipeline Audit] OMDb API lookup succeeded for {movie_title} (Rating: {imdb_rating})")
                else:
                    # OMDb failed or unconfigured, execute scraper fallback
                    omdb_reason = omdb_res.get("omdb_error") or "OMDb lookup returned empty rating"
                    print(f"[IMDb Pipeline Audit] OMDb failed ({omdb_reason}). Executing scraper fallback...")
                    
                    scraper_res = await self._scrape_imdb_rating(imdb_id, movie_title=movie_title)
                    
                    if scraper_res.get("status") == "success":
                        imdb_rating = scraper_res.get("rating")
                        omdb_status = "success"
                        omdb_error = None
                        fallback_path_used = "IMDb Web Scraper"
                        print(f"[IMDb Pipeline Audit] Scraper fallback succeeded for {movie_title} (Rating: {imdb_rating})")
                    else:
                        omdb_status = "error"
                        omdb_error = omdb_reason
                        fallback_path_used = "Failed Scraper Fallback"
                        print(f"[IMDb Pipeline Audit] Scraper fallback failed for {movie_title}. Reason: {omdb_error}")
            else:
                omdb_status = "error"
                omdb_error = "No IMDb ID found in TMDb"
                fallback_path_used = "None"
                print(f"[IMDb Pipeline Audit] No IMDb ID available for {movie_title} (TMDb ID: {movie_id}). Pipeline aborted.")

            # Final detailed logging summarizing the entire pipeline trace
            print(f"[IMDb Pipeline Logging Audit Summary]\n"
                  f"  * Movie Title: {movie_title}\n"
                  f"  * TMDb Movie ID: {movie_id}\n"
                  f"  * IMDb ID: {imdb_id}\n"
                  f"  * OMDb Request Result: {omdb_res if imdb_id else 'Not Attempted'}\n"
                  f"  * Scraper Execution Status: {scraper_res.get('status') if (imdb_id and omdb_res.get('imdb_rating') is None) else 'Not Attempted'}\n"
                  f"  * Scraper Extracted Rating: {scraper_res.get('rating') if (imdb_id and omdb_res.get('imdb_rating') is None) else 'Not Attempted'}\n"
                  f"  * Fallback Path Used: {fallback_path_used}\n"
                  f"  * Final IMDb Rating: {imdb_rating}")
            
            data["imdb_rating"] = imdb_rating
            data["metacritic_score"] = metacritic_score
            data["omdb_status"] = omdb_status
            data["omdb_error"] = omdb_error
            data["rating_source"] = fallback_path_used
            print(f"[TMDb Service] Final API details payload compiled: id={data.get('id')}, title={data.get('title')}, imdb_id={data.get('imdb_id')}, imdb_rating={data.get('imdb_rating')}, metacritic_score={data.get('metacritic_score')}, omdb_status={omdb_status}, omdb_error={omdb_error}")
            return data

# Instantiate service singleton
tmdb_service = TMDBService()
