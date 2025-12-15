from pydantic import BaseModel, Field
from typing import Optional, List

class UserCreate(BaseModel):
    user_id: int = Field(..., description="MovieLens user_id (demo users)")

class UserOut(BaseModel):
    user_id: int
    class Config:
        from_attributes = True

class MovieOut(BaseModel):
    movie_id: int
    title: str
    genres: Optional[str] = None
    class Config:
        from_attributes = True

class WatchedCreate(BaseModel):
    movie_id: int
    rating: Optional[float] = Field(None, description="Optional rating; if not provided default=4.0")

class RecommendationItem(BaseModel):
    movie_id: int
    title: str
    score: int
    reasons: Optional[List[str]] = None
