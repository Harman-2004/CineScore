import re
import torch
import torch.nn.functional as F
from typing import Dict, Any, Tuple, Optional
from app.config import settings

# Lexicon for dictionary fallback (offline/download limits)
POSITIVE_LEXICON = {
    "love", "loved", "loves", "loving", "great", "excellent", "awesome", "wonderful", "amazing",
    "good", "nice", "beautiful", "fantastic", "perfect", "masterpiece", "masterful", "brilliant",
    "superb", "enjoy", "enjoyed", "enjoyable", "glad", "happy", "thrilled", "favorite", "recommend",
    "outstanding", "spectacular", "entertaining", "fascinating", "compelling", "gripping", "smart",
    "fun", "funny", "original", "stunning", "gem", "classic", "satisfying", "refreshing"
}

NEGATIVE_LEXICON = {
    "hate", "hated", "hates", "hating", "bad", "terrible", "awful", "horrible", "worst", "poor",
    "waste", "boring", "bored", "dislike", "disliked", "disappointing", "disappointed", "disappointment",
    "fail", "failed", "failure", "stupid", "dumb", "annoying", "annoyed", "frustrated", "rubbish",
    "trash", "garbage", "pointless", "ridiculous", "lame", "predictable", "slow", "uninteresting",
    "wasted", "dull", "badly", "cliché", "mess", "mediocre", "disaster", "cheap", "silly"
}

