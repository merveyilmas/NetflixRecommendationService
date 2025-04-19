from database import init_db, engine
from models import Base
import os
from dotenv import load_dotenv

load_dotenv()

def test_database_connection():
    try:
        # Try to create all tables
        Base.metadata.create_all(bind=engine)
        print("Database connection successful! Tables created.")
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        print("Please check:")
        print("1. PostgreSQL is running")
        print("2. Database 'netflix_recommendation' exists")
        print("3. .env file has correct DATABASE_URL")
        print(f"Current DATABASE_URL: {os.getenv('DATABASE_URL')}")

if __name__ == "__main__":
    test_database_connection() 