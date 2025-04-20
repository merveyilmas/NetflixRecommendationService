from pydantic import BaseModel
from typing import Optional

class MovieBase(BaseModel):
    title: str
    description: Optional[str] = None
    genre: Optional[str] = None
    release_year: Optional[int] = None

class MovieCreate(MovieBase):
    pass

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    release_year: Optional[int] = None

class MovieResponse(MovieBase):
    id: int
    
    class Config:
        from_attributes = True 