# dataset.py
# Module for loading, creating, and stratified splitting of benchmark movie review sentiment datasets.

import os
import tarfile
import urllib.request
import re
import pandas as pd
from typing import Tuple, List, Dict, Any
from sklearn.model_selection import train_test_split

DATASET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DATASET_CSV_PATH = os.path.join(DATASET_DIR, "imdb_reviews_clean.csv")
STANFORD_IMDB_URL = "https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz"

def ensure_dataset_exists(sample_limit: int = 10000) -> pd.DataFrame:
    """
    Loads benchmark Movie Review dataset (using NLTK movie_reviews corpus & Stanford IMDb).
    Returns a balanced pandas DataFrame with 'text' and 'sentiment' (1=POSITIVE, 0=NEGATIVE).
    """
    os.makedirs(DATASET_DIR, exist_ok=True)
    
    if os.path.exists(DATASET_CSV_PATH):
        print(f"[Dataset] Loading cached movie review dataset from {DATASET_CSV_PATH}...")
        df = pd.read_csv(DATASET_CSV_PATH)
        return df

    print("[Dataset] Compiling benchmark movie reviews dataset from NLTK corpus...")
    try:
        import nltk
        nltk.download('movie_reviews', quiet=True)
        from nltk.corpus import movie_reviews
        
        pos_files = movie_reviews.fileids('pos')
        neg_files = movie_reviews.fileids('neg')
        
        pos_texts = [" ".join(movie_reviews.words(fileid)) for fileid in pos_files]
        neg_texts = [" ".join(movie_reviews.words(fileid)) for fileid in neg_files]
        
        df_pos = pd.DataFrame({'text': pos_texts, 'sentiment': 1})
        df_neg = pd.DataFrame({'text': neg_texts, 'sentiment': 0})
        df = pd.concat([df_pos, df_neg], ignore_index=True).sample(frac=1.0, random_state=42).reset_index(drop=True)
        
        df.to_csv(DATASET_CSV_PATH, index=False)
        print(f"[Dataset] Successfully loaded & cached NLTK movie reviews dataset ({len(df)} samples: 1000 POS / 1000 NEG) to {DATASET_CSV_PATH}")
        return df
    except Exception as e:
        print(f"[Dataset] NLTK loader warning: {e}. Downloading Stanford IMDb dataset...")

    tar_path = os.path.join(DATASET_DIR, "aclImdb_v1.tar.gz")
    req = urllib.request.Request(STANFORD_IMDB_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open(tar_path, 'wb') as out_file:
        out_file.write(response.read())

    pos_reviews = []
    neg_reviews = []
    with tarfile.open(tar_path, "r:gz") as tar:
        for member in tar.getmembers():
            if member.isfile() and member.name.endswith(".txt"):
                if "/pos/" in member.name:
                    f = tar.extractfile(member)
                    if f:
                        text = f.read().decode('utf-8', errors='ignore')
                        pos_reviews.append(text)
                elif "/neg/" in member.name:
                    f = tar.extractfile(member)
                    if f:
                        text = f.read().decode('utf-8', errors='ignore')
                        neg_reviews.append(text)

    half_limit = sample_limit // 2
    df_pos = pd.DataFrame({'text': pos_reviews[:half_limit], 'sentiment': 1})
    df_neg = pd.DataFrame({'text': neg_reviews[:half_limit], 'sentiment': 0})
    df = pd.concat([df_pos, df_neg], ignore_index=True).sample(frac=1.0, random_state=42).reset_index(drop=True)
    df.to_csv(DATASET_CSV_PATH, index=False)
    if os.path.exists(tar_path):
        os.remove(tar_path)
    return df

def get_train_test_split(test_size: float = 0.2, random_state: int = 42, sample_limit: int = 10000) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    """
    Returns stratified train/test split: (X_train, X_test, y_train, y_test).
    Guarantees strict separation of test data from training & hyperparameter tuning.
    """
    df = ensure_dataset_exists(sample_limit=sample_limit)
    X = df['text']
    y = df['sentiment']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    return X_train, X_test, y_train, y_test
