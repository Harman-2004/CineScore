from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict, Any
from datetime import datetime

class MovieGenre(BaseModel):
    id: int
    name: str

class MovieResponse(BaseModel):
    id: int
    title: str
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    release_date: Optional[str] = None
    genres: Optional[List[Union[MovieGenre, Dict[str, Any]]]] = None
    vote_average: Optional[float] = 0.0
    imdb_rating: Optional[float] = None
    metacritic_score: Optional[float] = None  # Metacritic rating score (out of 10)

class MovieListResponse(BaseModel):
    page: int
    results: List[MovieResponse]
    total_pages: int
    total_results: int

class MovieCacheResponse(BaseModel):
    id: int
    title: str
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    release_date: Optional[str] = None
    genres: Optional[List[Dict[str, Any]]] = None
    vote_average: float
    imdb_rating: Optional[float] = None
    metacritic_score: Optional[float] = None  # Cached Metacritic rating
    cached_at: datetime

    class Config:
        from_attributes = True
