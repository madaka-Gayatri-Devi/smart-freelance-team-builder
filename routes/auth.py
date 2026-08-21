from flask import Blueprint, render_template, request, redirect, url_for, flash, session  # Handles routes, forms, pages, and messages.
from flask_login import login_user, logout_user, current_user  # Handles user sessions.
from werkzeug.security import generate_password_hash, check_password_hash  # Secures user passwords.
from datetime import datetime, timezone  # Stores account creation time.
from database.mongodb import get_db  # Gives this file access to MongoDB.
from models.user import User  # Loads our User object.
import os
import requests
import secrets

auth = Blueprint("auth", __name__)  # Creates the authentication blueprint.

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:  # Checks whether the user is already logged in.
        return redirect(url_for("home"))  # Sends logged-in users to the homepage.
    if request.method == "POST":  # Runs this section when the login form is submitted.
        email = request.form.get("email", "").strip().lower()  # Gets and cleans the email.
        password = request.form.get("password", "")  # Gets the entered password.
        remember_me = request.form.get("remember_me") == "on"  # Checks the Remember Me option.
        if not email or not password:  # Checks that both fields were provided.
            flash("Please enter your email and password.", "danger")  # Shows an error message.
            return redirect(request.referrer or url_for("auth.login"))  # Returns to the login page.
        db = get_db()  # Gets our MongoDB database.
        user_data = db.users.find_one({"email": email})  # Searches for the user by email.
        if not user_data:  # Checks whether the email exists.
            flash("Invalid email or password.", "danger")  # Hides which login field was incorrect.
            return redirect(request.referrer or url_for("auth.login"))  # Returns to login.
        if not user_data.get("is_active", True):  # Checks whether the account is active.
            flash("Your account has been disabled.", "danger")  # Tells the user the account is disabled.
            return redirect(request.referrer or url_for("auth.login"))  # Returns to login.
        if not check_password_hash(user_data["password_hash"], password):  # Verifies the password.
            flash("Invalid email or password.", "danger")  # Shows an invalid-login message.
            return redirect(request.referrer or url_for("auth.login"))  # Returns to login.
        user = User(user_data)  # Creates a Flask-Login user object.
        login_user(user, remember=remember_me)  # Creates the user's login session.
        flash("Welcome back!", "success")  # Shows a successful login message.
        if user.role == "client":  # Checks whether the user is a client.
            return redirect(url_for("client.dashboard"))  # Sends the client to the client dashboard.
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
        full_name = request.form.get("full_name", "").strip()  # Gets the user's full name.
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
        if len(password) < 8:  # Requires a minimum eight-character password.
            flash("Password must contain at least 8 characters.", "danger")  # Shows a password message.
            return redirect(url_for("auth.register"))  # Returns to registration.
        if password != confirm_password:  # Checks that both passwords match.
            flash("Passwords do not match.", "danger")  # Shows a password mismatch message.
            return redirect(url_for("auth.register"))  # Returns to registration.
        if role not in ["client", "freelancer"]:  # Allows only the roles offered by your form.
            flash("Please select Client or Freelancer.", "danger")  # Shows a role validation message.
            return redirect(url_for("auth.register"))  # Returns to registration.
        if not terms:  # Checks whether the terms checkbox was selected.
            flash("Please accept the Terms of Service and Privacy Policy.", "danger")  # Shows a terms message.
            return redirect(url_for("auth.register"))  # Returns to registration.
        db = get_db()  # Gets our MongoDB database.
        existing_user = db.users.find_one({"email": email})  # Checks whether the email is already registered.
        if existing_user:  # Runs when the email already exists.
            flash("An account with this email already exists.", "warning")  # Shows a duplicate-account message.
            return redirect(url_for("auth.login"))  # Sends the user to login.
        user_data = {  # Creates the new user document.
            "full_name": full_name,  # Stores the user's name.
            "email": email,  # Stores the user's email.
            "password_hash": generate_password_hash(password),  # Stores only the hashed password.
            "role": role,  # Stores client or freelancer.
            "terms_accepted": True,  # Records that terms were accepted.
            "is_active": True,  # Enables the new account.
            "created_at": datetime.now(timezone.utc),  # Stores account creation time.
            "updated_at": datetime.now(timezone.utc)  # Stores the last update time.
        }
        result = db.users.insert_one(user_data)  # Saves the user to MongoDB.
        user_data["_id"] = result.inserted_id  # Adds MongoDB's generated ID to the user data.
        user = User(user_data)  # Creates the Flask-Login user object.
        login_user(user)  # Logs the newly registered user in.
        flash("Account created successfully!", "success")  # Shows a registration success message.
        if role == "client":  # Checks whether the new user is a client.
            return redirect(url_for("client.dashboard"))  # Sends the client to their dashboard.
        return redirect(url_for("freelancer.dashboard"))  # Sends the freelancer to their dashboard.
    return render_template("auth/register.html")  # Displays the registration page.
@auth.route("/logout")
def logout():
    logout_user()  # Removes the current user's login session.
    flash("You have been logged out.", "success")  # Shows a logout message.
    return redirect(url_for("home"))  # Returns the user to the homepage.

@auth.route("/login/google")
def google_login():
    role = request.args.get("role", "client")
    if role not in ["client", "freelancer"]:
        flash("Invalid role selected.", "danger")
        return redirect(url_for("auth.register"))
        
    session["oauth_state"] = secrets.token_urlsafe(16)
    session["oauth_role"] = role
    
    authorization_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
    redirect_uri = url_for("auth.google_callback", _external=True)
    
    request_uri = f"{authorization_endpoint}?client_id={GOOGLE_CLIENT_ID}&redirect_uri={redirect_uri}&response_type=code&scope=openid email profile&state={session['oauth_state']}"
    return redirect(request_uri)

@auth.route("/login/google/callback")
def google_callback():
    state = request.args.get("state")
    if state is None or state != session.get("oauth_state"):
        flash("Invalid OAuth state. Please try again.", "danger")
        return redirect(url_for("auth.login"))
        
    code = request.args.get("code")
    if not code:
        flash("Google authentication failed.", "danger")
        return redirect(url_for("auth.login"))
        
    token_endpoint = "https://oauth2.googleapis.com/token"
    redirect_uri = url_for("auth.google_callback", _external=True)
    
    token_response = requests.post(
        token_endpoint,
        data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
    )
    
    if not token_response.ok:
        flash("Failed to fetch token from Google.", "danger")
        return redirect(url_for("auth.login"))
        
    tokens = token_response.json()
    access_token = tokens.get("access_token")
    
    userinfo_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"
    userinfo_response = requests.get(
        userinfo_endpoint,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    
    if userinfo_response.ok:
        user_info = userinfo_response.json()
        email = user_info.get("email")
        name = user_info.get("name")
        
        db = get_db()
        user_data = db.users.find_one({"email": email})
        
        if not user_data:
            role = session.get("oauth_role", "client")
            new_user = {
                "full_name": name,
                "email": email,
                "password_hash": "",
                "role": role,
                "terms_accepted": True,
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            result = db.users.insert_one(new_user)
            new_user["_id"] = result.inserted_id
            user_data = new_user
            flash("Successfully created account with Google.", "success")
            
        user = User(user_data)
        login_user(user)
        
        if user.role == "client":
            return redirect(url_for("client.dashboard"))
        elif user.role == "freelancer":
            return redirect(url_for("freelancer.dashboard"))
        elif user.role == "admin":
            return redirect(url_for("admin.dashboard"))
            
    flash("Google authentication failed.", "danger")
    return redirect(url_for("auth.login"))