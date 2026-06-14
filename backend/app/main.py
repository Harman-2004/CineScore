from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.config import settings
from app.database import Base, engine
from app.auth import router as auth_router
from app.sentiment import router as sentiment_router
from app.routers import movies, reviews, recommendations, rest

# Automatically create database tables if they do not exist
try:
    from app.models.recommendation import MovieEmbedding, RecommendationCache, UserPreference, UserInteraction
    Base.metadata.create_all(bind=engine)
    
    # Auto-migration check for existing tables (SQLite support)
    try:
        import sqlite3
        conn = sqlite3.connect('movies.db')
        cursor = conn.cursor()
        
        # Check ratings columns
        cursor.execute("PRAGMA table_info(ratings)")
        cols = [col[1] for col in cursor.fetchall()]
        if 'youtube_score' not in cols:
            cursor.execute("ALTER TABLE ratings ADD COLUMN youtube_score FLOAT;")
            print("[Startup Migration] Added youtube_score column to ratings table.")
            
        # Check reviews columns
        cursor.execute("PRAGMA table_info(reviews)")
        cols_rev = [col[1] for col in cursor.fetchall()]
        if 'source' not in cols_rev:
            cursor.execute("ALTER TABLE reviews ADD COLUMN source VARCHAR(50) DEFAULT 'Web';")
            print("[Startup Migration] Added source column to reviews table.")
            
        # Check movies columns
        cursor.execute("PRAGMA table_info(movies)")
        cols_mov = [col[1] for col in cursor.fetchall()]
        if 'trailer_transcript' not in cols_mov:
            cursor.execute("ALTER TABLE movies ADD COLUMN trailer_transcript TEXT;")
            print("[Startup Migration] Added trailer_transcript column to movies table.")
        if 'keywords' not in cols_mov:
            cursor.execute("ALTER TABLE movies ADD COLUMN keywords JSON;")
            print("[Startup Migration] Added keywords column to movies table.")
        if 'cast' not in cols_mov:
            cursor.execute("ALTER TABLE movies ADD COLUMN cast JSON;")
            print("[Startup Migration] Added cast column to movies table.")
        if 'director' not in cols_mov:
            cursor.execute("ALTER TABLE movies ADD COLUMN director VARCHAR(255);")
            print("[Startup Migration] Added director column to movies table.")
        if 'themes' not in cols_mov:
            cursor.execute("ALTER TABLE movies ADD COLUMN themes JSON;")
            print("[Startup Migration] Added themes column to movies table.")
            
        # Ensure default viewer user exists
        cursor.execute("SELECT count(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO users (id, email, username, hashed_password, is_active) VALUES (1, 'viewer@cinescore.ai', 'cinescore_viewer', 'mock_password', 1)")
            print("[Startup Migration] Created default viewer user (ID=1).")
            
        conn.commit()
        conn.close()

    except Exception as migration_error:
        print(f"[Startup Migration] WARNING: SQLite migration check failed: {migration_error}")


except Exception as e:
    print(f"WARNING: Could not automatically initialize database tables: {e}")

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