class SentimentService:
    def __init__(self):
        self.model_name = "distilbert-base-uncased-finetuned-sst-2-english"
        self._tokenizer = None
        self._model = None
        self._model_loaded = False
        self._load_error = False

    def _lazy_load_model(self):
        """
        Lazily loads the Hugging Face tokenizer and model.
        Prevents app startup delays and handles download failures gracefully.
        """
        if self._model_loaded or self._load_error:
            return
            
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            print(f"Loading Hugging Face model: {self.model_name}...")
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name, local_files_only=False)
            self._model = AutoModelForSequenceClassification.from_pretrained(self.model_name, local_files_only=False)
            self._model.eval()
            self._model_loaded = True
            print("Hugging Face sentiment analysis model loaded successfully.")
        except Exception as e:
            self._load_error = True
            print(f"WARNING: Hugging Face model download failed or offline. Using local lexicon fallback. Details: {e}")

    def _fallback_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Pure Python fallback dictionary sentiment analyzer.
        Counts positive/negative words and calculates soft softmax probabilities.
        """
        words = re.findall(r"\b\w+\b", text.lower())
        if not words:
            return {
                "positive_score": 0.5,
                "negative_score": 0.5,
                "final_sentiment": "NEUTRAL",
                "method": "local_lexicon_fallback_empty"
            }
            
        pos_count = sum(1 for w in words if w in POSITIVE_LEXICON)
        neg_count = sum(1 for w in words if w in NEGATIVE_LEXICON)
        
        pos_raw = float(pos_count)
        neg_raw = float(neg_count)
        
        exp_pos = torch.exp(torch.tensor(pos_raw * 0.5)).item()
        exp_neg = torch.exp(torch.tensor(neg_raw * 0.5)).item()
        sum_exp = exp_pos + exp_neg
        
        pos_prob = exp_pos / sum_exp
        neg_prob = exp_neg / sum_exp
        
        if pos_prob > 0.58:
            label = "POSITIVE"
        elif neg_prob > 0.58:
            label = "NEGATIVE"
        else:
            label = "NEUTRAL"
            
        return {
            "positive_score": round(pos_prob, 4),
            "negative_score": round(neg_prob, 4),
            "final_sentiment": label,
            "method": "local_lexicon_fallback"
        }

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyzes movie review text sentiment using Hugging Face DistilBERT.
        Falls back to rule-based lexicon if Hugging Face/offline errors occur.
        """
        if not text or not text.strip():
            return {
                "positive_score": 0.5,
                "negative_score": 0.5,
                "final_sentiment": "NEUTRAL",
                "method": "empty_input"
            }
            
        self._lazy_load_model()
        
        if not self._model_loaded:
            return self._fallback_sentiment(text)
            
        try:
            inputs = self._tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            
            with torch.no_grad():
                outputs = self._model(**inputs)
                
            probs = F.softmax(outputs.logits, dim=-1).squeeze().tolist()
            
            if isinstance(probs, float):
                probs = [1.0 - probs, probs]
                
            neg_score = probs[0]
            pos_score = probs[1]
            
            if pos_score > 0.60:
                final_sentiment = "POSITIVE"
            elif neg_score > 0.60:
                final_sentiment = "NEGATIVE"
            else:
                final_sentiment = "NEUTRAL"
                
            return {
                "positive_score": round(float(pos_score), 4),
                "negative_score": round(float(neg_score), 4),
                "final_sentiment": final_sentiment,
                "method": "hugging_face_transformers"
            }
        except Exception as e:
            print(f"Hugging Face runtime error: {e}. Falling back to lexicon.")
            return self._fallback_sentiment(text)

    def convert_sentiment_to_rating(self, sentiment_result: Dict[str, Any]) -> float:
        """
        Utility that converts a neural sentiment result into a movie rating out of 10:
        - POSITIVE: Maps to the 8.0 to 10.0 range.
        - NEUTRAL: Maps to exactly 5.0.
        - NEGATIVE: Maps to the 1.0 to 3.0 range.
        """
        label = sentiment_result.get("final_sentiment", "NEUTRAL")
        pos_score = sentiment_result.get("positive_score", 0.5)
        neg_score = sentiment_result.get("negative_score", 0.5)
        
        if label == "POSITIVE":
            # Map 0.5 to 1.0 positive confidence score linearly to 8.0 to 10.0 range
            norm = max(0.0, min(1.0, (pos_score - 0.5) / 0.5)) if pos_score > 0.5 else 0.0
            rating = 8.0 + (norm * 2.0)
            return round(rating, 1)
        elif label == "NEGATIVE":
            # Map 0.5 to 1.0 negative confidence score linearly to 1.0 to 3.0 range
            norm = max(0.0, min(1.0, (neg_score - 0.5) / 0.5)) if neg_score > 0.5 else 0.0
            # Higher negative probability yields a score closer to 1.0
            rating = 3.0 - (norm * 2.0)
            return round(rating, 1)
        else:
            return 5.0

    def analyze_aspects(self, text: str) -> Dict[str, float]:
        """
        Analyzes the review text and extracts separate sentiment ratings (out of 10)
        for acting, story, music, visual effects, and direction.
        Uses sentence-based keyword mapping and neural/lexicon sentiment models.
        """
        if not text or not text.strip():
            return {
                "acting": 5.0,
                "story": 5.0,
                "music": 5.0,
                "visual_effects": 5.0,
                "direction": 5.0
            }

        # Aspect Keywords List
        aspect_keywords = {
            "acting": ["act", "acting", "actor", "actors", "actress", "cast", "performance", "performances", "play", "role", "roles"],
            "story": ["story", "plot", "script", "screenplay", "writing", "theme", "themes", "premise", "pacing"],
            "music": ["music", "song", "songs", "score", "soundtrack", "zimmer", "melody", "sound", "audio", "musical"],
            "visual_effects": ["effects", "visual", "visuals", "cgi", "sfx", "cinematography", "camera", "lighting", "aesthetic"],
            "direction": ["directing", "direction", "director", "nolan", "filmmaking", "filmmaker", "directs", "directed"]
        }

        # Split review into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Determine global sentiment rating of the review as a baseline fallback
        global_result = self.analyze_text(text)
        global_score = self.convert_sentiment_to_rating(global_result)

        aspect_scores = {}

        for aspect, keywords in aspect_keywords.items():
            # Find sentences matching keywords for this specific aspect
            matching_sentences = []
            for s in sentences:
                s_lower = s.lower()
                if any(re.search(r'\b' + re.escape(k) + r'\b', s_lower) for k in keywords):
                    matching_sentences.append(s)

            if matching_sentences:
                # Evaluate sentiment of sentences that mention this aspect explicitly
                combined_text = " ".join(matching_sentences)
                aspect_result = self.analyze_text(combined_text)
                aspect_score = self.convert_sentiment_to_rating(aspect_result)
                aspect_scores[aspect] = aspect_score
            else:
                # Fallback to a soft deterministic variation of the global review rating
                hash_val = sum(ord(c) for c in aspect) % 5
                noise = (hash_val - 2) * 0.2
                fallback_score = max(1.0, min(10.0, global_score + noise))
                aspect_scores[aspect] = round(fallback_score, 1)

        return aspect_scores

# Instantiate service singleton
sentiment_service = SentimentService()
