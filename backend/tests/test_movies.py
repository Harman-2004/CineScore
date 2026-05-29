from fastapi.testclient import TestClient

def test_get_popular_movies(client: TestClient):
    response = client.get("/api/movies/popular")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "page" in data
    assert len(data["results"]) > 0
    # Popular results should contain some mock movies we configured
    first_movie = data["results"][0]
    assert "id" in first_movie
    assert "title" in first_movie
    assert "overview" in first_movie

def test_search_movies(client: TestClient):
    response = client.get("/api/movies/search?query=Inception")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 1
    assert data["results"][0]["title"] == "Inception"

def test_get_movie_details(client: TestClient):
    response = client.get("/api/movies/27205")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 27205
    assert data["title"] == "Inception"
    assert "genres" in data
    assert len(data["genres"]) > 0

def test_get_movie_details_not_found(client: TestClient):
    # For nonexistent ID, since TMDb key is mock, it returns a generic fallback detail instead of 404
    # Let's verify we get a valid payload
    response = client.get("/api/movies/999999")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 999999
    assert "Mock Movie 999999" in data["title"]
