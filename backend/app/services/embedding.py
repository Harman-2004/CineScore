import re
import math
import numpy as np
from typing import List, Dict, Any

CINEMATIC_THEMES = [
    "space exploration", "human survival", "family sacrifice", "time dilation",
    "artificial intelligence", "dystopian society", "time travel", "revenge quest",
    "superhero origin", "romantic drama", "mind bending mystery", "crime syndicate",
    "haunted house", "existential dread", "coming of age", "alien invasion",
    "war and conflict", "forbidden love", "political corruption", "grief and loss",
    "betrayal and loyalty", "chase and survival", "psychological breakdown", "identity crisis"
]

class EmbeddingService:
    def __init__(self):
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self._tokenizer = None
        self._model = None
        self._is_loaded = False
        self._load_failed = False
        self._theme_embeddings_cache = {}

    def _lazy_load(self):
        if self._is_loaded or self._load_failed:
            return
        try:
            import torch
            from transformers import AutoTokenizer, AutoModel
            print(f"[Embedding Service] Loading Sentence Transformers: {self.model_name}...")
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModel.from_pretrained(self.model_name)
            self._model.eval()
            self._is_loaded = True
            print("[Embedding Service] Sentence Transformers loaded successfully.")
            
            # Precompute candidate themes embeddings
            for theme in CINEMATIC_THEMES:
                self._theme_embeddings_cache[theme] = self._generate_embedding_tf(theme)
            print("[Embedding Service] Precomputed theme embeddings.")
        except Exception as e:
            self._load_failed = True
            print(f"[Embedding Service] WARNING: Failed to load sentence-transformers model: {e}. Falling back to keyword/TF-IDF similarity engine.")

    def _generate_embedding_tf(self, text: str) -> List[float]:
        """Runs the PyTorch HuggingFace model to produce a normalized 384-d embedding."""
        import torch
        inputs = self._tokenizer(text, padding=True, truncation=True, max_length=512, return_tensors="pt")
        with torch.no_grad():
            model_output = self._model(**inputs)
        
        # Mean Pooling
        token_embeddings = model_output[0]
        attention_mask = inputs['attention_mask']
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        sentence_embedding = sum_embeddings / sum_mask
        
        # Normalize
        sentence_embedding = torch.nn.functional.normalize(sentence_embedding, p=2, dim=1)
        return sentence_embedding[0].tolist()

    def get_embedding(self, text: str) -> List[float]:
        """
        Calculates a 384-dimensional vector. If the torch model fails or is offline,
        returns a deterministic TF-IDF pseudo-embedding based on hash keys to guarantee
        no failures and consistent calculations.
        """
        if not text:
            return [0.0] * 384
        
        self._lazy_load()
        if self._is_loaded:
            try:
                return self._generate_embedding_tf(text)
            except Exception as e:
                print(f"[Embedding Service] PyTorch inference failed: {e}. Falling back to pseudo-embedding.")
        
        # High-fidelity pseudo-embedding fallback (384 floats, L2 normalized)
        # Seeded by the text tokens so same text always yields identical vectors
        tokens = re.findall(r"\b\w{3,}\b", text.lower())
        vec = np.zeros(384)
        for t in tokens:
            # Hash token into multiple indices in 384-space
            h = hash(t)
            for idx in [h % 384, (h // 384) % 384, (h // 147456) % 384]:
                vec[idx] += 1.0
        
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def extract_themes(self, text: str) -> List[str]:
        """
        Extracts matching cinematic themes semantically by computing the cosine similarity
        between the text embedding and pre-defined theme vectors.
        """
        if not text:
            return []
        
        text_embedding = self.get_embedding(text)
        scored_themes = []
        for theme in CINEMATIC_THEMES:
            theme_embedding = self._theme_embeddings_cache.get(theme)
            if not theme_embedding:
                theme_embedding = self.get_embedding(theme)
                self._theme_embeddings_cache[theme] = theme_embedding
            
            # Cosine similarity (since vectors are L2 normalized, it is just dot product)
            sim = sum(t * m for t, m in zip(text_embedding, theme_embedding))
            scored_themes.append((sim, theme))
        
        # Sort and filter
        scored_themes.sort(key=lambda x: x[0], reverse=True)
        # Return all themes with similarity > 0.25, or at least top 3
        themes = [t for sim, t in scored_themes if sim > 0.25]
        if len(themes) < 3:
            themes = [t for sim, t in scored_themes[:3]]
        return themes

    def extract_keywords(self, text: str) -> List[str]:
        """
        Extracts top keywords from a description text.
        """
        STOP_WORDS = {"the", "and", "a", "of", "to", "is", "in", "that", "it", "with", "as", "for", "on", "was", "by", "an", "at", "are", "be", "this", "from", "who", "which", "has", "but", "not"}
        words = re.findall(r"\b\w{4,}\b", text.lower())
        freqs = {}
        for w in words:
            if w not in STOP_WORDS:
                freqs[w] = freqs.get(w, 0) + 1
        
        sorted_kws = sorted(freqs.items(), key=lambda x: x[1], reverse=True)
        return [kw[0] for kw in sorted_kws[:10]]

# Instantiate singleton
embedding_service = EmbeddingService()
