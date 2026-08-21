import os  # Reads configuration values from the environment.
from dotenv import load_dotenv  # Loads values from the .env file.
load_dotenv()  # Loads the .env file.
class Config:
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "smartteam-development-secret-key"
    )  # Stores the Flask secret key.
    MONGO_URI = os.getenv(
        "MONGO_URI",
        "mongodb://localhost:27017/"
    )  # Stores the MongoDB connection URL.
    DATABASE_NAME = os.getenv(
        "DATABASE_NAME",
        "smart_freelance_team_builder"
    )  # Stores the MongoDB database name.
    GOOGLE_CLIENT_ID = os.getenv(
        "GOOGLE_CLIENT_ID"
    )  # Stores the Google OAuth client ID.
    GOOGLE_CLIENT_SECRET = os.getenv(
        "GOOGLE_CLIENT_SECRET"
    )  # Stores the Google OAuth client secret.
    GOOGLE_REDIRECT_URI = os.getenv(
        "GOOGLE_REDIRECT_URI",
        "http://localhost:5000/auth/google/callback"
    )  # Stores the Google OAuth callback URL.