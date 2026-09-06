import os
import joblib
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

from app.sentiment.dataset import get_train_test_split
from app.sentiment.preprocessor import preprocessor

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_models")

def train_and_save_winning_model(sample_limit: int = 10000):
    """
    Trains the winning TF-IDF + Linear SVM model on dataset and saves joblib artifacts.
    """
    print("=" * 60)
    print("      TRAINING & SAVING SENTIMENT ML MODEL (TF-IDF + Linear SVM)")
    print("=" * 60)
    
    t0 = time.time()
    X_train_raw, X_test_raw, y_train, y_test = get_train_test_split(test_size=0.2, random_state=42, sample_limit=sample_limit)
    print(f"[Dataset] Train samples: {len(X_train_raw)}, Test samples: {len(X_test_raw)}")
    
    print("[Preprocessing] Preprocessing training data...")
    X_train_clean = [preprocessor.preprocess(t) for t in X_train_raw]
    
    print("[TF-IDF] Fitting TF-IDF Vectorizer...")
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=20000, sublinear_tf=True)
    X_train_vec = vectorizer.fit_transform(X_train_clean)
    
    print("[Linear SVM] Fitting LinearSVC model...")
    clf = LinearSVC(C=0.5, random_state=42, dual='auto')
    clf.fit(X_train_vec, y_train)
    
    os.makedirs(MODELS_DIR, exist_ok=True)
    vec_path = os.path.join(MODELS_DIR, "tfidf_vectorizer.joblib")
    clf_path = os.path.join(MODELS_DIR, "sentiment_classifier.joblib")
    
    joblib.dump(vectorizer, vec_path)
    joblib.dump(clf, clf_path)
    
    elapsed = time.time() - t0
    print(f"[Success] Saved Vectorizer to {vec_path}")
    print(f"[Success] Saved Classifier to {clf_path}")
    print(f"[Completed] Total training and persistence took {elapsed:.2f} seconds.")

if __name__ == "__main__":
    train_and_save_winning_model()
