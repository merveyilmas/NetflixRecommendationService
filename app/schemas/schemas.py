from pydantic import BaseModel, EmailStr
from typing import Optional, List

class MovieBase(BaseModel):
    title: str
    description: Optional[str] = None
    genre: Optional[str] = None
    release_year: Optional[int] = None

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id: int
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

class RatingBase(BaseModel):
    rating: float

class RatingCreate(RatingBase):
    movie_id: int

class Rating(RatingBase):
    user_id: int
    movie_id: int
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None 