import requests
import json

BASE_URL = "http://localhost:8000"

def create_user(username, email, password):
    register_data = {
        "username": username,
        "email": email,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/users/", json=register_data)
    return response.json()

def login(username, password):
    login_data = {
        "username": username,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/token", data=login_data)
    return response.json()["access_token"]

def add_movie(token, movie_data):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/movies/", json=movie_data, headers=headers)
    return response.json()

def rate_movie(token, movie_id, rating):
    headers = {"Authorization": f"Bearer {token}"}
    rating_data = {
        "movie_id": movie_id,
        "rating": rating
    }
    response = requests.post(f"{BASE_URL}/ratings/", json=rating_data, headers=headers)
    return response.json()

def test_api():
    try:
        # First, reset the database
        print("Resetting database...")
        requests.post(f"{BASE_URL}/reset/")
        
        # Create multiple users
        users = [
            {"username": "scifi_fan", "email": "scifi@example.com", "password": "test123"},
            {"username": "action_lover", "email": "action@example.com", "password": "test123"},
            {"username": "movie_buff", "email": "buff@example.com", "password": "test123"}
        ]
        
        # First, create all movies using the first user
        print("\nCreating movies...")
        first_user = users[0]
        create_user(**first_user)
        token = login(first_user["username"], first_user["password"])
        
        test_movies = [
            {
                "title": "Inception",
                "description": "A thief who steals corporate secrets through the use of dream-sharing technology",
                "genre": "Sci-Fi",
                "release_year": 2010
            },
            {
                "title": "The Dark Knight",
                "description": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham",
                "genre": "Action",
                "release_year": 2008
            },
            {
                "title": "Interstellar",
                "description": "A team of explorers travel through a wormhole in space",
                "genre": "Sci-Fi",
                "release_year": 2014
            },
            {
                "title": "The Matrix",
                "description": "A computer hacker learns about the true nature of reality",
                "genre": "Sci-Fi",
                "release_year": 1999
            },
            {
                "title": "Pulp Fiction",
                "description": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine",
                "genre": "Crime",
                "release_year": 1994
            },
            {
                "title": "The Shawshank Redemption",
                "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency",
                "genre": "Drama",
                "release_year": 1994
            },
            {
                "title": "Fight Club",
                "description": "An insomniac office worker and a devil-may-care soapmaker form an underground fight club that evolves into something much, much more",
                "genre": "Drama",
                "release_year": 1999
            }
        ]
        
        for movie in test_movies:
            print(f"Adding movie: {movie['title']}")
            add_movie(token, movie)
        
        # Get all movies
        movies_response = requests.get(f"{BASE_URL}/movies/", headers={"Authorization": f"Bearer {token}"})
        movies = movies_response.json()
        
        # Now create other users and have them rate different subsets of movies
        for user in users:
            print(f"\nProcessing user: {user['username']}")
            if user["username"] != first_user["username"]:
                create_user(**user)
                token = login(user["username"], user["password"])
            
            # Rate movies based on user preferences
            if user["username"] == "scifi_fan":
                # Sci-Fi fan rates only sci-fi movies
                for movie in movies:
                    if movie["genre"] == "Sci-Fi":
                        print(f"{user['username']} rating {movie['title']}: 5.0")
                        rate_movie(token, movie["id"], 5.0)
            
            elif user["username"] == "action_lover":
                # Action lover rates action and some sci-fi movies
                for movie in movies:
                    if movie["genre"] == "Action":
                        print(f"{user['username']} rating {movie['title']}: 5.0")
                        rate_movie(token, movie["id"], 5.0)
                    elif movie["title"] in ["Inception", "The Matrix"]:
                        print(f"{user['username']} rating {movie['title']}: 4.0")
                        rate_movie(token, movie["id"], 4.0)
            
            else:  # movie_buff
                # Movie buff rates a mix of movies
                for movie in movies:
                    if movie["title"] in ["The Dark Knight", "Pulp Fiction", "The Shawshank Redemption"]:
                        print(f"{user['username']} rating {movie['title']}: 5.0")
                        rate_movie(token, movie["id"], 5.0)
                    elif movie["title"] in ["Inception", "Fight Club"]:
                        print(f"{user['username']} rating {movie['title']}: 4.5")
                        rate_movie(token, movie["id"], 4.5)

            # Get recommendations for each user
            recommendations_response = requests.get(
                f"{BASE_URL}/recommendations/",
                headers={"Authorization": f"Bearer {token}"}
            )
            try:
                recommendations = recommendations_response.json()
                print(f"\nRecommendations for {user['username']}:")
                if not recommendations:
                    print("No recommendations available yet.")
                else:
                    # Remove duplicates
                    seen_titles = set()
                    unique_recommendations = []
                    for movie in recommendations:
                        if movie["title"] not in seen_titles:
                            seen_titles.add(movie["title"])
                            unique_recommendations.append(movie)
                    
                    for movie in unique_recommendations:
                        print(f"- {movie['title']} ({movie['genre']})")
            except json.JSONDecodeError:
                print("No recommendations available yet.")

    except Exception as e:
        print("Unexpected error:", str(e))

if __name__ == "__main__":
    test_api() 