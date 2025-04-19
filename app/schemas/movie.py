from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class MovieBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    release_year: int = Field(..., ge=1900, le=datetime.now().year)
    genre: str = Field(..., min_length=1, max_length=50)
    duration: int = Field(..., ge=1)
    rating: float = Field(..., ge=0, le=10)
    feature_vector: str

class MovieCreate(MovieBase):
    pass

class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    release_year: Optional[int] = Field(None, ge=1900, le=datetime.now().year)
    genre: Optional[str] = Field(None, min_length=1, max_length=50)
    duration: Optional[int] = Field(None, ge=1)
    rating: Optional[float] = Field(None, ge=0, le=10)
    feature_vector: Optional[str] = None

class MovieInDB(MovieBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MovieResponse(MovieBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 