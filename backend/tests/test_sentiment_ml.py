import pytest
import os
from app.sentiment.preprocessor import preprocessor
from app.sentiment.analyzer import SentimentService, sentiment_service

def test_preprocessor_text_cleaning():
    raw_text = "<b>Masterpiece!</b> Visit https://example.com for more info."
    cleaned = preprocessor.preprocess(raw_text)
    assert "<b>" not in cleaned
    assert "https" not in cleaned
    assert "masterpiece" in cleaned

def test_preprocessor_emoji_handling():
    raw_text = "This movie is 🔥, I almost 🤮"
    cleaned = preprocessor.preprocess(raw_text)
    assert "fire_emoji" in cleaned
    assert "vomit_emoji" in cleaned

def test_preprocessor_negation_handling():
    raw_text = "The movie was not good and never boring."
    cleaned = preprocessor.preprocess(raw_text)
    assert "not_good" in cleaned
    assert "never_boring" in cleaned

def test_sentiment_service_positive_prediction():
    text = "An absolute masterpiece of modern cinema! Brilliant acting and breathtaking visual effects."
    res = sentiment_service.analyze_text(text)
    assert "positive_score" in res
    assert "negative_score" in res
    assert "final_sentiment" in res
    assert "method" in res
    assert res["final_sentiment"] == "POSITIVE"
    assert res["positive_score"] > 0.5
    assert res["method"] == "tfidf_linear_svm"

def test_sentiment_service_negative_prediction():
    text = "A complete waste of time and money. Terrible plot, horrible acting, and incredibly boring."
    res = sentiment_service.analyze_text(text)
    assert res["final_sentiment"] == "NEGATIVE"
    assert res["negative_score"] > 0.5
    assert res["method"] == "tfidf_linear_svm"

def test_sentiment_service_empty_input():
    res = sentiment_service.analyze_text("   ")
    assert res["final_sentiment"] == "NEUTRAL"
    assert res["positive_score"] == 0.5
    assert res["method"] == "empty_input"

def test_sentiment_rating_conversion():
    pos_res = {"final_sentiment": "POSITIVE", "positive_score": 0.9}
    neg_res = {"final_sentiment": "NEGATIVE", "negative_score": 0.9}
    neu_res = {"final_sentiment": "NEUTRAL", "positive_score": 0.5}

    assert 8.0 <= sentiment_service.convert_sentiment_to_rating(pos_res) <= 10.0
    assert 1.0 <= sentiment_service.convert_sentiment_to_rating(neg_res) <= 3.0
    assert sentiment_service.convert_sentiment_to_rating(neu_res) == 5.0

def test_fallback_when_model_missing(monkeypatch):
    dummy_service = SentimentService()
    dummy_service.vec_path = "non_existent_vec.joblib"
    dummy_service.clf_path = "non_existent_clf.joblib"
    
    res = dummy_service.analyze_text("This was a great movie")
    assert res["method"] == "local_lexicon_fallback"
    assert res["final_sentiment"] == "POSITIVE"
