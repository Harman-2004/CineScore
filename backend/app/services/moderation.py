import re
from typing import Dict, Any, List, Set

SPAM_KEYWORDS = [
    "buy now", "discount", "promo", "coupon", "free click", "visit my site", "earn money",
    "make money", "subscribe", "follow me", "whatsapp", "telegram", "crypto", "bitcoin",
    "http://", "https://", "www.", "click here", "gift card", "cash prize", "check out my"
]

class ReviewModerationService:
    def __init__(self):
        self.spam_keywords = SPAM_KEYWORDS

    def analyze_review_pool(self, reviews: List[Any]) -> List[Dict[str, Any]]:
        """
        Processes a list of reviews for a movie, dynamically evaluating
        individual spambot checks, and flagging repeated (duplicate) reviews.
        """
        seen_texts: Set[str] = set()
        moderated_reviews = []

        # Sort chronologically to determine duplicates (first one is original, later ones are duplicates)
        reviews_sorted = sorted(reviews, key=lambda r: r.created_at if hasattr(r, 'created_at') and r.created_at else r.id)

        for r in reviews_sorted:
            text = r.review_text if hasattr(r, 'review_text') else r.get("review_text", "")
            rating = r.rating if hasattr(r, 'rating') else r.get("rating", 5.0)
            author = r.author if hasattr(r, 'author') else r.get("reviewer", "Anonymous")
            
            # 1. Spam & Bot Heuristic Evaluation
            is_spam = False
            is_bot = False
            spam_reasons = []
            spam_probability = 0.0

            text_clean = text.strip()
            text_lower = text_clean.lower()

            if not text_clean:
                is_spam = True
                spam_reasons.append("Empty review text")
                spam_probability = 1.0
            else:
                # Rule A: Duplicate Check (Whitespace-normalized exact matching)
                text_norm = "".join(text_lower.split())
                if text_norm in seen_texts:
                    is_spam = True
                    spam_reasons.append("Duplicate review (repeated content)")
                    spam_probability = max(spam_probability, 0.95)
                seen_texts.add(text_norm)

                # Rule B: Blacklisted Spam Keywords
                matched_keywords = [kw for kw in self.spam_keywords if kw in text_lower]
                if matched_keywords:
                    is_spam = True
                    spam_reasons.append(f"Contains promotional content: {', '.join(matched_keywords)}")
                    spam_probability = max(spam_probability, 0.85)

                # Rule C: Screaming Spam (Excessive Capitalization)
                if len(text_clean) > 15:
                    caps_count = sum(1 for c in text_clean if c.isupper())
                    caps_ratio = caps_count / len(text_clean)
                    if caps_ratio > 0.65:
                        is_spam = True
                        spam_reasons.append("Excessive capitalization (screaming)")
                        spam_probability = max(spam_probability, 0.75)

                # Rule D: Character Repetition (Spam behavior)
                # Matches 6 or more repeated consecutive characters (e.g. "greatttttt")
                if re.search(r'((.)\2{5,})', text_lower):
                    is_spam = True
                    spam_reasons.append("Excessive character repetition")
                    spam_probability = max(spam_probability, 0.70)

                # Rule E: Lexical Diversity & Repetitive Structure (Bot behavior)
                words = re.findall(r"\b\w+\b", text_lower)
                if len(words) > 15:
                    unique_ratio = len(set(words)) / len(words)
                    if unique_ratio < 0.38:
                        is_bot = True
                        spam_reasons.append("Repetitive structure (possible automated bot)")
                        spam_probability = max(spam_probability, 0.80)

                # Rule F: Low Effort Anomalous Rating
                if len(words) <= 2 and (rating == 1.0 or rating == 10.0):
                    is_spam = True
                    spam_reasons.append("Low effort rating anomaly (spam pattern)")
                    spam_probability = max(spam_probability, 0.65)

            # Compile flags
            if spam_probability >= 0.50:
                is_spam = True

            moderated_reviews.append({
                "id": r.id if hasattr(r, 'id') else r.get("id"),
                "is_spam": is_spam,
                "is_bot": is_bot,
                "spam_reasons": spam_reasons,
                "spam_probability": round(spam_probability, 2)
            })

        return moderated_reviews

# Instantiate singleton service
review_moderation_service = ReviewModerationService()
