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

## Project Structure

```
netflixRecommendation/
├── app/
│   ├── core/           # Core configurations and utilities
│   ├── models/         # Database models
│   ├── schemas/        # Pydantic models for request/response
│   ├── services/       # Business logic and services
│   ├── database.py     # Database connection and session
│   ├── main.py         # FastAPI application entry point
│   ├── models.py       # ML models and recommendation logic
│   ├── recommendation.py # Recommendation system implementation
│   └── schemas.py      # API schemas
├── .env                # Environment variables
└── README.md           # Project documentation
```

## Prerequisites

- Python 3.8+
- PostgreSQL
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/merveyilmas/NetflixRecommendationService.git
cd netflixRecommendation
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/netflix_recommendation
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. Start the Database and Application:
```bash
# First, ensure PostgreSQL is running and the database exists
createdb netflix_recommendation
# Then run the application which will create the tables
uvicorn app.main:app --reload
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token
- `GET /auth/me` - Get current user information

### Movies
- `GET /movies/` - Get list of movies (with pagination)
- `GET /movies/{movie_id}` - Get movie by ID
- `POST /movies/` - Add a new movie
- `PUT /movies/{movie_id}` - Update a movie
- `DELETE /movies/{movie_id}` - Delete a movie

### Ratings
- `GET /ratings/user` - Get current user's ratings
- `GET /ratings/movie/{movie_id}` - Get ratings for a specific movie
- `POST /ratings/` - Create a new rating
- `PUT /ratings/{rating_id}` - Update a rating
- `DELETE /ratings/{rating_id}` - Delete a rating

### Recommendations
- `GET /recommendations/` - Get personalized movie recommendations

## Example Usage

1. Register a new user:
```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "email": "test@example.com", "password": "test123"}'
```

2. Login and get token:
```bash
curl -X POST "http://localhost:8000/auth/login" \
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

4. Get recommendations:
```bash
curl -X GET "http://localhost:8000/recommendations/" \
     -H "Authorization: Bearer <your_token>"
```

## Development

To run the application in development mode:
```bash
uvicorn app.main:app --reload
```

The API documentation will be available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FastAPI team for the amazing web framework
- scikit-learn team for the machine learning library
- PostgreSQL team for the database system 