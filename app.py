from flask import Flask, render_template  # Creates the Flask app and renders HTML.
from flask_login import LoginManager  # Manages user login sessions.
from flask_cors import CORS  # Allows frontend requests to the backend.
from dotenv import load_dotenv  # Loads variables from the .env file.
from bson import ObjectId  # Handles MongoDB document IDs.
import os  # Reads environment variables.
from database.mongodb import init_db, get_db  # Imports MongoDB functions.
from models.user import User  # Imports the User model.
from routes.auth import auth  # Imports the authentication routes.
load_dotenv()  # Loads the values from the .env file
app = Flask(__name__)  # Creates the Flask application.
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "smartteam-development-secret-key"
)  # Sets the secret key used for secure sessions.
CORS(app)  # Enables CORS for the application.
init_db()  # Connects the application to MongoDB.
app.register_blueprint(auth)  # Registers login, register, and logout routes.
login_manager = LoginManager()  # Creates the Flask-Login manager.
login_manager.init_app(app)  # Connects Flask-Login to the Flask application.
login_manager.login_view = "auth.login"  # Sets the login route for protected pages.
@login_manager.user_loader
def load_user(user_id):
    db = get_db()  # Gets the MongoDB database.
    try:
        user_data = db.users.find_one(
            {"_id": ObjectId(user_id)}
        )  # Finds the user using their MongoDB ID.
    except Exception:
        return None  # Returns no user if the ID is invalid.
    if not user_data:
        return None  # Returns no user if the user does not exist.
    return User(user_data)  # Converts the MongoDB document into a Flask user.
@app.route("/")
def home():
    return render_template("landing.html")  # Displays the SmartTeam landing page.
@app.route("/health")
def health():
    return {
        "status": "success",
        "message": "SmartTeam backend is running"
    }  # Provides a simple backend health check.
if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )  # Starts the Flask development server.