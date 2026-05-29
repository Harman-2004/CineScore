from fastapi.testclient import TestClient

def test_cold_start_recommendations(client: TestClient, test_user_token: dict):
    # No reviews have been written yet, should fall back to general popular movies (cold start)
    response = client.get("/api/recommendations", headers=test_user_token)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    # Recommendation score should equal the neutral fallback score (0.5)
    assert data[0]["recommendation_score"] == 0.5

def test_personalized_recommendations(client: TestClient, test_user_token: dict):
    # 1. Fetch movie details to populate MovieCache in database
    # Inception (Action, Sci-Fi, Adventure)
    client.get("/api/movies/27205")
    # Interstellar (Adventure, Drama, Sci-Fi)
    client.get("/api/movies/157336")
    # The Dark Knight (Drama, Action, Crime, Thriller)
    client.get("/api/movies/155")
    
    # 2. Write a highly-rated review for Inception (User likes Action and Sci-Fi)
    client.post("/api/reviews", json={
        "movie_id": 27205,
        "rating": 10.0,
        "review_text": "I absolutely love this masterpiece. Masterful action and sci-fi narrative."
    }, headers=test_user_token)
    
    # 3. Request recommendations
    response = client.get("/api/recommendations?limit=5", headers=test_user_token)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    
    # The list should not contain Inception (since the user already reviewed it)
    for m in data:
        assert m["id"] != 27205
        
    # The top recommendation should ideally have a positive recommendation score (> 0.5)
    # due to overlap with Action/Sci-Fi/Adventure from Inception (e.g., Interstellar shares Sci-Fi/Adventure)
    assert data[0]["recommendation_score"] > 0.5
