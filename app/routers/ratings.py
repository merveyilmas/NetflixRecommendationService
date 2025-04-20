from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User
from app.routers.auth import get_current_user
from app.services.ratings_service import (
    get_ratings_by_user,
    get_ratings_by_movie,
    get_rating_by_user_and_movie,
    create_rating,
    update_rating,
    delete_rating
)
from app.schemas.rating_schemas import RatingCreate, RatingUpdate, RatingResponse

router = APIRouter()

@router.get("/user/", response_model=List[RatingResponse])
def read_user_ratings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ratings = get_ratings_by_user(db, current_user.id)
    return [RatingResponse.model_validate(rating.__dict__) for rating in ratings]

@router.get("/movie/{movie_id}", response_model=List[RatingResponse])
def read_movie_ratings(movie_id: int, db: Session = Depends(get_db)):
    ratings = get_ratings_by_movie(db, movie_id)
    return [RatingResponse.model_validate(rating.__dict__) for rating in ratings]

@router.post("/", response_model=RatingResponse)
def create_rating_endpoint(
    rating: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if user has already rated this movie
    existing_rating = get_rating_by_user_and_movie(db, current_user.id, rating.movie_id)
    if existing_rating:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already rated this movie"
        )
    
    rating_data = rating.dict()
    rating_data["user_id"] = current_user.id
    db_rating = create_rating(db, rating_data)
    return RatingResponse.model_validate(db_rating.__dict__)

@router.put("/{rating_id}", response_model=RatingResponse)
def update_rating_endpoint(
    rating_id: int,
    rating: RatingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_rating = update_rating(db, rating_id, rating.rating)
    if db_rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")
    return RatingResponse.model_validate(db_rating.__dict__)

@router.delete("/{rating_id}")
def delete_rating_endpoint(
    rating_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = delete_rating(db, rating_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rating not found")
    return {"message": "Rating deleted successfully"} 