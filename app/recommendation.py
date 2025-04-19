from sqlalchemy.orm import Session
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class RecommendationSystem:
    def __init__(self, db: Session):
        self.db = db
        
    def get_recommendations(self, user_id: int, n_recommendations: int = 5):
        # Get all ratings
        ratings = self.db.execute("""
            SELECT user_id, movie_id, rating 
            FROM ratings
        """).fetchall()
        
        if not ratings:
            return []
            
        # Convert to DataFrame
        ratings_df = pd.DataFrame(ratings, columns=['user_id', 'movie_id', 'rating'])
        
        # Create user-movie matrix
        user_movie_matrix = ratings_df.pivot(
            index='user_id',
            columns='movie_id',
            values='rating'
        ).fillna(0)
        
        # Calculate user similarity
        user_similarity = cosine_similarity(user_movie_matrix)
        user_similarity_df = pd.DataFrame(
            user_similarity,
            index=user_movie_matrix.index,
            columns=user_movie_matrix.index
        )
        
        # Get similar users
        similar_users = user_similarity_df[user_id].sort_values(ascending=False)[1:6]
        
        # Get movies rated by similar users
        similar_users_ratings = ratings_df[ratings_df['user_id'].isin(similar_users.index)]
        
        # Get movies not rated by the current user
        user_rated_movies = set(ratings_df[ratings_df['user_id'] == user_id]['movie_id'])
        recommended_movies = similar_users_ratings[
            ~similar_users_ratings['movie_id'].isin(user_rated_movies)
        ]
        
        # Calculate weighted average ratings
        movie_scores = recommended_movies.groupby('movie_id').apply(
            lambda x: np.average(x['rating'], weights=similar_users[x['user_id']])
        ).sort_values(ascending=False)
        
        # Get top n recommendations
        top_movie_ids = movie_scores.head(n_recommendations).index.tolist()
        
        # Get movie details
        recommended_movies = self.db.execute("""
            SELECT id, title, description, genre, release_year 
            FROM movies 
            WHERE id IN :movie_ids
        """, {"movie_ids": tuple(top_movie_ids)}).fetchall()
        
        return [
            {
                "id": movie.id,
                "title": movie.title,
                "description": movie.description,
                "genre": movie.genre,
                "release_year": movie.release_year
            }
            for movie in recommended_movies
        ] 