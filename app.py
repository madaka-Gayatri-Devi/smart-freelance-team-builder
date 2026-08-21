from flask import Flask, render_template  # Creates the Flask app and renders HTML.
from flask_login import LoginManager  # Manages user login sessions.
from flask_cors import CORS  # Allows frontend requests to the backend.
from dotenv import load_dotenv  # Loads variables from the .env file.
from bson import ObjectId  # Handles MongoDB document IDs.
import os  # Reads environment variables.
from database.mongodb import init_db, get_db  # Imports MongoDB functions.
from models.user import User  # Imports the User model.
from routes.auth import auth  # Imports the authentication routes.
from routes.client import client
from routes.freelancer import freelancer
from routes.admin import admin

load_dotenv()  # Loads the values from the .env file
app = Flask(__name__)  # Creates the Flask application.
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "smartteam-development-secret-key"
)  # Sets the secret key used for secure sessions.
CORS(app)  # Enables CORS for the application.
init_db()  # Connects the application to MongoDB.

app.register_blueprint(auth)  # Registers login, register, and logout routes.
app.register_blueprint(client, url_prefix='/client')
app.register_blueprint(freelancer, url_prefix='/freelancer')
app.register_blueprint(admin, url_prefix='/admin')
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

DEMO_PROFILES = {
    "sarah": {
        "name": "Sarah Johnson",
        "role": "UI/UX Designer",
        "rating": 4.9,
        "status": "Top Rated",
        "available": True,
        "image": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=400&q=80",
        "skills": ["Figma", "UX Research", "Design Systems", "Prototyping", "Wireframing"],
        "bio": "Experienced UI/UX designer focused on creating intuitive and scalable digital experiences. I specialize in bridging the gap between user needs and business goals through clean, accessible design.",
        "experience": "5+ Years",
        "projects": 42,
        "rate": "$65/hr",
        "reviews": [
            {"author": "NovaTech", "text": "Sarah completely transformed our SaaS dashboard. Intuitive and beautiful."},
            {"author": "BrightCommerce", "text": "Delivered the mobile app designs ahead of schedule. Highly recommended."}
        ]
    },
    "michael": {
        "name": "Michael Thomas",
        "role": "React Developer",
        "rating": 4.8,
        "status": "Available",
        "available": True,
        "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80",
        "skills": ["React", "Node.js", "MongoDB", "Redux", "TypeScript"],
        "bio": "Full-stack developer with a passion for building fast, responsive web applications using the MERN stack.",
        "experience": "4 Years",
        "projects": 28,
        "rate": "$55/hr",
        "reviews": [
            {"author": "CloudWorks", "text": "Michael built our client portal from scratch. Excellent React skills."},
        ]
    },
    "david": {
        "name": "David Rodriguez",
        "role": "Backend Developer",
        "rating": 4.9,
        "status": "Expert",
        "available": True,
        "image": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=400&q=80",
        "skills": ["Python", "Flask", "PostgreSQL", "Docker", "AWS"],
        "bio": "Backend architect specializing in scalable APIs, microservices, and database optimization.",
        "experience": "7 Years",
        "projects": 56,
        "rate": "$80/hr",
        "reviews": [
            {"author": "MarketPro", "text": "David optimized our database queries and reduced load times by 70%."}
        ]
    },
    "emily": {
        "name": "Emily Chen",
        "role": "Data Scientist",
        "rating": 5.0,
        "status": "Available",
        "available": True,
        "image": "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?auto=format&fit=crop&w=400&q=80",
        "skills": ["Python", "Machine Learning", "AI", "TensorFlow", "Data Analysis"],
        "bio": "Data scientist helping businesses leverage their data through predictive modeling and machine learning.",
        "experience": "6 Years",
        "projects": 34,
        "rate": "$90/hr",
        "reviews": [
            {"author": "FinTech Startup", "text": "Emily's predictive model increased our conversion rate significantly."}
        ]
    }
}

@app.route("/profile/<username>")
def profile(username):
    profile_data = DEMO_PROFILES.get(username)
    if not profile_data:
        from flask import abort
        abort(404)
    return render_template("profile.html", profile=profile_data)

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