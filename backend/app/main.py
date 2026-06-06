from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.config import settings
from app.database import Base, engine
from app.auth import router as auth_router
from app.sentiment import router as sentiment_router
from app.routers import movies, reviews, recommendations, rest

from sqlalchemy import inspect, text

# Automatically create database tables if they do not exist
try:
    Base.metadata.create_all(bind=engine)
    
    # Automatic SQLite schema column migrations check
    inspector = inspect(engine)
    movie_cols = [c["name"] for c in inspector.get_columns("movies")]
    if "imdb_id" not in movie_cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE movies ADD COLUMN imdb_id VARCHAR"))
        print("[Database Migration] Column 'imdb_id' successfully added to 'movies' table.")
        
    if "runtime" not in movie_cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE movies ADD COLUMN runtime INTEGER"))
        print("[Database Migration] Column 'runtime' successfully added to 'movies' table.")

    if "is_details_loaded" not in movie_cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE movies ADD COLUMN is_details_loaded BOOLEAN DEFAULT 0 NOT NULL"))
        print("[Database Migration] Column 'is_details_loaded' successfully added to 'movies' table.")

    if "omdb_status" not in movie_cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE movies ADD COLUMN omdb_status VARCHAR"))
        print("[Database Migration] Column 'omdb_status' successfully added to 'movies' table.")

    if "omdb_error" not in movie_cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE movies ADD COLUMN omdb_error VARCHAR"))
        print("[Database Migration] Column 'omdb_error' successfully added to 'movies' table.")

    if "media_type" not in movie_cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE movies ADD COLUMN media_type VARCHAR"))
        print("[Database Migration] Column 'media_type' successfully added to 'movies' table.")

    if "rating_source" not in movie_cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE movies ADD COLUMN rating_source VARCHAR"))
        print("[Database Migration] Column 'rating_source' successfully added to 'movies' table.")
        
    review_cols = [c["name"] for c in inspector.get_columns("reviews")]
    if "aspect_scores" not in review_cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE reviews ADD COLUMN aspect_scores JSON"))
        print("[Database Migration] Column 'aspect_scores' successfully added to 'reviews' table.")
except Exception as e:
    print(f"WARNING: Could not automatically initialize database tables or run migrations: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A modern AI-powered movie rating, review sentiment analysis, scraper, and recommendation platform.",
    version="1.0.0"
)

# Set CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Performance Middleware: Log request execution time
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected system error occurred: {str(exc)}"}
    )

# Register Standard Root-Level REST API (e.g. /movies, /movie/{id}, /reviews/{movie})
app.include_router(rest.router)

# Register API Routers under standard /api prefix
app.include_router(auth_router, prefix="/api")
app.include_router(movies.router, prefix="/api")
app.include_router(reviews.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(sentiment_router, prefix="/api")

@app.get("/")
def read_root():
    """
    Root API health check and informational entry point.
    """
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }
