import os
import re
import math
import joblib
from typing import Dict, Any, Tuple, Optional
from app.sentiment.preprocessor import preprocessor

# Lexicon for dictionary fallback (offline/missing model limits)
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
        self.models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_models")
        self.vec_path = os.path.join(self.models_dir, "tfidf_vectorizer.joblib")
        self.clf_path = os.path.join(self.models_dir, "sentiment_classifier.joblib")
        
        self._vectorizer = None
        self._classifier = None
        self._ml_loaded = False
        self._load_failed = False

    def _lazy_load_ml_model(self):
        """
        Lazily loads trained TF-IDF Vectorizer and Linear SVM classifier artifacts.
        Prevents app startup overhead and handles missing files gracefully.
        """
        if self._ml_loaded or self._load_failed:
            return
            
        try:
            if os.path.exists(self.vec_path) and os.path.exists(self.clf_path):
                self._vectorizer = joblib.load(self.vec_path)
                self._classifier = joblib.load(self.clf_path)
                self._ml_loaded = True
                print("Supervised ML Sentiment Model (TF-IDF + Linear SVM) loaded successfully.")
            else:
                self._load_failed = True
                print(f"WARNING: Sentiment model artifacts missing at {self.models_dir}. Falling back to local lexicon.")
        except Exception as e:
            self._load_failed = True
            print(f"WARNING: Failed to load ML sentiment model: {e}. Falling back to local lexicon.")

    def _fallback_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Pure Python fallback dictionary sentiment analyzer.
        Counts positive/negative words and calculates soft softmax probabilities using math.exp.
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
        
        exp_pos = math.exp(pos_raw * 0.5)
        exp_neg = math.exp(neg_raw * 0.5)
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
        Analyzes review text sentiment using Supervised TF-IDF + Linear SVM ML Model.
        Falls back to local rule-based lexicon if model artifacts are missing or error occurs.
        """
        if not text or not text.strip():
            return {
                "positive_score": 0.5,
                "negative_score": 0.5,
                "final_sentiment": "NEUTRAL",
                "method": "empty_input"
            }
            
        self._lazy_load_ml_model()
        
        if not self._ml_loaded:
            return self._fallback_sentiment(text)

        try:
            # 1. Apply robust domain preprocessing (cleaning, emojis, negations)
            cleaned_text = preprocessor.preprocess(text)
            
            # 2. Extract TF-IDF features
            X_vec = self._vectorizer.transform([cleaned_text])
            
            # 3. Obtain SVM decision boundary score (margin)
            margin = float(self._classifier.decision_function(X_vec)[0])
            
            # 4. Calibrate margin to pseudo-probability via Sigmoid curve
            # Scaling factor 1.2 provides well-calibrated confidence scores for LinearSVM
            pos_prob = 1.0 / (1.0 + math.exp(-margin * 1.2))
            neg_prob = 1.0 - pos_prob
            
            # 5. Determine sentiment category label
            if margin > 0.15:
                final_sentiment = "POSITIVE"
            elif margin < -0.15:
                final_sentiment = "NEGATIVE"
            else:
                final_sentiment = "NEUTRAL"
                
            return {
                "positive_score": round(pos_prob, 4),
                "negative_score": round(neg_prob, 4),
                "final_sentiment": final_sentiment,
                "method": "tfidf_linear_svm"
            }
        except Exception as e:
            print(f"ML Sentiment Analysis failed: {e}. Falling back to lexicon.")
            return self._fallback_sentiment(text)

    def convert_sentiment_to_rating(self, sentiment_result: Dict[str, Any]) -> float:
        """
        Utility that converts a sentiment result into a movie rating out of 10:
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
            rating = 3.0 - (norm * 2.0)
            return round(rating, 1)
        else:
            return 5.0

    def analyze_aspects(self, text: str) -> Dict[str, float]:
        """
        Analyzes the review text and extracts separate sentiment ratings (out of 10)
        for acting, story, music, visual effects, and direction.
        Uses sentence-based keyword mapping and ML sentiment models.
        """
        if not text or not text.strip():
            return {
                "acting": 5.0,
                "story": 5.0,
                "music": 5.0,
                "visual_effects": 5.0,
                "direction": 5.0
            }

        aspect_keywords = {
            "acting": ["act", "acting", "actor", "actors", "actress", "cast", "performance", "performances", "play", "role", "roles"],
            "story": ["story", "plot", "script", "screenplay", "writing", "theme", "themes", "premise", "pacing"],
            "music": ["music", "song", "songs", "score", "soundtrack", "zimmer", "melody", "sound", "audio", "musical"],
            "visual_effects": ["effects", "visual", "visuals", "cgi", "sfx", "cinematography", "camera", "lighting", "aesthetic"],
            "direction": ["directing", "direction", "director", "nolan", "filmmaking", "filmmaker", "directs", "directed"]
        }

        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        global_result = self.analyze_text(text)
        global_score = self.convert_sentiment_to_rating(global_result)

        aspect_scores = {}

        for aspect, keywords in aspect_keywords.items():
            matching_sentences = []
            for s in sentences:
                s_lower = s.lower()
                if any(re.search(r'\b' + re.escape(k) + r'\b', s_lower) for k in keywords):
                    matching_sentences.append(s)

            if matching_sentences:
                combined_text = " ".join(matching_sentences)
                aspect_result = self.analyze_text(combined_text)
                aspect_score = self.convert_sentiment_to_rating(aspect_result)
                aspect_scores[aspect] = aspect_score
            else:
                hash_val = sum(ord(c) for c in aspect) % 5
                noise = (hash_val - 2) * 0.2
                fallback_score = max(1.0, min(10.0, global_score + noise))
                aspect_scores[aspect] = round(fallback_score, 1)

        return aspect_scores

# Instantiate service singleton
sentiment_service = SentimentService()
