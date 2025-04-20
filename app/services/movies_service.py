from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import Movie

def get_movies(db: Session, skip: int = 0, limit: int = 100) -> List[Movie]:
    return db.query(Movie).offset(skip).limit(limit).all()

def get_movie_by_id(db: Session, movie_id: int) -> Optional[Movie]:
    return db.query(Movie).filter(Movie.id == movie_id).first()

def create_movie(db: Session, movie_data: dict) -> Movie:
    db_movie = Movie(
        title=movie_data["title"],
        description=movie_data["description"],
        genre=movie_data["genre"],
        release_year=movie_data["release_year"]
    )
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

def update_movie(db: Session, movie_id: int, movie_data: dict) -> Optional[Movie]:
    db_movie = get_movie_by_id(db, movie_id)
    if not db_movie:
        return None
    
    for key, value in movie_data.items():
        setattr(db_movie, key, value)
    
    db.commit()
    db.refresh(db_movie)
    return db_movie

def delete_movie(db: Session, movie_id: int) -> bool:
    db_movie = get_movie_by_id(db, movie_id)
    if not db_movie:
        return False
    
    db.delete(db_movie)
    db.commit()
    return True 