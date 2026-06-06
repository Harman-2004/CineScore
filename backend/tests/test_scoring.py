from app.services.scoring import calculate_normalized_weights

def test_scoring_all_sources_available():
    # FinalScore = 0.40(IMDb) + 0.20(TMDb) + 0.10(Metacritic) + 0.30(NLP)
    # IMDb = 8.0, TMDb = 7.0, Metacritic = 6.0, NLP = 9.0
    # Expected: 0.4*8 + 0.2*7 + 0.1*6 + 0.3*9 = 3.2 + 1.4 + 0.6 + 2.7 = 7.9
    score, effective_weights, available, missing = calculate_normalized_weights(8.0, 7.0, 6.0, 9.0)
    
    assert score == 7.9
    assert effective_weights["imdb"] == 0.40
    assert effective_weights["tmdb"] == 0.20
    assert effective_weights["metacritic"] == 0.10
    assert effective_weights["nlp"] == 0.30
    assert "imdb" in available
    assert "tmdb" in available
    assert "metacritic" in available
    assert "nlp" in available
    assert len(missing) == 0

def test_scoring_imdb_missing():
    # IMDb is unavailable. Total available weight sum = 0.20 + 0.10 + 0.30 = 0.60
    # TMDb = 0.20 / 0.60 = 0.3333
    # Metacritic = 0.10 / 0.60 = 0.1667
    # NLP = 0.30 / 0.60 = 0.5000
    score, effective_weights, available, missing = calculate_normalized_weights(None, 7.0, 6.0, 9.0)
    
    assert effective_weights["imdb"] == 0.0
    assert abs(effective_weights["tmdb"] - 0.3333) < 0.0001
    assert abs(effective_weights["metacritic"] - 0.1667) < 0.0001
    assert effective_weights["nlp"] == 0.50
    assert "imdb" in missing
    assert "tmdb" in available
    assert "metacritic" in available
    assert "nlp" in available

def test_scoring_multiple_missing():
    # IMDb and Metacritic unavailable. Total available weight sum = 0.20 + 0.30 = 0.50
    # TMDb = 0.20 / 0.50 = 0.40
    # NLP = 0.30 / 0.50 = 0.60
    score, effective_weights, available, missing = calculate_normalized_weights("N/A", 8.0, "NULL", 7.0)
    
    assert effective_weights["imdb"] == 0.0
    assert effective_weights["metacritic"] == 0.0
    assert effective_weights["tmdb"] == 0.40
    assert effective_weights["nlp"] == 0.60
    assert "imdb" in missing
    assert "metacritic" in missing
    assert "tmdb" in available
    assert "nlp" in available
    
    # Expected weighted score: 0.4 * 8 + 0.6 * 7 = 3.2 + 4.2 = 7.4
    assert score == 7.4

def test_scoring_no_sources_available():
    # All sources are None or N/A
    score, effective_weights, available, missing = calculate_normalized_weights("N/A", "N/A", "N/A", None)
    
    assert score == 0.0
    assert all(w == 0.0 for w in effective_weights.values())
    assert len(available) == 0
    assert len(missing) == 4

def test_scoring_type_parsing_robustness():
    # Verifies float conversion handles weird formats
    score, effective_weights, available, missing = calculate_normalized_weights(" 8.5 ", 7.2, "60", "  ")
    # nlp is invalid float, so missing. Available: imdb (8.5), tmdb (7.2), metacritic (6.0) -> metacritic converted from 60 to 6.0? Wait, metacritic score is normally 0-100, but calculate_normalized_weights just parses whatever is passed. If 60.0 is parsed as 60.0... let's see.
    # Wait, safe_float parses "60" to 60.0. Let's verify.
    assert "imdb" in available
    assert "tmdb" in available
    assert "metacritic" in available
    assert "nlp" in missing
