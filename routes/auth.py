from flask import Blueprint, request, redirect, url_for, flash, current_app, session
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from database.mongodb import get_db
from models.user import User
auth = Blueprint("auth", __name__)
# Login route
@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember_me = request.form.get("remember_me") == "on"
        if not email or not password:
            flash("Please enter your email and password.", "danger")
            return redirect(url_for("home", auth="login"))
        db = get_db()
        user_data = db.users.find_one({"email": email})
        if not user_data:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("home", auth="login"))
        if not user_data.get("is_active", True):
            flash("Your account has been disabled.", "danger")
            return redirect(url_for("home", auth="login"))
        password_hash = user_data.get("password_hash")
        if not password_hash or not check_password_hash(password_hash, password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("home", auth="login"))
        user = User(user_data)
        login_user(user, remember=remember_me)
        flash("Welcome back!", "success")
        if user.role == "client":
            return redirect(url_for("client.dashboard"))
        if user.role == "freelancer":
            return redirect(url_for("freelancer.dashboard"))
        if user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("home"))
    return redirect(url_for("home", auth="login"))
# Register route
@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        role = request.form.get("role", "").strip().lower()
        terms = request.form.get("terms")
        if not full_name:
            flash("Please enter your full name.", "danger")
            return redirect(url_for("home", auth="register"))
        if not email:
            flash("Please enter your email address.", "danger")
            return redirect(url_for("home", auth="register"))
        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "danger")
            return redirect(url_for("home", auth="register"))
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("home", auth="register"))
        if role not in ["client", "freelancer"]:
            flash("Please select Client or Freelancer.", "danger")
            return redirect(url_for("home", auth="register"))
        if not terms:
            flash("Please accept the Terms of Service and Privacy Policy.", "danger")
            return redirect(url_for("home", auth="register"))
        db = get_db()
        existing_user = db.users.find_one({"email": email})
        if existing_user:
            flash("An account with this email already exists.", "warning")
            return redirect(url_for("home", auth="login"))
        user_data = {
            "full_name": full_name,
            "email": email,
            "password_hash": generate_password_hash(password),
            "role": role,
            "terms_accepted": True,
            "is_active": True,
            "auth_provider": "local",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        result = db.users.insert_one(user_data)
        user_data["_id"] = result.inserted_id
        user = User(user_data)
        login_user(user)
        flash("Account created successfully!", "success")
        if role == "client":
            return redirect(url_for("client.dashboard"))
        return redirect(url_for("freelancer.dashboard"))
    return redirect(url_for("home", auth="register"))
# Google login route
@auth.route("/google")
@auth.route("/login/google")
def google_login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    role = request.args.get("role", "client").strip().lower()
    if role not in ["client", "freelancer"]:
        role = "client"
    session["google_role"] = role
    google = current_app.extensions.get("google_oauth")
    if not google:
        flash("Google login is not configured correctly.", "danger")
        return redirect(url_for("home", auth="login"))
    redirect_uri = url_for("auth.google_callback", _external=True)
    return google.authorize_redirect(redirect_uri)
# Google callback route
@auth.route("/google/callback")
def google_callback():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    google = current_app.extensions.get("google_oauth")
    if not google:
        flash("Google login is not configured correctly.", "danger")
        return redirect(url_for("home", auth="login"))
    try:
        token = google.authorize_access_token()
        user_info = token.get("userinfo")
        if not user_info:
            user_info = google.userinfo()
        google_id = user_info.get("sub")
        email = user_info.get("email", "").strip().lower()
        full_name = user_info.get("name", "")
        profile_picture = user_info.get("picture", "")
        if not google_id or not email:
            flash("Unable to get your Google account information.", "danger")
            return redirect(url_for("home", auth="login"))
        role = session.pop("google_role", "client")
        if role not in ["client", "freelancer"]:
            role = "client"
        db = get_db()
        user_data = db.users.find_one({"email": email})
        if user_data:
            if not user_data.get("is_active", True):
                flash("Your account has been disabled.", "danger")
                return redirect(url_for("home", auth="login"))
            update_data = {
                "google_id": google_id,
                "profile_picture": profile_picture,
                "auth_provider": "google",
                "updated_at": datetime.now(timezone.utc)
            }
            if user_data.get("role") not in ["client", "freelancer", "admin"]:
                update_data["role"] = role
            db.users.update_one({"_id": user_data["_id"]}, {"$set": update_data})
            user_data.update(update_data)
        else:
            user_data = {
                "full_name": full_name or "Google User",
                "email": email,
                "google_id": google_id,
                "profile_picture": profile_picture,
                "password_hash": None,
                "role": role,
                "terms_accepted": True,
                "is_active": True,
                "auth_provider": "google",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            result = db.users.insert_one(user_data)
            user_data["_id"] = result.inserted_id
        user = User(user_data)
        login_user(user)
        flash("Successfully signed in with Google!", "success")
        if user.role == "client":
            return redirect(url_for("client.dashboard"))
        if user.role == "freelancer":
            return redirect(url_for("freelancer.dashboard"))
        if user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("home"))
    except Exception as error:
        print("Google login error:", error)
        flash("Google login failed. Please try again.", "danger")
        return redirect(url_for("home", auth="login"))
# Logout route
@auth.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))