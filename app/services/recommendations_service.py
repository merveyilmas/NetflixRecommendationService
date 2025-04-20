from typing import List, Dict, Tuple
import numpy as np
from sqlalchemy.orm import Session

from app.models import Movie, Rating

def get_user_movie_ratings(db: Session) -> Dict[int, Dict[int, float]]:
    """Create a user-movie rating matrix"""
    ratings = db.query(Rating).all()
    user_movie_ratings = {}
    for rating in ratings:
        if rating.user_id not in user_movie_ratings:
            user_movie_ratings[rating.user_id] = {}
        user_movie_ratings[rating.user_id][rating.movie_id] = rating.rating
    return user_movie_ratings

def get_unrated_movies(db: Session, user_id: int) -> List[Movie]:
    """Get movies that the user hasn't rated yet"""
    user_ratings = db.query(Rating.movie_id).filter(Rating.user_id == user_id).all()
    rated_movie_ids = {rating[0] for rating in user_ratings}
    return db.query(Movie).filter(~Movie.id.in_(rated_movie_ids)).all()

def calculate_cosine_similarity(user1_ratings: Dict[int, float], user2_ratings: Dict[int, float]) -> float:
    """Calculate cosine similarity between two users based on their ratings"""
    common_movies = set(user1_ratings.keys()) & set(user2_ratings.keys())
    if not common_movies:
        return 0.0
    
    user1_vector = np.array([user1_ratings[movie_id] for movie_id in common_movies])
    user2_vector = np.array([user2_ratings[movie_id] for movie_id in common_movies])
    
    dot_product = np.dot(user1_vector, user2_vector)
    norm1 = np.linalg.norm(user1_vector)
    norm2 = np.linalg.norm(user2_vector)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)

def get_similar_users(
    db: Session,
    user_id: int,
    user_movie_ratings: Dict[int, Dict[int, float]],
    min_similarity: float = 0.5
) -> List[Tuple[int, float]]:
    """Get users similar to the current user based on their ratings"""
    if user_id not in user_movie_ratings:
        return []
    
    user_ratings = user_movie_ratings[user_id]
    similar_users = []
    
    for other_user_id, other_ratings in user_movie_ratings.items():
        if other_user_id == user_id:
            continue
        
        similarity = calculate_cosine_similarity(user_ratings, other_ratings)
        if similarity >= min_similarity:
            similar_users.append((other_user_id, similarity))
    
    return sorted(similar_users, key=lambda x: x[1], reverse=True)

def get_popular_movies(db: Session, unrated_movies: List[Movie], min_rating: float = 4.0) -> List[Movie]:
    """Get popular movies based on average ratings"""
    popular_movies = []
    for movie in unrated_movies:
        ratings = db.query(Rating).filter(Rating.movie_id == movie.id).all()
        if not ratings:
            continue
        
        avg_rating = sum(rating.rating for rating in ratings) / len(ratings)
        if avg_rating >= min_rating:
            popular_movies.append(movie)
    
    return sorted(popular_movies, key=lambda x: x.id)

def get_recommendations(
    db: Session,
    user_id: int,
    limit: int = 10
) -> List[Movie]:
    """Get movie recommendations for a user"""
    # Get all necessary data
    user_movie_ratings = get_user_movie_ratings(db)
    unrated_movies = get_unrated_movies(db, user_id)
    
    if not unrated_movies:
        return []
    
    # If user has no ratings, return popular movies
    if user_id not in user_movie_ratings or not user_movie_ratings[user_id]:
        return get_popular_movies(db, unrated_movies)[:limit]
    
    # Get similar users
    similar_users = get_similar_users(db, user_id, user_movie_ratings)
    if not similar_users:
        return get_popular_movies(db, unrated_movies)[:limit]
    
    # Get movies rated highly by similar users
    recommended_movies = []
    for movie in unrated_movies:
        weighted_sum = 0
        similarity_sum = 0
        
        for similar_user_id, similarity in similar_users:
            if movie.id in user_movie_ratings[similar_user_id]:
                rating = user_movie_ratings[similar_user_id][movie.id]
                weighted_sum += rating * similarity
                similarity_sum += similarity
        
        if similarity_sum > 0:
            predicted_rating = weighted_sum / similarity_sum
            if predicted_rating >= 4.0:  # Only recommend highly rated movies
                recommended_movies.append((movie, predicted_rating))
    
    # Sort by predicted rating and return top N
    recommended_movies.sort(key=lambda x: x[1], reverse=True)
    return [movie for movie, _ in recommended_movies[:limit]] 