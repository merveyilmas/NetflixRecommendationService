from pydantic import BaseModel
from typing import Optional

class RatingBase(BaseModel):
    rating: float

class RatingCreate(RatingBase):
    movie_id: int

class RatingUpdate(RatingBase):
    pass

class RatingResponse(RatingBase):
    id: int
    user_id: int
    movie_id: int
    
    class Config:
        from_attributes = True 