from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Association table for user-movie ratings
user_movie_ratings = Table(
    'user_movie_ratings',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('movie_id', Integer, ForeignKey('movies.id'), primary_key=True),
    Column('rating', Float)
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Relationship with movies through ratings
    rated_movies = relationship("Movie", secondary=user_movie_ratings, back_populates="rated_by")

class Movie(Base):
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    genre = Column(String)
    release_year = Column(Integer)
    
    # Relationship with users through ratings
    rated_by = relationship("User", secondary=user_movie_ratings, back_populates="rated_movies") 