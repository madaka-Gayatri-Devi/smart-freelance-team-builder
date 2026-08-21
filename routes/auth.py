from flask import Blueprint, render_template, request, redirect, url_for, flash, session  # Handles routes, pages, forms, and OAuth session data.
from flask_login import login_user, logout_user, current_user  # Handles user login sessions.
from werkzeug.security import generate_password_hash, check_password_hash  # Secures passwords.
from datetime import datetime, timezone  # Stores account timestamps.
from database.mongodb import get_db  # Gives this file access to MongoDB.
from models.user import User  # Loads our Flask-Login User model.
from bson import ObjectId  # Handles MongoDB IDs.
from flask import current_app  # Gives access to the Flask application.
auth = Blueprint("auth", __name__)  # Creates the authentication blueprint.
@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:  # Checks whether the user is already logged in.
        return redirect(url_for("home"))  # Sends logged-in users to the homepage.
    if request.method == "POST":  # Runs when the login form is submitted.
        email = request.form.get("email", "").strip().lower()  # Gets and cleans the email.
        password = request.form.get("password", "")  # Gets the password.
        remember_me = request.form.get("remember_me") == "on"  # Checks Remember Me.
        if not email or not password:  # Checks that both fields were provided.
            flash("Please enter your email and password.", "danger")  # Shows an error message.
            return redirect(url_for("auth.login"))  # Returns to login.
        db = get_db()  # Gets our MongoDB database.
        user_data = db.users.find_one({"email": email})  # Searches for the user by email.
        if not user_data:  # Checks whether the user exists.
            flash("Invalid email or password.", "danger")  # Shows an invalid-login message.
            return redirect(url_for("auth.login"))  # Returns to login.
        if not user_data.get("is_active", True):  # Checks whether the account is active.
            flash("Your account has been disabled.", "danger")  # Shows an account-disabled message.
            return redirect(url_for("auth.login"))  # Returns to login.
        if not check_password_hash(user_data["password_hash"], password):  # Verifies the password.
            flash("Invalid email or password.", "danger")  # Shows an invalid-login message.
            return redirect(url_for("auth.login"))  # Returns to login.
        user = User(user_data)  # Creates a Flask-Login user object.
        login_user(user, remember=remember_me)  # Creates the login session.
        flash("Welcome back!", "success")  # Shows a successful login message.
        if user.role == "client":  # Checks whether the user is a client.
            return redirect(url_for("client.dashboard"))  # Sends the client to their dashboard.
        if user.role == "freelancer":  # Checks whether the user is a freelancer.
            return redirect(url_for("freelancer.dashboard"))  # Sends the freelancer to their dashboard.
        if user.role == "admin":  # Checks whether the user is an admin.
            return redirect(url_for("admin.dashboard"))  # Sends the admin to their dashboard.
        return redirect(url_for("home"))  # Fallback for an unknown role.
    return render_template("auth/login.html")  # Displays the login page.
@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:  # Checks whether the user is already logged in.
        return redirect(url_for("home"))  # Sends logged-in users to the homepage.
    if request.method == "POST":  # Runs when the registration form is submitted.
        full_name = request.form.get("full_name", "").strip()  # Gets the full name.
        email = request.form.get("email", "").strip().lower()  # Gets and cleans the email.
        password = request.form.get("password", "")  # Gets the password.
        confirm_password = request.form.get("confirm_password", "")  # Gets the confirmation password.
        role = request.form.get("role", "").strip().lower()  # Gets the selected role.
        terms = request.form.get("terms")  # Checks whether terms were accepted.
        if not full_name:  # Checks whether a name was entered.
            flash("Please enter your full name.", "danger")  # Shows a validation message.
            return redirect(url_for("auth.register"))  # Returns to registration.
        if not email:  # Checks whether an email was entered.
            flash("Please enter your email address.", "danger")  # Shows a validation message.
            return redirect(url_for("auth.register"))  # Returns to registration.
        if len(password) < 8:  # Requires at least eight characters.
            flash("Password must contain at least 8 characters.", "danger")  # Shows a password message.
            return redirect(url_for("auth.register"))  # Returns to registration.
        if password != confirm_password:  # Checks that both passwords match.
            flash("Passwords do not match.", "danger")  # Shows a mismatch message.
            return redirect(url_for("auth.register"))  # Returns to registration.
        if role not in ["client", "freelancer"]:  # Allows only the roles offered by the form.
            flash("Please select Client or Freelancer.", "danger")  # Shows a role message.
            return redirect(url_for("auth.register"))  # Returns to registration.
        if not terms:  # Checks whether terms were accepted.
            flash("Please accept the Terms of Service and Privacy Policy.", "danger")  # Shows a terms message.
            return redirect(url_for("auth.register"))  # Returns to registration.
        db = get_db()  # Gets our MongoDB database.
        existing_user = db.users.find_one({"email": email})  # Checks for an existing account.
        if existing_user:  # Runs when the email already exists.
            flash("An account with this email already exists.", "warning")  # Shows a duplicate-account message.
            return redirect(url_for("auth.login"))  # Sends the user to login.
        user_data = {
            "full_name": full_name,  # Stores the user's name.
            "email": email,  # Stores the user's email.
            "password_hash": generate_password_hash(password),  # Stores the hashed password.
            "role": role,  # Stores the selected role.
            "terms_accepted": True,  # Records terms acceptance.
            "is_active": True,  # Enables the account.
            "auth_provider": "local",  # Identifies this as a normal password account.
            "created_at": datetime.now(timezone.utc),  # Stores account creation time.
            "updated_at": datetime.now(timezone.utc)  # Stores account update time.
        }
        result = db.users.insert_one(user_data)  # Saves the user to MongoDB.
        user_data["_id"] = result.inserted_id  # Adds MongoDB's generated ID.
        user = User(user_data)  # Creates the Flask-Login user object.
        login_user(user)  # Logs the newly registered user in.
        flash("Account created successfully!", "success")  # Shows registration success.
        if role == "client":  # Checks whether the user is a client.
            return redirect(url_for("client.dashboard"))  # Sends the client to the dashboard.
        return redirect(url_for("freelancer.dashboard"))  # Sends the freelancer to the dashboard.
    return render_template("auth/register.html")  # Displays the registration page.
