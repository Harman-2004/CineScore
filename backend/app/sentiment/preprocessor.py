# preprocessor.py
# Consistent NLP Text Preprocessing Pipeline for Sentiment Classification.

import re
import string
import nltk
from typing import List

# Download NLTK stopwords if not present
try:
    from nltk.corpus import stopwords
    STOPWORDS = set(stopwords.words('english'))
except Exception:
    nltk.download('stopwords')
    from nltk.corpus import stopwords
    STOPWORDS = set(stopwords.words('english'))

# Preserve negation words in stopwords so critical sentiment shifts are retained
NEGATION_WORDS = {
    "not", "no", "nor", "neither", "never", "none", "n't", "cannot", "can't",
    "dont", "don't", "didnt", "didn't", "doesnt", "doesn't", "wasnt", "wasn't",
    "isnt", "isn't", "couldnt", "couldn't", "wouldnt", "wouldn't", "shouldnt", "shouldn't",
    "without", "against"
}
FILTERED_STOPWORDS = STOPWORDS - NEGATION_WORDS

# Emoji mapping table to preserve sentiment signals in YouTube comments
EMOJI_MAP = {
    "❤️": " love_emoji ", "😍": " love_emoji ", "🥰": " love_emoji ", "💕": " love_emoji ",
    "🔥": " fire_emoji ", "👍": " thumbsup_emoji ", "👏": " applause_emoji ", "🙌": " praise_emoji ",
    "😂": " joy_emoji ", "🤣": " joy_emoji ", "😊": " happy_emoji ", "😁": " happy_emoji ",
    "👎": " thumbsdown_emoji ", "💩": " trash_emoji ", "🤮": " vomit_emoji ", "🤢": " gross_emoji ",
    "😭": " cry_emoji ", "😡": " angry_emoji ", "🤬": " angry_emoji ", "💔": " heartbreak_emoji "
}

class TextPreprocessor:
    """
    Standardized NLP Preprocessing pipeline applied consistently across all sentiment models.
    
    Pipeline Steps:
    1. HTML Tag Removal (<br />, <p>, etc.)
    2. URL & Web Link Removal
    3. Emoji Translation to Sentiment Tokens
    4. Lowercasing
    5. Contraction Expansion & Negation Marking (e.g., 'not good' -> 'not_good')
    6. Punctuation & Special Character Removal (preserving underscore for negations)
    7. Whitespace Normalization
    8. Tokenization & Negation-Aware Stopword Removal
    """

    @staticmethod
    def replace_emojis(text: str) -> str:
        """Translates common sentiment emojis into explicit textual tokens."""
        for emoji, token in EMOJI_MAP.items():
            if emoji in text:
                text = text.replace(emoji, token)
        return text

    @staticmethod
    def expand_contractions_and_negations(text: str) -> str:
        """Expands common contractions and binds negation words to adjacent terms."""
        # Standard contractions
        text = re.sub(r"\bcan['’]t\b", "cannot", text)
        text = re.sub(r"\bwon['’]t\b", "will not", text)
        text = re.sub(r"\bn['’]t\b", " not", text)
        text = re.sub(r"\b['’]re\b", " are", text)
        text = re.sub(r"\b['’]s\b", " is", text)
        text = re.sub(r"\b['’]d\b", " would", text)
        text = re.sub(r"\b['’]ll\b", " will", text)
        text = re.sub(r"\b['’]t\b", " not", text)
        text = re.sub(r"\b['’]ve\b", " have", text)
        text = re.sub(r"\b['’]m\b", " am", text)

        # Handle explicit phrase negations like "not bad", "never boring", "could have been better"
        text = re.sub(r"\bnot\s+bad\b", "not_bad", text)
        text = re.sub(r"\bnot\s+good\b", "not_good", text)
        text = re.sub(r"\bnever\s+boring\b", "never_boring", text)
        text = re.sub(r"\bcould\s+have\s+been\s+better\b", "could_have_been_better", text)
        
        # General negation prefixing: "not great" -> "not_great"
        text = re.sub(r"\b(not|no|never|cannot)\s+([a-z]+)\b", r"\1_\2", text)
        return text

    @classmethod
    def clean_text(cls, text: str) -> str:
        """Applies full string cleaning transformation."""
        if not text or not isinstance(text, str):
            return ""

        # 1. Lowercasing
        text = text.lower()

        # 2. HTML Tag Removal
        text = re.sub(r"<[^>]+>", " ", text)

        # 3. URL Removal
        text = re.sub(r"https?://\S+|www\.\S+", " ", text)

        # 4. Emoji Translation
        text = cls.replace_emojis(text)

        # 5. Negation & Contraction Transformation
        text = cls.expand_contractions_and_negations(text)

        # 6. Punctuation Removal (preserve underscores used in negations)
        punct_to_remove = "".join([c for c in string.punctuation if c != "_"])
        text = text.translate(str.maketrans(punct_to_remove, " " * len(punct_to_remove)))

        # 7. Whitespace Normalization
        text = re.sub(r"\s+", " ", text).strip()

        return text

    @classmethod
    def tokenize_and_remove_stopwords(cls, text: str) -> List[str]:
        """Tokenizes cleaned text and removes non-essential stopwords."""
        cleaned = cls.clean_text(text)
        tokens = cleaned.split()
        filtered = [t for t in tokens if t not in FILTERED_STOPWORDS and len(t) > 1]
        return filtered

    @classmethod
    def preprocess(cls, text: str) -> str:
        """
        Returns normalized preprocessed text string suitable for TF-IDF Vectorizer and Word2Vec.
        """
        tokens = cls.tokenize_and_remove_stopwords(text)
        return " ".join(tokens)

# Singleton instance
preprocessor = TextPreprocessor()
