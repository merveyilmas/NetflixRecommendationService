from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from . import models
from .database import engine, get_db
from .recommendation import RecommendationSystem

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Security
SECRET_KEY = "your-secret-key"  # Change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True

class MovieCreate(BaseModel):
    title: str
    description: str
    genre: str
    release_year: int

class MovieResponse(BaseModel):
    id: int
    title: str
    description: str
    genre: str
    release_year: int

    class Config:
        orm_mode = True

class RatingCreate(BaseModel):
    movie_id: int
    rating: float

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

# Routes
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/movies/", response_model=List[MovieResponse])
def get_movies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    movies = db.query(models.Movie).offset(skip).limit(limit).all()
    return movies

@app.post("/movies/", response_model=MovieResponse)
def create_movie(
    movie: MovieCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_movie = models.Movie(
        title=movie.title,
        description=movie.description,
        genre=movie.genre,
        release_year=movie.release_year
    )
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

@app.post("/ratings/")
def create_rating(
    rating: RatingCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_rating = models.Rating(
        rating=rating.rating,
        user_id=current_user.id,
        movie_id=rating.movie_id
    )
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating

@app.get("/recommendations/", response_model=List[MovieResponse])
async def get_recommendations(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get all movies
    movies = db.query(models.Movie).all()
    
    # Get all ratings
    ratings = db.query(models.Rating).all()
    
    # Create user-movie rating matrix
    user_ratings = {}
    for rating in ratings:
        if rating.user_id not in user_ratings:
            user_ratings[rating.user_id] = {}
        user_ratings[rating.user_id][rating.movie_id] = rating.rating
    
    # Get movies that current user hasn't rated yet
    current_user_rated_movie_ids = set()
    if current_user.id in user_ratings:
        current_user_rated_movie_ids = set(user_ratings[current_user.id].keys())
    
    unrated_movies = [movie for movie in movies if movie.id not in current_user_rated_movie_ids]
    
    # If no unrated movies, return empty list
    if not unrated_movies:
        return []
    
    # If current user has no ratings, return popular unrated movies
    if not current_user_rated_movie_ids:
        # Calculate average ratings for unrated movies
        movie_avg_ratings = {}
        for movie in unrated_movies:
            movie_ratings = [r.rating for r in movie.ratings]
            if movie_ratings:
                movie_avg_ratings[movie.id] = sum(movie_ratings) / len(movie_ratings)
        
        # Sort movies by average rating
        sorted_movies = sorted(unrated_movies, key=lambda m: movie_avg_ratings.get(m.id, 0), reverse=True)
        return sorted_movies[:5]
    
    # Calculate similarity between current user and other users
    similarities = {}
    current_user_ratings = user_ratings[current_user.id]
    
    for user_id, ratings in user_ratings.items():
        if user_id == current_user.id:
            continue
            
        # Find common movies
        common_movies = set(current_user_ratings.keys()) & set(ratings.keys())
        if not common_movies:
            continue
            
        # Calculate cosine similarity
        current_ratings = [current_user_ratings[movie_id] for movie_id in common_movies]
        other_ratings = [ratings[movie_id] for movie_id in common_movies]
        
        dot_product = sum(a * b for a, b in zip(current_ratings, other_ratings))
        norm_current = sum(r * r for r in current_ratings) ** 0.5
        norm_other = sum(r * r for r in other_ratings) ** 0.5
        
        if norm_current * norm_other == 0:
            continue
            
        similarity = dot_product / (norm_current * norm_other)
        similarities[user_id] = similarity
    
    # If no similar users found, return popular unrated movies
    if not similarities:
        movie_avg_ratings = {}
        for movie in unrated_movies:
            movie_ratings = [r.rating for r in movie.ratings]
            if movie_ratings:
                movie_avg_ratings[movie.id] = sum(movie_ratings) / len(movie_ratings)
        
        sorted_movies = sorted(unrated_movies, key=lambda m: movie_avg_ratings.get(m.id, 0), reverse=True)
        return sorted_movies[:5]
    
    # Get top similar users
    top_users = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # Find movies that similar users liked but current user hasn't rated
    recommended_movies = []
    for user_id, similarity in top_users:
        user_rated_movies = set(user_ratings[user_id].keys())
        unrated_movies_for_user = user_rated_movies - current_user_rated_movie_ids
        
        for movie_id in unrated_movies_for_user:
            if user_ratings[user_id][movie_id] >= 4.0:  # Only recommend highly rated movies
                movie = next((m for m in unrated_movies if m.id == movie_id), None)
                if movie and movie not in recommended_movies:
                    recommended_movies.append(movie)
    
    # If no recommendations found, return popular unrated movies
    if not recommended_movies:
        movie_avg_ratings = {}
        for movie in unrated_movies:
            movie_ratings = [r.rating for r in movie.ratings]
            if movie_ratings:
                movie_avg_ratings[movie.id] = sum(movie_ratings) / len(movie_ratings)
        
        sorted_movies = sorted(unrated_movies, key=lambda m: movie_avg_ratings.get(m.id, 0), reverse=True)
        return sorted_movies[:5]
    
    return recommended_movies[:5]  # Return top 5 recommendations

@app.post("/reset/")
def reset_database(db: Session = Depends(get_db)):
    # Drop all tables
    models.Base.metadata.drop_all(bind=engine)
    # Create all tables
    models.Base.metadata.create_all(bind=engine)
    return {"message": "Database reset successfully"} 