@auth.route("/google")
def google_login():
    if current_user.is_authenticated:  # Checks whether the user is already logged in.
        return redirect(url_for("home"))  # Sends logged-in users to the homepage.
    google = current_app.extensions["google_oauth"]  # Gets the Google OAuth client.
    redirect_uri = url_for(
        "auth.google_callback",
        _external=True
    )  # Creates the Google callback URL.
    return google.authorize_redirect(
        redirect_uri
    )  # Redirects the user to Google's login page.
@auth.route("/google/callback")
def google_callback():
    if current_user.is_authenticated:  # Checks whether the user is already logged in.
        return redirect(url_for("home"))  # Sends logged-in users to the homepage.
    google = current_app.extensions["google_oauth"]  # Gets the Google OAuth client.
    try:
        token = google.authorize_access_token()  # Exchanges Google's authorization code for tokens.
        user_info = token.get("userinfo")  # Gets the user's Google profile information.
        if not user_info:  # Checks whether Google returned user information.
            user_info = google.userinfo()  # Requests the user information from Google.
        google_id = user_info.get("sub")  # Gets Google's unique user ID.
        email = user_info.get("email", "").lower()  # Gets the Google account email.
        full_name = user_info.get("name", "")  # Gets the user's Google profile name.
        profile_picture = user_info.get("picture", "")  # Gets the user's Google profile picture.
        if not google_id or not email:  # Makes sure required Google information exists.
            flash("Unable to get your Google account information.", "danger")  # Shows an error.
            return redirect(url_for("home"))  # Returns to the homepage.
        db = get_db()  # Gets our MongoDB database.
        user_data = db.users.find_one(
            {"email": email}
        )  # Searches for an existing account using the Google email.
        if user_data:  # Runs when the email already exists.
            update_data = {
                "google_id": google_id,  # Stores the Google account ID.
                "profile_picture": profile_picture,  # Updates the profile picture.
                "updated_at": datetime.now(timezone.utc)  # Updates the account timestamp.
            }
            db.users.update_one(
                {"_id": user_data["_id"]},
                {"$set": update_data}
            )  # Updates the existing account.

            user_data.update(update_data)  # Updates the local user data.
        else:
            user_data = {
                "full_name": full_name or "Google User",  # Stores the Google user's name.
                "email": email,  # Stores the Google email.
                "google_id": google_id,  # Stores Google's unique user ID.
                "profile_picture": profile_picture,  # Stores the Google profile picture.
                "password_hash": None,  # Google users do not need a local password.
                "role": "client",  # Uses client as the default role for new Google accounts.
                "terms_accepted": True,  # Records account creation through Google.
                "is_active": True,  # Enables the account.
                "auth_provider": "google",  # Identifies this as a Google account.
                "created_at": datetime.now(timezone.utc),  # Stores account creation time.
                "updated_at": datetime.now(timezone.utc)  # Stores account update time.
            }
            result = db.users.insert_one(
                user_data
            )  # Creates the new Google user.
            user_data["_id"] = result.inserted_id  # Adds MongoDB's generated ID.
        user = User(user_data)  # Creates the Flask-Login user object.
        login_user(user)  # Creates the login session.
        flash("Successfully signed in with Google!", "success")  # Shows a success message.
        if user.role == "client":  # Checks whether the user is a client.
            return redirect(url_for("client.dashboard"))  # Sends the client to the dashboard.
        if user.role == "freelancer":  # Checks whether the user is a freelancer.
            return redirect(url_for("freelancer.dashboard"))  # Sends the freelancer to the dashboard.
        if user.role == "admin":  # Checks whether the user is an admin.
            return redirect(url_for("admin.dashboard"))  # Sends the admin to the dashboard.
        return redirect(url_for("home"))  # Fallback redirect.
    except Exception as error:
        print("Google login error:", error)  # Prints the OAuth error for debugging.
        flash("Google login failed. Please try again.", "danger")  # Shows a user-friendly error.
        return redirect(url_for("home"))  # Returns to the homepage.
@auth.route("/logout")
def logout():
    logout_user()  # Removes the current user's login session.
    flash("You have been logged out.", "success")  # Shows a logout message.
    return redirect(url_for("home"))  # Returns the user to the homepage.