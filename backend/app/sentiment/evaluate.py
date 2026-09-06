# evaluate.py
# Benchmark Evaluation Suite comparing TextBlob, TF-IDF + Logistic Regression,
# TF-IDF + Linear SVM, and Word2Vec + Random Forest on the benchmark IMDb test set.

import os
import time
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from gensim.models import Word2Vec

from app.sentiment.dataset import get_train_test_split
from app.sentiment.preprocessor import preprocessor
from textblob import TextBlob

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_models")

class DocumentVectorVectorizer:
    """Helper to convert tokenized documents into fixed-size Mean Word2Vec vectors."""
    def __init__(self, w2v_model, vector_size: int = 100):
        self.w2v_model = w2v_model
        self.vector_size = vector_size

    def transform_tokens(self, token_list: List[List[str]]) -> np.ndarray:
        vectors = []
        for tokens in token_list:
            valid_words = [w for w in tokens if w in self.w2v_model.wv]
            if valid_words:
                vec = np.mean(self.w2v_model.wv[valid_words], axis=0)
            else:
                vec = np.zeros(self.vector_size)
            vectors.append(vec)
        return np.array(vectors)

def evaluate_model_performance(name: str, y_true: np.ndarray, y_pred: np.ndarray, train_time: float, predict_time: float) -> Dict[str, Any]:
    """Calculates standard classification metrics: Accuracy, Precision, Recall, F1, Confusion Matrix."""
    acc = accuracy_score(y_true, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary')
    cm = confusion_matrix(y_true, y_pred)
    
    return {
        "model": name,
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1": round(float(f1), 4),
        "confusion_matrix": cm.tolist(),
        "train_time_sec": round(float(train_time), 4),
        "predict_time_sec": round(float(predict_time), 4)
    }

def run_textblob_baseline(X_raw_test: pd.Series, y_test: pd.Series) -> Dict[str, Any]:
    """Evaluates existing TextBlob sentiment engine against ground-truth test labels."""
    print("\n--- Evaluating TextBlob Baseline ---")
    t0 = time.time()
    preds = []
    for text in X_raw_test:
        blob = TextBlob(text)
        pol = blob.sentiment.polarity
        preds.append(1 if pol > 0.0 else 0)
    predict_time = time.time() - t0
    
    return evaluate_model_performance("TextBlob Baseline", y_test.values, np.array(preds), train_time=0.0, predict_time=predict_time)

def run_tfidf_logistic_regression(X_train_clean: List[str], y_train: pd.Series, X_test_clean: List[str], y_test: pd.Series) -> Tuple[Dict[str, Any], Any, Any]:
    """Phase 4: TF-IDF + Logistic Regression."""
    print("\n--- Training Model 1: TF-IDF + Logistic Regression ---")
    t0 = time.time()
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=20000, sublinear_tf=True)
    X_train_vec = vectorizer.fit_transform(X_train_clean)
    
    clf = LogisticRegression(C=2.0, max_iter=1000, random_state=42)
    clf.fit(X_train_vec, y_train)
    train_time = time.time() - t0
    
    t0 = time.time()
    X_test_vec = vectorizer.transform(X_test_clean)
    y_pred = clf.predict(X_test_vec)
    predict_time = time.time() - t0
    
    metrics = evaluate_model_performance("TF-IDF + Logistic Regression", y_test.values, y_pred, train_time, predict_time)
    return metrics, vectorizer, clf

def run_tfidf_linear_svm(X_train_clean: List[str], y_train: pd.Series, X_test_clean: List[str], y_test: pd.Series) -> Tuple[Dict[str, Any], Any, Any]:
    """Phase 5: TF-IDF + Linear SVM."""
    print("\n--- Training Model 2: TF-IDF + Linear SVM ---")
    t0 = time.time()
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=20000, sublinear_tf=True)
    X_train_vec = vectorizer.fit_transform(X_train_clean)
    
    clf = LinearSVC(C=0.5, random_state=42, dual='auto')
    clf.fit(X_train_vec, y_train)
    train_time = time.time() - t0
    
    t0 = time.time()
    X_test_vec = vectorizer.transform(X_test_clean)
    y_pred = clf.predict(X_test_vec)
    predict_time = time.time() - t0
    
    metrics = evaluate_model_performance("TF-IDF + Linear SVM", y_test.values, y_pred, train_time, predict_time)
    return metrics, vectorizer, clf

