from fastapi import FastAPI
from app.models import User, Movie, Rating
from app.database import engine
from app.routers import auth, movies, ratings, recommendations

# Create database tables
Rating.metadata.create_all(bind=engine)

app = FastAPI()

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(movies.router, prefix="/movies", tags=["movies"])
app.include_router(ratings.router, prefix="/ratings", tags=["ratings"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"]) 