from fastapi.testclient import TestClient

def test_debug_movie_endpoint(client: TestClient):
    response = client.get("/debug/movie/27205")
    assert response.status_code == 200
    data = response.json()
    assert data["tmdb_id"] == 27205
    assert data["title"] == "Inception"
    assert data["media_type"] == "Movie"
    assert "quality_check" in data
    assert "missing_fields" in data
    
    qc = data["quality_check"]
    assert "tmdb_score_exists" in qc
    assert "imdb_id_exists" in qc
    assert "omdb_lookup_succeeded" in qc
    assert "metacritic_score_exists" in qc
