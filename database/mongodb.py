from pymongo import MongoClient  # Imports MongoDB client from PyMongo.
import os  # Allows us to read settings from the environment.
client = None  # Stores the MongoDB connection.
db = None  # Stores our project database.
def init_db():
    global client, db  # Allows this function to update the global variables.
    mongo_uri = os.getenv(
        "MONGO_URI",
        "mongodb://localhost:27017/"
    )  # Gets the MongoDB URL from .env.
    database_name = os.getenv(
        "DATABASE_NAME",
        "smart_freelance_team_builder"
    )  # Gets the database name from .env.
    client = MongoClient(
        mongo_uri,
        serverSelectionTimeoutMS=5000
    )  # Connects to the local MongoDB server without SSL.
    client.admin.command("ping")  # Checks whether MongoDB is reachable.
    db = client[database_name]  # Selects our project database.
    print("MongoDB connected successfully.")  # Shows successful connection.
    print(f"Database: {database_name}")  # Shows the database name.
    return db  # Returns the database connection.
def get_db():
    return db  # Gives other backend files access to our database.