def run_word2vec_random_forest(X_train_tokens: List[List[str]], y_train: pd.Series, X_test_tokens: List[List[str]], y_test: pd.Series) -> Tuple[Dict[str, Any], Any, Any]:
    """Phase 6: Word2Vec + Random Forest."""
    print("\n--- Training Model 3: Word2Vec + Random Forest ---")
    t0 = time.time()
    w2v = Word2Vec(sentences=X_train_tokens, vector_size=100, window=5, min_count=2, workers=4, seed=42)
    
    vec_encoder = DocumentVectorVectorizer(w2v, vector_size=100)
    X_train_vec = vec_encoder.transform_tokens(X_train_tokens)
    
    clf = RandomForestClassifier(n_estimators=200, max_depth=20, min_samples_split=5, random_state=42, n_jobs=-1)
    clf.fit(X_train_vec, y_train)
    train_time = time.time() - t0
    
    t0 = time.time()
    X_test_vec = vec_encoder.transform_tokens(X_test_tokens)
    y_pred = clf.predict(X_test_vec)
    predict_time = time.time() - t0
    
    metrics = evaluate_model_performance("Word2Vec + Random Forest", y_test.values, y_pred, train_time, predict_time)
    return metrics, w2v, clf

def perform_error_analysis(X_raw_test: List[str], y_test: List[int], y_pred: List[int]) -> List[Dict[str, Any]]:
    """Phase 8: Error Analysis on Misclassified Test Samples."""
    misclassified = []
    for raw_text, true_lbl, pred_lbl in zip(X_raw_test, y_test, y_pred):
        if true_lbl != pred_lbl:
            # Check for linguistic phenomena
            text_lower = raw_text.lower()
            reasons = []
            if "not " in text_lower or "no " in text_lower or "n't" in text_lower:
                reasons.append("Negation")
            if "could have been" in text_lower or "should have" in text_lower or "but" in text_lower:
                reasons.append("Mixed Sentiment / Expectation")
            if len(raw_text.split()) < 10:
                reasons.append("Short Review")
            elif len(raw_text.split()) > 150:
                reasons.append("Long Detailed Review")
            if not reasons:
                reasons.append("Subtle Sarcasm / Complex Terminology")

            misclassified.append({
                "raw_text": raw_text[:200] + ("..." if len(raw_text) > 200 else ""),
                "true_label": "POSITIVE" if true_lbl == 1 else "NEGATIVE",
                "predicted_label": "POSITIVE" if pred_lbl == 1 else "NEGATIVE",
                "categories": reasons
            })
            if len(misclassified) >= 10:
                break
    return misclassified

