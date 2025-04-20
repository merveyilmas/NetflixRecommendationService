from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, Movie
from app.routers.auth import get_current_user
from app.services.movies_service import (
    get_movies,
    get_movie_by_id,
    create_movie,
    update_movie,
    delete_movie
)
from app.schemas.movie_schemas import MovieCreate, MovieUpdate, MovieResponse

router = APIRouter()

@router.get("/", response_model=List[MovieResponse])
def read_movies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    movies = get_movies(db, skip, limit)
    return movies

@router.get("/{movie_id}", response_model=MovieResponse)
def read_movie(
    movie_id: int,
    db: Session = Depends(get_db)
):
    db_movie = get_movie_by_id(db, movie_id)
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return db_movie

@router.post("/", response_model=MovieResponse)
def create_movie_endpoint(
    movie: MovieCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_movie = create_movie(db, movie.dict())
    return db_movie

@router.put("/{movie_id}", response_model=MovieResponse)
def update_movie_endpoint(
    movie_id: int,
    movie: MovieUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_movie = update_movie(db, movie_id, movie.dict(exclude_unset=True))
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return db_movie

@router.delete("/{movie_id}")
def delete_movie_endpoint(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = delete_movie(db, movie_id)
    if not success:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"message": "Movie deleted successfully"}
