from app.services.scoring import calculate_normalized_weights

def test_scoring_all_sources_available():
    # Base weights (YouTube prioritized): YouTube = 40%, IMDb = 25%, NLP = 15%, TMDb = 10%, Metacritic = 10%
    # IMDb = 8.0, TMDb = 7.0, Metacritic = 6.0, NLP = 9.0, YouTube = 8.0
    # Expected weighted score: 0.25*8 + 0.10*7 + 0.10*6 + 0.15*9 + 0.40*8 = 2.0 + 0.7 + 0.6 + 1.35 + 3.2 = 7.85
    score, effective_weights, available, missing = calculate_normalized_weights(8.0, 7.0, 6.0, 9.0, 8.0)
    
    assert score == 7.85
    assert effective_weights["imdb"] == 0.25
    assert effective_weights["tmdb"] == 0.10
    assert effective_weights["metacritic"] == 0.10
    assert effective_weights["nlp"] == 0.15
    assert effective_weights["youtube"] == 0.40
    assert "imdb" in available
    assert "tmdb" in available
    assert "metacritic" in available
    assert "nlp" in available
    assert "youtube" in available
    assert len(missing) == 0

def test_scoring_youtube_missing():
    # YouTube is missing. Total available weight sum = 0.25 + 0.10 + 0.10 + 0.15 = 0.60
    # IMDb = 0.25 / 0.60 = 0.4167
    # TMDb = 0.10 / 0.60 = 0.1667
    # Metacritic = 0.10 / 0.60 = 0.1667
    # NLP = 0.15 / 0.60 = 0.2500
    score, effective_weights, available, missing = calculate_normalized_weights(8.0, 7.0, 6.0, 9.0, None)
    
    assert abs(effective_weights["imdb"] - 0.4167) < 0.0001
    assert abs(effective_weights["tmdb"] - 0.1667) < 0.0001
    assert abs(effective_weights["metacritic"] - 0.1667) < 0.0001
    assert abs(effective_weights["nlp"] - 0.2500) < 0.0001
    assert effective_weights["youtube"] == 0.0
    assert "youtube" in missing

def test_scoring_multiple_missing():
    # IMDb and Metacritic and YouTube unavailable. Total available weight sum = 0.10 + 0.15 = 0.25
    # TMDb = 0.10 / 0.25 = 0.4000
    # NLP = 0.15 / 0.25 = 0.6000
    score, effective_weights, available, missing = calculate_normalized_weights("N/A", 8.0, "NULL", 7.0, None)
    
    assert effective_weights["imdb"] == 0.0
    assert effective_weights["metacritic"] == 0.0
    assert effective_weights["youtube"] == 0.0
    assert effective_weights["tmdb"] == 0.40
    assert effective_weights["nlp"] == 0.60
    assert "imdb" in missing
    assert "metacritic" in missing
    assert "youtube" in missing
    assert "tmdb" in available
    assert "nlp" in available
    
    # Expected weighted score: 0.40 * 8 + 0.60 * 7 = 3.2 + 4.2 = 7.40
    assert score == 7.40


def test_scoring_no_sources_available():
    # All sources are None or N/A
    score, effective_weights, available, missing = calculate_normalized_weights("N/A", "N/A", "N/A", None, "N/A")
    
    assert score == 0.0
    assert all(w == 0.0 for w in effective_weights.values())
    assert len(available) == 0
    assert len(missing) == 5

def test_scoring_type_parsing_robustness():
    # Verifies float conversion handles weird formats
    score, effective_weights, available, missing = calculate_normalized_weights(" 8.5 ", 7.2, "60", "  ", None)
    assert "imdb" in available
    assert "tmdb" in available
    assert "metacritic" in available
    assert "nlp" in missing
    assert "youtube" in missing
