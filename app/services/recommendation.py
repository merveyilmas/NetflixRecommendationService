import numpy as np
from sklearn.preprocessing import StandardScaler
import json
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import logging

from app.db.models import User, Movie
from app.schemas.movie import MovieResponse

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self):
        self.scaler = StandardScaler()
        self._is_fitted = False
    
    def _vector_to_array(self, vector_str: str) -> np.ndarray:
        try:
            if vector_str is None:
                return np.zeros(10)
            return np.array(json.loads(vector_str))
        except Exception as e:
            logger.error(f"Error converting vector to array: {str(e)}")
            return np.zeros(10)
    
    def _array_to_vector(self, array: np.ndarray) -> str:
        try:
            return json.dumps(array.tolist())
        except Exception as e:
            logger.error(f"Error converting array to vector: {str(e)}")
            return json.dumps([0] * 10)
    
    def update_user_preferences(self, db: Session, user_id: int) -> bool:
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"User {user_id} not found")
                return False
            
            watched_movies = user.watched_movies
            if not watched_movies:
                logger.info(f"User {user_id} has no watched movies")
                return False
            
            feature_vectors = [self._vector_to_array(movie.feature_vector) for movie in watched_movies]
            if feature_vectors:
                user_preference = np.mean(feature_vectors, axis=0)
                user.preference_vector = self._array_to_vector(user_preference)
                db.commit()
                logger.info(f"Updated preferences for user {user_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error updating user preferences: {str(e)}")
            return False
    
    def get_recommendations(
        self, 
        db: Session, 
        user_id: int, 
        n_recommendations: int = 10
    ) -> List[Dict]:
        try:
            logger.info(f"Getting recommendations for user {user_id}")
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"User {user_id} not found")
                return []
            
            if not user.preference_vector:
                logger.warning(f"User {user_id} has no preference vector")
                return []
            
            # Get user's preference vector
            user_preference = self._vector_to_array(user.preference_vector)
            
            # Get movies not watched by user
            watched_movie_ids = [movie.id for movie in user.watched_movies]
            potential_movies = db.query(Movie).filter(~Movie.id.in_(watched_movie_ids)).all()
            
            if not potential_movies:
                logger.info(f"No potential movies found for user {user_id}")
                return []
            
            # Prepare feature vectors
            movie_vectors = np.array([self._vector_to_array(movie.feature_vector) for movie in potential_movies])
            
            # Scale vectors if not already fitted
            if not self._is_fitted:
                self.scaler.fit(movie_vectors)
                self._is_fitted = True
            
            scaled_movie_vectors = self.scaler.transform(movie_vectors)
            scaled_user_preference = self.scaler.transform([user_preference])[0]
            
            # Calculate cosine similarity
            similarities = []
            for movie, movie_vector in zip(potential_movies, scaled_movie_vectors):
                similarity = np.dot(scaled_user_preference, movie_vector) / (
                    np.linalg.norm(scaled_user_preference) * np.linalg.norm(movie_vector)
                )
                similarities.append((movie, similarity))
            
            # Sort by similarity and get top recommendations
            similarities.sort(key=lambda x: x[1], reverse=True)
            recommendations = [
                {
                    "id": movie.id,
                    "title": movie.title,
                    "description": movie.description,
                    "genre": movie.genre,
                    "rating": movie.rating,
                    "similarity": float(similarity)
                }
                for movie, similarity in similarities[:n_recommendations]
            ]
            
            logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in get_recommendations: {str(e)}")
            return []

recommendation_service = RecommendationService() 