def run_full_evaluation(sample_limit: int = 10000) -> Dict[str, Any]:
    """Executes full evaluation suite across all 4 models and returns metrics table."""
    print("=" * 60)
    print("      CINESCORE SENTIMENT MODEL BENCHMARK EVALUATION")
    print("=" * 60)
    
    X_train_raw, X_test_raw, y_train, y_test = get_train_test_split(test_size=0.2, random_state=42, sample_limit=sample_limit)
    
    print(f"[Preprocessing] Cleaning {len(X_train_raw)} train and {len(X_test_raw)} test reviews...")
    t0 = time.time()
    X_train_clean = [preprocessor.preprocess(t) for t in X_train_raw]
    X_test_clean = [preprocessor.preprocess(t) for t in X_test_raw]
    
    X_train_tokens = [t.split() for t in X_train_clean]
    X_test_tokens = [t.split() for t in X_test_clean]
    print(f"[Preprocessing] Completed in {time.time() - t0:.2f} seconds.")

    # 1. Baseline TextBlob
    m0_metrics = run_textblob_baseline(X_test_raw, y_test)
    
    # 2. Model 1: TF-IDF + Logistic Regression
    m1_metrics, tfidf_lr_vec, lr_clf = run_tfidf_logistic_regression(X_train_clean, y_train, X_test_clean, y_test)
    
    # 3. Model 2: TF-IDF + Linear SVM
    m2_metrics, tfidf_svm_vec, svm_clf = run_tfidf_linear_svm(X_train_clean, y_train, X_test_clean, y_test)
    
    # 4. Model 3: Word2Vec + Random Forest
    m3_metrics, w2v_model, rf_clf = run_word2vec_random_forest(X_train_tokens, y_train, X_test_tokens, y_test)

    results = [m0_metrics, m1_metrics, m2_metrics, m3_metrics]
    
    # Print Comparison Table
    print("\n" + "=" * 80)
    print(f"{'Model':<30} | {'Accuracy':<8} | {'Precision':<9} | {'Recall':<7} | {'F1':<6} | {'Train (s)':<9} | {'Predict (s)':<11}")
    print("-" * 80)
    for r in results:
        print(f"{r['model']:<30} | {r['accuracy']:<8.4f} | {r['precision']:<9.4f} | {r['recall']:<7.4f} | {r['f1']:<6.4f} | {r['train_time_sec']:<9.4f} | {r['predict_time_sec']:<11.4f}")
    print("=" * 80)

    # Winner Selection based primarily on F1-score and Accuracy
    supervised_models = [m1_metrics, m2_metrics, m3_metrics]
    winner = max(supervised_models, key=lambda x: (x['f1'], x['accuracy']))
    print(f"\n[WINNER]: {winner['model']} (F1: {winner['f1']}, Accuracy: {winner['accuracy']})")

    # Persist Winning Model Artifacts
    os.makedirs(MODELS_DIR, exist_ok=True)
    if winner['model'] == "TF-IDF + Logistic Regression":
        joblib.dump(tfidf_lr_vec, os.path.join(MODELS_DIR, "tfidf_vectorizer.joblib"))
        joblib.dump(lr_clf, os.path.join(MODELS_DIR, "sentiment_classifier.joblib"))
        win_vec, win_clf = tfidf_lr_vec, lr_clf
    elif winner['model'] == "TF-IDF + Linear SVM":
        joblib.dump(tfidf_svm_vec, os.path.join(MODELS_DIR, "tfidf_vectorizer.joblib"))
        joblib.dump(svm_clf, os.path.join(MODELS_DIR, "sentiment_classifier.joblib"))
        win_vec, win_clf = tfidf_svm_vec, svm_clf
    else:
        w2v_model.save(os.path.join(MODELS_DIR, "word2vec.model"))
        joblib.dump(rf_clf, os.path.join(MODELS_DIR, "sentiment_classifier.joblib"))
        win_vec, win_clf = w2v_model, rf_clf

    # Error Analysis for Winning Model
    X_test_clean_vec = win_vec.transform(X_test_clean) if hasattr(win_vec, 'transform') else None
    if X_test_clean_vec is not None:
        y_winning_pred = win_clf.predict(X_test_clean_vec)
    else:
        doc_encoder = DocumentVectorVectorizer(win_vec, vector_size=100)
        X_test_w2v = doc_encoder.transform_tokens(X_test_tokens)
        y_winning_pred = win_clf.predict(X_test_w2v)

    error_analysis = perform_error_analysis(list(X_test_raw), list(y_test), list(y_winning_pred))

    return {
        "comparison": results,
        "winner": winner['model'],
        "winning_metrics": winner,
        "error_analysis": error_analysis
    }

if __name__ == '__main__':
    run_full_evaluation()
