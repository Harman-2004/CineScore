from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings
import logging

logger = logging.getLogger("cinescore.database")

db_url = settings.DATABASE_URL

# Automatically convert "postgres://" to "postgresql://" for SQLAlchemy 1.4+ compatibility
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
    logger.info("Automatically converted postgres:// connection string to postgresql://")

# Configure connection pooling and database engine settings
if db_url and db_url.startswith("sqlite"):
    engine = create_engine(
        db_url, 
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        db_url,
        pool_pre_ping=True,      # Tests connection liveness before executing queries
        pool_recycle=1800,       # Recycles connections after 30 minutes to prevent timeouts on serverless backends like Neon
        pool_size=10,            # Main connection pool limit
        max_overflow=20          # Allows up to 20 additional overflow connections under heavy load
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    FastAPI dependency that provides a transactional database session.
    Ensures the session is closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
