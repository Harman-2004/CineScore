import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine
from app.auth import router as auth_router
from app.sentiment import router as sentiment_router
from app.routers import movies, reviews, recommendations, rest

# Import models to register them with Base.metadata
from app.models.movie import Movie
from app.models.rating import Rating
from app.models.review import Review
from app.models.user import User
from app.models.recommendation import MovieEmbedding, RecommendationCache, UserPreference, UserInteraction

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("cinescore.main")

def run_database_migrations_and_validation(engine):
    """
    Performs startup environment validations, checks the database connection,
    creates any missing tables, and runs database-agnostic schema checks.
    """
    # 1. Environment Variable Validation
    logger.info("Validating system configuration and environment variables...")
    is_production = settings.ENVIRONMENT.lower() == "production"
    
    # Check DATABASE_URL
    if not settings.DATABASE_URL:
        err_msg = "DATABASE_URL must be configured!"
        logger.error(err_msg)
        raise ValueError(err_msg)
        
    if is_production and settings.DATABASE_URL.startswith("sqlite"):
        err_msg = "DATABASE_URL is set to default SQLite in production environment. A production database (e.g. Neon PostgreSQL) is required."
        logger.error(err_msg)
        raise ValueError(err_msg)

    # Check SECRET_KEY
    if is_production and settings.SECRET_KEY == "9a8b7c6d5e4f3g2h1i0j9k8l7m6n5o4p3q2r1s0t":
        err_msg = "SECRET_KEY must be changed from the default mock value in production!"
        logger.error(err_msg)
        raise ValueError(err_msg)

    # Warn if optional third-party integrations keys are missing
    missing_api_keys = []
    if not settings.TMDB_API_KEY:
        missing_api_keys.append("TMDB_API_KEY")
    if not settings.OMDB_API_KEY:
        missing_api_keys.append("OMDB_API_KEY")
    if not settings.YOUTUBE_API_KEY:
        missing_api_keys.append("YOUTUBE_API_KEY")
        
    if missing_api_keys:
        logger.warning(
            f"Optional API keys are missing: {', '.join(missing_api_keys)}. "
            "CineScore will fallback to realistic mock data where needed."
        )
    else:
        logger.info("All third-party integration API keys are configured.")

    # 2. Verify Database Connection
    logger.info("Verifying connection to the database...")
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("Database connection test succeeded.")
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        raise e

    # 3. Create Tables
    logger.info("Ensuring database tables are created...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Base database tables verified/created successfully.")
    except Exception as e:
        logger.error(f"Failed to create/verify base database tables: {e}")
        raise e

    # 4. Perform database-agnostic column migrations
    logger.info("Inspecting tables for missing columns and schema updates...")
    try:
        inspector = inspect(engine)
        
        # Check ratings columns
        if inspector.has_table("ratings"):
            cols = [col["name"] for col in inspector.get_columns("ratings")]
            if "youtube_score" not in cols:
                with engine.begin() as conn:
                    conn.execute(text("ALTER TABLE ratings ADD COLUMN youtube_score FLOAT;"))
                logger.info("[Migration] Successfully added youtube_score column to ratings table.")
                
        # Check reviews columns
        if inspector.has_table("reviews"):
            cols = [col["name"] for col in inspector.get_columns("reviews")]
            if "source" not in cols:
                with engine.begin() as conn:
                    conn.execute(text("ALTER TABLE reviews ADD COLUMN source VARCHAR(50) DEFAULT 'Web';"))
                logger.info("[Migration] Successfully added source column to reviews table.")
                
        # Check movies columns
        if inspector.has_table("movies"):
            cols = [col["name"] for col in inspector.get_columns("movies")]
            with engine.begin() as conn:
                if "trailer_transcript" not in cols:
                    conn.execute(text("ALTER TABLE movies ADD COLUMN trailer_transcript TEXT;"))
                    logger.info("[Migration] Successfully added trailer_transcript column to movies table.")
                if "keywords" not in cols:
                    conn.execute(text("ALTER TABLE movies ADD COLUMN keywords JSON;"))
                    logger.info("[Migration] Successfully added keywords column to movies table.")
                if "cast" not in cols:
                    conn.execute(text("ALTER TABLE movies ADD COLUMN cast JSON;"))
                    logger.info("[Migration] Successfully added cast column to movies table.")
                if "director" not in cols:
                    conn.execute(text("ALTER TABLE movies ADD COLUMN director VARCHAR(255);"))
                    logger.info("[Migration] Successfully added director column to movies table.")
                if "themes" not in cols:
                    conn.execute(text("ALTER TABLE movies ADD COLUMN themes JSON;"))
                    logger.info("[Migration] Successfully added themes column to movies table.")
                    
        # 5. Check/Create default viewer user
        logger.info("Ensuring default user seeded in database...")
        with Session(engine) as session:
            user = session.query(User).filter(User.id == 1).first()
            if not user:
                if session.query(User).count() == 0:
                    default_viewer = User(
                        id=1,
                        email="viewer@cinescore.ai",
                        username="cinescore_viewer",
                        hashed_password="mock_password",
                        is_active=True
                    )
                    session.add(default_viewer)
                    session.commit()
                    logger.info("[Migration] Successfully created default viewer user (ID=1).")
    except Exception as migration_error:
        logger.error(f"Database migration/seeding check failed: {migration_error}")
        raise migration_error

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan manager handles startup migrations, validations,
    and shutdown cleanup.
    """
    logger.info("Initializing CineScore API Lifecycle...")
    try:
        run_database_migrations_and_validation(engine)
        logger.info("CineScore startup migrations and validations completed successfully.")
    except Exception as e:
        logger.critical(f"FATAL: CineScore failed to start due to validation error: {e}")
        # Crash server on startup if settings are invalid in production
        if settings.ENVIRONMENT.lower() == "production":
            import sys
            sys.exit(1)
    yield
    logger.info("Shutting down CineScore API Lifecycle...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A modern AI-powered movie rating, review sentiment analysis, scraper, and recommendation platform.",
    version="1.0.0",
    lifespan=lifespan
)

# Set CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    allow_origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
    allow_credentials = True
    if "*" in allow_origins:
        allow_credentials = False

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
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
    logger.error(f"Global Exception Caught: {str(exc)}", exc_info=True)
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
