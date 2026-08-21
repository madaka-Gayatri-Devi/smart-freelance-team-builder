from flask import Flask, render_template  # Creates the Flask app and renders HTML.
from flask_login import LoginManager  # Manages user login sessions.
from flask_cors import CORS  # Allows frontend requests to the backend.
from authlib.integrations.flask_client import OAuth  # Handles Google OAuth login.
from bson import ObjectId  # Handles MongoDB document IDs.
from config import Config  # Imports all application configuration.
from database.mongodb import init_db, get_db  # Imports MongoDB functions.
from models.user import User  # Imports the User model.
from routes.auth import auth  # Imports authentication routes.
app = Flask(__name__)  # Creates the Flask application.
app.config.from_object(Config)  # Loads all settings from config.py.
CORS(app)  # Enables CORS for the application.
init_db()  # Connects the application to MongoDB.
app.register_blueprint(auth)  # Registers login, register, and logout routes.
login_manager = LoginManager()  # Creates the Flask-Login manager.
login_manager.init_app(app)  # Connects Flask-Login to the Flask application.
login_manager.login_view = "auth.login"  # Sets the login route for protected pages.
oauth = OAuth(app)  # Creates the OAuth manager.
google = oauth.register(
    name="google",  # Gives the Google provider a name.
    client_id=app.config["GOOGLE_CLIENT_ID"],  # Gets the Google client ID from config.py.
    client_secret=app.config["GOOGLE_CLIENT_SECRET"],  # Gets the Google client secret from config.py.
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",  # Google OAuth configuration.
    client_kwargs={
        "scope": "openid email profile"  # Requests basic Google account information.
    }
)
app.extensions["google_oauth"] = google  # Makes the Google OAuth client available to auth routes.
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