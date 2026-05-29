from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Movie AI Rating Platform"
    ENVIRONMENT: str = "development"
    
    # JWT Security Configuration
    SECRET_KEY: str = "9a8b7c6d5e4f3g2h1i0j9k8l7m6n5o4p3q2r1s0t"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/movie_db"
    
    # TMDb API Config
    TMDB_API_KEY: Optional[str] = None
    
    # OMDb API Config (for official IMDb & Metacritic scores)
    OMDB_API_KEY: Optional[str] = None
    
    # CORS Origins (Comma separated string converted to list)
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()
