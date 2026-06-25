from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import List, Optional, Any
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Movie AI Rating Platform"
    ENVIRONMENT: str = "development"
    
    # JWT Security Configuration
    SECRET_KEY: str = "9a8b7c6d5e4f3g2h1i0j9k8l7m6n5o4p3q2r1s0t"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./movies.db"
    
    # TMDb API Config (optional for fallback mock data)
    TMDB_API_KEY: Optional[str] = None
    
    # OMDb API Config (optional for official IMDb & Metacritic scores)
    OMDB_API_KEY: Optional[str] = None
    
    # YouTube API Config (optional for reviews scraper)
    YOUTUBE_API_KEY: Optional[str] = None
    
    # CORS Origins (Handles comma separated string or lists)
    BACKEND_CORS_ORIGINS: Any = ["*"]

    # Read from .env in the backend directory or local env vars
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["*"]

# Instantiate settings
settings = Settings()
