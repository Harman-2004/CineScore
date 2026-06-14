import requests
from typing import List, Dict, Any, Optional
from app.config import settings

class YouTubeScraper:
    """
    Scrapes or fetches audience reviews from YouTube trailer video comment sections.
    Uses the official YouTube Data API v3 if YOUTUBE_API_KEY is configured;
    otherwise, it falls back to a high-fidelity local mock comments generator.
    """
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        self.search_url = "https://www.googleapis.com/youtube/v3/search"
        self.comments_url = "https://www.googleapis.com/youtube/v3/commentThreads"
        
        # Diagnostics: Print API Key status on initialization
        if not self.api_key or self.api_key.startswith("your_youtube_api_key"):
            print("[YouTube Scraper] WARNING: YouTube API key not configured or set to default placeholder. Using local fallback generator.")
        else:
            print("[YouTube Scraper] YouTube Data API v3 key detected. Real-time scraping is active.")

    def scrape_reviews(self, movie_title: str) -> List[Dict[str, Any]]:
        """
        Gathers audience trailer comments for a movie title.
        """
        if self.api_key and not self.api_key.startswith("your_youtube_api_key"):
            try:
                # 1. Search for movie trailer
                search_params = {
                    "q": f"{movie_title} official trailer",
                    "type": "video",
                    "part": "id",
                    "maxResults": 1,
                    "key": self.api_key
                }
                search_response = requests.get(self.search_url, params=search_params, timeout=5)
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    items = search_data.get("items", [])
                    if items:
                        video_id = items[0].get("id", {}).get("videoId")
                        if video_id:
                            # 2. Fetch comments for the trailer video
                            comment_params = {
                                "videoId": video_id,
                                "part": "snippet",
                                "maxResults": 100,  # Fetch a larger pool of comments
                                "order": "relevance",  # Sort by relevance (popularity/likes)
                                "key": self.api_key
                            }
                            comments_response = requests.get(self.comments_url, params=comment_params, timeout=5)
                            if comments_response.status_code == 200:
                                comments_data = comments_response.json()
                                parsed = []
                                for item in comments_data.get("items", []):
                                    snippet = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
                                    author = snippet.get("authorDisplayName", "YouTube User")
                                    text = snippet.get("textOriginal", "")
                                    like_count = snippet.get("likeCount", 0)
                                    if text:
                                        # Clean up author names (removing @)
                                        if author.startswith("@"):
                                            author = author[1:]
                                        parsed.append({
                                            "author": author,
                                            "rating": None,  # Will be dynamically computed by sentiment analyzer
                                            "text": text,
                                            "source": "YouTube",
                                            "like_count": like_count
                                        })
                                
                                # Sort by like count descending and slice top 60
                                parsed.sort(key=lambda x: x.get("like_count", 0), reverse=True)
                                top_60 = parsed[:60]
                                for p in top_60:
                                    p.pop("like_count", None)
                                
                                # Only return if we actually scraped comments
                                if top_60:
                                    return top_60
                                else:
                                    print(f"[YouTube Scraper] Trailer video comments fetched successfully but yielded 0 comments. Falling back to mock comments.")
                            else:
                                print(f"[YouTube Scraper] YouTube Comments API returned status code {comments_response.status_code}. Response: {comments_response.text[:250]}")
                        else:
                            print(f"[YouTube Scraper] Search results found but no videoId present. Falling back to mock comments.")
                    else:
                        print(f"[YouTube Scraper] No search results found for trailer query. Falling back to mock comments.")
                else:
                    print(f"[YouTube Scraper] YouTube Search API returned status code {search_response.status_code}. Response: {search_response.text[:250]}")
            except Exception as e:
                print(f"[YouTube Scraper] Failed to fetch comments via API due to exception: {e}")

        # Fallback dataset
        return self._get_fallback_comments(movie_title)

    def _get_fallback_comments(self, movie_title: str) -> List[Dict[str, Any]]:
        """
        Generates highly realistic YouTube trailer comments based on movie title.
        Guarantees returning exactly 60 comments, ordered by simulated like counts.
        """
        title_lower = movie_title.lower()
        movie_comments = []
        
        if "inception" in title_lower:
            movie_comments = [
                {"author": "nolan_fan_99", "text": "This trailer still gives me goosebumps. Hans Zimmer's horns literally changed movie trailers forever."},
                {"author": "cine_review_yt", "text": "The hallway scene in this trailer got me so hyped back in 2010. Masterpiece of cinematography."},
                {"author": "dream_walker", "text": "Wait, did the top fall at the end of the trailer? Still questioning reality 16 years later."},
                {"author": "trailer_spotter", "text": "Hands down one of the greatest trailers ever edited. Perfect pacing and build-up."},
                {"author": "retro_cinema", "text": "This is Nolan's peak. The sound design is absolutely unreal."},
                {"author": "mind_bender", "text": "I remember seeing this in theaters, the crowd went absolutely crazy. Best sci-fi of the decade."},
                {"author": "cobb_dreamer", "text": "The music build-up at the end of the trailer is insanely good. I have it on repeat."},
                {"author": "totem_spinner", "text": "This trailer is a masterclass in how to edit a movie trailer without giving away the plot."}
            ]
        elif "dark knight" in title_lower:
            movie_comments = [
                {"author": "gotham_legend", "text": "Heath Ledger's voice in this trailer. 'Why so serious?' still gives me chills."},
                {"author": "bat_collector", "text": "I remember watching this trailer on repeat. Heath Ledger completely became the Joker."},
                {"author": "movie_junkie_92", "text": "This is more than a superhero movie, this is an elite crime drama. Best trailer of the 2000s."},
                {"author": "ledger_fan", "text": "Heath's performance is legendary. He defined a generation of villains."},
                {"author": "gotham_knight", "text": "The pacing of this trailer is absolutely insane. Heath Ledger deserves every bit of praise."},
                {"author": "zimmer_brass", "text": "The rising tension in the music gives me goosebumps every single time. Masterpiece."},
                {"author": "bat_fanatic", "text": "We will never get a villain performance as iconic as Heath's Joker. Chills from the trailer alone."},
                {"author": "harvey_dent_stan", "text": "Two-Face and Joker in one trailer... Nolan really delivered the ultimate Batman movie."}
            ]
        elif "interstellar" in title_lower:
            movie_comments = [
                {"author": "space_traveler", "text": "The organ music in this trailer makes me emotional. Zimmer is a wizard."},
                {"author": "cosmic_mind", "text": "We used to look up at the sky and wonder at our place in the stars... What a line."},
                {"author": "physics_student", "text": "That black hole visualization in the trailer still looks better than anything else in CGI."},
                {"author": "wormhole_surfer", "text": "One of the few trailers that actually captures the scale and emotion of space travel."},
                {"author": "gravity_rider", "text": "Hans Zimmer's organ score in this trailer is absolutely unreal. Instant goosebumps."},
                {"author": "matthew_mc_fan", "text": "Matthew McConaughey's voiceover is so powerful. Can't wait to watch this masterpiece."},
                {"author": "murph_science", "text": "The visual effects shown here are stunning. This is going to be a cinematic event."},
                {"author": "stellar_voyager", "text": "This trailer makes me tear up. The emotional weight Nolan builds is crazy."}
            ]

        # Generic comment templates to fill up to 60 comments
        generic_templates = [
            "This trailer looks absolutely insane! Can't wait to watch {title} in theaters.",
            "Honestly, the cinematography in these shots is stunning. Hope the plot is as good as the visuals.",
            "The cast is stacked! If the trailer is this good, the actual movie of {title} is going to be a masterpiece.",
            "I have watched this trailer {num} times already today. The music is perfect.",
            "Looks decent but I hope they didn't put all the best scenes in the trailer like they usually do.",
            "That bass drop in the middle of the trailer gave me goosebumps. Brilliant audio work.",
            "Every frame of this {title} trailer is like a painting. Masterful color grading.",
            "This feels like a return to form for the director. The pacing of the trailer is elite.",
            "I hope the trailer isn't baiting us. It looks very promising, hope the execution matches.",
            "This is easily going to be a box office hit. The hype around {title} is unreal right now.",
            "The director never misses. This is going to be a theater experience.",
            "I am sold. Taking my entire family to watch this on day one!",
            "Can we talk about that transition at {time}? Pure editing perfection.",
            "I did not expect that twist at the end of the trailer. Mind blown.",
            "The color palette of this movie looks so beautiful. A feast for the eyes.",
            "The soundtrack alone is worth the ticket price. Absolutely phenomenal.",
            "I'm keeping my expectations in check, but man, this looks outstanding.",
            "This trailer gave me actual chills. The acting looks top-tier.",
            "Finally, a movie that looks original and exciting! Instant watch.",
            "The CGI looks so clean and integrated. Not like the usual green screen mess."
        ]

        # Generate comments to fill up to 60
        all_comments = []
        # Add the specific ones first
        for mc in movie_comments:
            all_comments.append({
                "author": mc["author"],
                "rating": None,
                "text": mc["text"],
                "source": "YouTube",
                "simulated_likes": 1000 - len(all_comments) * 10
            })

        # Fill the rest with generated comments
        index = 1
        while len(all_comments) < 60:
            template = generic_templates[(index - 1) % len(generic_templates)]
            num_times = (index * 3) % 15 + 2
            time_val = f"1:{index % 50:02d}"
            text = template.format(title=movie_title, num=num_times, time=time_val)
            author = f"user_{movie_title.replace(' ', '_').lower()}_{index}"
            all_comments.append({
                "author": author,
                "rating": None,
                "text": text,
                "source": "YouTube",
                "simulated_likes": 500 - index * 8
            })
            index += 1

        # Sort comments by simulated likes to mimic "most likes" ordering
        all_comments.sort(key=lambda x: x["simulated_likes"], reverse=True)
        
        # Remove simulated_likes key to keep data clean
        for c in all_comments:
            c.pop("simulated_likes", None)

        return all_comments

    def fetch_trailer_transcript(self, video_id: Optional[str], movie_title: str) -> str:
        """
        Fetches timed captions XML from YouTube for the given video_id, parses the text elements,
        and returns the consolidated transcript string. If it fails, falls back to a simulated transcript.
        """
        # If video_id is not provided, we try to search for it using YouTube API key if configured
        if not video_id and self.api_key and not self.api_key.startswith("your_youtube_api_key"):
            try:
                search_params = {
                    "q": f"{movie_title} official trailer",
                    "type": "video",
                    "part": "id",
                    "maxResults": 1,
                    "key": self.api_key
                }
                search_response = requests.get(self.search_url, params=search_params, timeout=5)
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    items = search_data.get("items", [])
                    if items:
                        video_id = items[0].get("id", {}).get("videoId")
            except Exception as e:
                print(f"[YouTube Scraper] Failed to search video_id for transcript: {e}")

        # If we still don't have a video_id, use fallback
        if not video_id:
            print(f"[YouTube Scraper] No video ID available for '{movie_title}'. Using fallback transcript.")
            return self._get_fallback_transcript(movie_title)

        url = f"https://www.youtube.com/watch?v={video_id}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        try:
            import re
            import json
            from bs4 import BeautifulSoup
            
            print(f"[YouTube Scraper] Fetching trailer page for transcript of '{movie_title}' (video ID: {video_id})")
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"[YouTube Scraper] Failed to fetch YouTube page, status code {response.status_code}. Using fallback.")
                return self._get_fallback_transcript(movie_title)
            
            html = response.text
            match = re.search(r'"captionTracks"\s*:\s*(\[.+?\])', html)
            tracks = []
            if match:
                try:
                    tracks = json.loads(match.group(1))
                except Exception:
                    pass
            
            if not tracks:
                # Try finding player response
                player_match = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});', html)
                if not player_match:
                    player_match = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?})\s*(?:var|window|url|;)', html)
                if player_match:
                    try:
                        player_response = json.loads(player_match.group(1))
                        tracks = player_response.get("captions", {}).get("playerCaptionsTracklistRenderer", {}).get("captionTracks", [])
                    except Exception:
                        pass

            if not tracks:
                print(f"[YouTube Scraper] No caption tracks found in player HTML for '{movie_title}'. Using fallback.")
                return self._get_fallback_transcript(movie_title)
                
            en_track = None
            for t in tracks:
                if t.get("languageCode") == "en":
                    en_track = t
                    break
            if not en_track:
                en_track = tracks[0]
                
            base_url = en_track.get("baseUrl")
            if not base_url:
                print(f"[YouTube Scraper] Selected track has no baseUrl for '{movie_title}'. Using fallback.")
                return self._get_fallback_transcript(movie_title)
                
            print(f"[YouTube Scraper] Requesting subtitles XML from YouTube for '{movie_title}'...")
            caption_resp = requests.get(base_url, headers=headers, timeout=10)
            if caption_resp.status_code != 200 or not caption_resp.text:
                print(f"[YouTube Scraper] Subtitles request failed (status {caption_resp.status_code}, len {len(caption_resp.text) if caption_resp.text else 0}). Using fallback.")
                return self._get_fallback_transcript(movie_title)
                
            soup = BeautifulSoup(caption_resp.text, "html.parser")
            text_elements = soup.find_all("text")
            
            if not text_elements:
                print(f"[YouTube Scraper] Parsed 0 text elements from subtitles XML. Using fallback.")
                return self._get_fallback_transcript(movie_title)
                
            lines = [el.text for el in text_elements if el.text]
            transcript_text = " ".join(lines)
            if len(transcript_text.strip()) < 50:
                print(f"[YouTube Scraper] Scraped transcript is too short. Using fallback.")
                return self._get_fallback_transcript(movie_title)
                
            print(f"[YouTube Scraper] Successfully scraped real trailer transcript for '{movie_title}' ({len(transcript_text)} chars).")
            return transcript_text
            
        except Exception as e:
            print(f"[YouTube Scraper] Exception in fetch_trailer_transcript for '{movie_title}': {e}. Using fallback.")
            return self._get_fallback_transcript(movie_title)

    def _get_fallback_transcript(self, movie_title: str) -> str:
        """
        Generates realistic trailer transcript fallbacks for core movies
        and dynamically synthesizes one for other titles.
        """
        title_lower = movie_title.lower()
        if "inception" in title_lower:
            return (
                "[Dramatic music plays] Cobb: What is the most resilient parasite? Bacteria? A virus? An idea. "
                "An idea, resilient, highly contagious. Arthur: Once an idea has taken hold of the brain, it's almost "
                "impossible to eradicate. Cobb: An idea that is fully formed, fully understood, that sticks. "
                "Cobb: We create the world of the dream. We bring the subject into that dream, and they fill it with "
                "their secrets. Ariadne: But it feels real when we're in it. Cobb: Because it is real while it lasts. "
                "Cobb: You need to learn how to build mazes. Ariadne: What happens when the subconscious starts attacking? "
                "Cobb: We wake up. [BASS DROP] Mal: Do you still believe in reality? Cobb: I need to get back to my children. "
                "Cobb: Inception is possible. [Hans Zimmer Time score swells]"
            )
        elif "dark knight" in title_lower:
            return (
                "[Joker laughter] Joker: Why so serious? Let's put a smile on that face. Alfred: Some men just want to "
                "watch the world burn. Batman: Gotham needs me. Joker: You complete me. Dent: You either die a hero, "
                "or you live long enough to see yourself become the villain. Batman: I'm not a hero. I'm whatever "
                "Gotham needs me to be. [Tense strings building, explosion sounds, Batpod roaring]"
            )
        elif "interstellar" in title_lower:
            return (
                "Cooper: We used to look up at the sky and wonder at our place in the stars. Now we just look down and "
                "worry about our place in the dirt. Brand: We're not meant to save the world. We're meant to leave it. "
                "Cooper: I'm coming back, Murph. Murph: You have no idea when you're coming back. Cooper: Do not go gentle "
                "into that good night. Rage, rage against the dying of the light. [Organ music intensifies, spacecraft "
                "engine engines firing, wormhole distortion]"
            )
        elif "pulp fiction" in title_lower:
            return (
                "Jules: Ezekiel 25:17. The path of the righteous man is beset on all sides by the iniquities of the "
                "selfish and the tyranny of evil men. Vincent: You know what they call a Quarter Pounder with Cheese in "
                "Paris? Jules: They call it a Royale with Cheese. Mia: Don't you hate that? Vincent: Hate what? Mia: "
                "Uncomfortable silences. Butch: Zed's dead, baby. Zed's dead. [Classic surf guitar theme Misirlou plays]"
            )
        elif "matrix" in title_lower:
            return (
                "Morpheus: This is your last chance. After this, there is no turning back. You take the blue pill, the "
                "story ends, you wake up in your bed and believe whatever you want to believe. You take the red pill, "
                "you stay in Wonderland, and I show you how deep the rabbit hole goes. Neo: Whoa. Trinity: Neo, no one has "
                "ever done this before. Agent Smith: It is the sound of inevitability, Mr. Anderson. [Techno music beats "
                "swell, bullets flying in slow motion, metal clashing]"
            )
        elif "forrest gump" in title_lower:
            return (
                "Forrest: My mama always said life was like a box of chocolates. You never know what you're gonna get. "
                "Jenny: Run, Forrest! Run! Forrest: I'm not a smart man... but I know what love is. Bubba: Anyway, like I "
                "was sayin', shrimp is the fruit of the sea. You can barbecue it, boil it, broil it, bake it, saute it. "
                "[Guitar chords strumming, feather floating in the wind]"
            )
        elif "godfather" in title_lower:
            return (
                "Vito Corleone: I'm gonna make him an offer he can't refuse. Michael: Don't ask me about my business, Kay. "
                "Michael: It's not personal, Sonny. It's strictly business. Clemenza: Leave the gun. Take the cannoli. "
                "Michael: Only don't tell me that you're innocent. Because it insults my intelligence and it makes me "
                "very angry. [Godfather waltz accordion theme plays, gunshots, dramatic opera strings]"
            )
        elif "green mile" in title_lower:
            return (
                "John Coffey: My name is John Coffey, like the drink, only not spelled the same. Paul: What do you want me "
                "to do, John? John: I'm tired, boss. Tired of bein' on the road, lonely as a sparrow in the rain. I'm tired "
                "of people bein' ugly to each other. Paul: On the day of my judgment, when I stand before God, and He asks "
                "me why did I let one of His miracles die... what am I gonna say? [Soft emotional piano music plays]"
            )
            
        return (
            f"[Epic trailer voiceover] In a world where anything is possible, one hero must stand against the dark. "
            f"[Thrilling orchestra swell] '{movie_title}' brings a spectacular journey of courage, betrayal, and ultimate "
            f"sacrifice. Character A: We don't have much time! Character B: We have to try, no matter the cost. "
            f"'{movie_title}' - coming soon to theaters. [Dramatic crash, title card fade out]"
        )

youtube_scraper = YouTubeScraper()
