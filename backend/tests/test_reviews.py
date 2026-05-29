from fastapi.testclient import TestClient

def test_create_review(client: TestClient, test_user_token: dict):
    # Pre-populate movie detail in cache by visiting detail route
    client.get("/api/movies/27205")
    
    # Post a positive review
    review_data = {
        "movie_id": 27205,
        "rating": 9.5,
        "review_text": "This movie is absolutely wonderful, stunning, and beautiful! A true masterpiece."
    }
    response = client.post("/api/reviews", json=review_data, headers=test_user_token)
    assert response.status_code == 201
    data = response.json()
    assert data["movie_id"] == 27205
    assert data["rating"] == 9.5
    assert data["sentiment_label"] == "POSITIVE"
    assert data["sentiment_score"] > 0.15

def test_create_duplicate_review(client: TestClient, test_user_token: dict):
    client.get("/api/movies/27205")
    
    review_data = {
        "movie_id": 27205,
        "rating": 8.0,
        "review_text": "Pretty good sci-fi movie. Recommended."
    }
    # Create first
    client.post("/api/reviews", json=review_data, headers=test_user_token)
    # Attempt duplicate
    response = client.post("/api/reviews", json=review_data, headers=test_user_token)
    assert response.status_code == 400
    assert "already submitted a review" in response.json()["detail"]

def test_get_movie_reviews(client: TestClient, test_user_token: dict):
    client.get("/api/movies/27205")
    client.post("/api/reviews", json={
        "movie_id": 27205,
        "rating": 8.0,
        "review_text": "Loved the dream within a dream concept. Awesome script."
    }, headers=test_user_token)
    
    response = client.get("/api/reviews/movie/27205")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["user"]["username"] == "testuser"
    assert data[0]["rating"] == 8.0

def test_update_review(client: TestClient, test_user_token: dict):
    client.get("/api/movies/27205")
    post_res = client.post("/api/reviews", json={
        "movie_id": 27205,
        "rating": 8.0,
        "review_text": "Great concept, loved the action."
    }, headers=test_user_token)
    review_id = post_res.json()["id"]
    
    # Update to a negative review
    update_res = client.put(f"/api/reviews/{review_id}", json={
        "rating": 3.0,
        "review_text": "Hated the pacing, terribly boring and stupid movie."
    }, headers=test_user_token)
    
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["rating"] == 3.0
    assert updated_data["sentiment_label"] == "NEGATIVE"
    assert updated_data["sentiment_score"] < -0.15

def test_delete_review(client: TestClient, test_user_token: dict):
    client.get("/api/movies/27205")
    post_res = client.post("/api/reviews", json={
        "movie_id": 27205,
        "rating": 8.0,
        "review_text": "Stunning movie. Highly recommended."
    }, headers=test_user_token)
    review_id = post_res.json()["id"]
    
    # Delete
    del_res = client.delete(f"/api/reviews/{review_id}", headers=test_user_token)
    assert del_res.status_code == 204
    
    # Verify deleted
    get_res = client.get("/api/reviews/movie/27205")
    assert len(get_res.json()) == 0
