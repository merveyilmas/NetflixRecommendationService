from setuptools import setup, find_packages

setup(
    name="netflix-recommendation",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.109.2",
        "uvicorn==0.27.1",
        "sqlalchemy==2.0.25",
        "psycopg2-binary==2.9.9",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "python-multipart==0.0.6",
        "python-dotenv==1.0.0",
        "pandas==2.2.0",
        "scikit-learn==1.4.0",
        "numpy==1.26.3"
    ],
) 