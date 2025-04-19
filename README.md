# Netflix-like Movie Recommendation System

A collaborative filtering movie recommendation system that suggests movies based on user preferences and ratings. Built with FastAPI, PostgreSQL, and machine learning algorithms.

## Features

- User authentication and authorization
- Movie management (add, view, rate)
- Collaborative filtering recommendation system
- Cosine similarity for user-based recommendations
- RESTful API endpoints
- Database reset functionality
- Unique recommendations based on user preferences

## Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL
- **Machine Learning**: scikit-learn, pandas, numpy
- **Authentication**: JWT (JSON Web Tokens)
- **Dependencies**: SQLAlchemy, pydantic, python-jose, passlib

## Prerequisites

- Python 3.8+
- PostgreSQL
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/merveyilmas/NetflixRecommendationService.git
cd netflix-recommendation
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

4. Set up environment variables:
Create a `.env` file in the project root with:
```env
DATABASE_URL=postgresql://postgres:12345@localhost:5432/netflix_recommendation
```

5. Initialize the database:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Authentication
- `POST /users/` - Register a new user
- `POST /token` - Login and get access token

### Movies
- `GET /movies/` - Get list of movies
- `POST /movies/` - Add a new movie
- `POST /ratings/` - Rate a movie
- `GET /recommendations/` - Get personalized movie recommendations
- `POST /reset/` - Reset the database (for testing purposes)

## Example Usage

1. Register a new user:
```bash
curl -X POST "http://localhost:8000/users/" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "email": "test@example.com", "password": "test123"}'
```

2. Login and get token:
```bash
curl -X POST "http://localhost:8000/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=testuser&password=test123"
```

3. Add a movie:
```bash
curl -X POST "http://localhost:8000/movies/" \
     -H "Authorization: Bearer <your_token>" \
     -H "Content-Type: application/json" \
     -d '{
         "title": "Inception",
         "description": "A thief who steals corporate secrets through the use of dream-sharing technology",
         "genre": "Sci-Fi",
         "release_year": 2010
     }'
```

4. Rate a movie:
```bash
curl -X POST "http://localhost:8000/ratings/" \
     -H "Authorization: Bearer <your_token>" \
     -H "Content-Type: application/json" \
     -d '{"movie_id": 1, "rating": 4.5}'
```

5. Get recommendations:
```bash
curl -X GET "http://localhost:8000/recommendations/" \
     -H "Authorization: Bearer <your_token>"
```

6. Reset database (for testing):
```bash
curl -X POST "http://localhost:8000/reset/" \
     -H "Authorization: Bearer <your_token>"
```

## How It Works

The recommendation system uses a collaborative filtering approach:

1. **User Ratings**: Users rate movies on a scale of 1-5
2. **Similarity Calculation**: The system calculates cosine similarity between users based on their ratings
3. **Recommendation Generation**:
   - For users with no ratings: Returns most popular movies
   - For users with ratings: Finds similar users and recommends movies they liked but the current user hasn't rated
   - If no similar users found: Returns most popular unrated movies
4. **Personalization**: Recommendations are unique to each user and only include movies they haven't rated yet

## Example Scenarios

1. **Sci-Fi Fan**:
   - Rates sci-fi movies highly
   - Gets recommendations for action, drama, and crime movies

2. **Action Lover**:
   - Rates action movies highly
   - Gets recommendations for sci-fi and other genres

3. **Movie Buff**:
   - Rates various genres
   - Gets recommendations for unrated movies based on similar users' preferences

## Testing

Run the test script to see the recommendation system in action:
```bash
python test_api.py
```

This will:
1. Create test users with different preferences
2. Add sample movies
3. Simulate user ratings
4. Show personalized recommendations for each user

## Project Structure

```
netflixRecommendation/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Database models
│   ├── database.py          # Database configuration
│   ├── recommendation.py    # Recommendation system
│   └── .env                # Environment variables
├── setup.py                # Package configuration
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FastAPI team for the amazing web framework
- scikit-learn team for the machine learning library
- PostgreSQL team for the database system 