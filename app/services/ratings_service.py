from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import Rating

def get_ratings_by_user(db: Session, user_id: int) -> List[Rating]:
    return db.query(Rating).filter(Rating.user_id == user_id).all()

def get_ratings_by_movie(db: Session, movie_id: int) -> List[Rating]:
    return db.query(Rating).filter(Rating.movie_id == movie_id).all()

def get_rating_by_user_and_movie(db: Session, user_id: int, movie_id: int) -> Optional[Rating]:
    return db.query(Rating).filter(
        Rating.user_id == user_id,
        Rating.movie_id == movie_id
    ).first()

def create_rating(db: Session, rating_data: dict) -> Rating:
    db_rating = Rating(
        rating=rating_data["rating"],
        user_id=rating_data["user_id"],
        movie_id=rating_data["movie_id"]
    )
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating

def update_rating(db: Session, rating_id: int, rating_value: float) -> Optional[Rating]:
    db_rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not db_rating:
        return None
    
    db_rating.rating = rating_value
    db.commit()
    db.refresh(db_rating)
    return db_rating

def delete_rating(db: Session, rating_id: int) -> bool:
    db_rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not db_rating:
        return False
    
    db.delete(db_rating)
    db.commit()
    return True 