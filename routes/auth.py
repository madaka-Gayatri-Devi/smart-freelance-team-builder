from flask import Blueprint, render_template, redirect, url_for, flash, request
from models import db
from models.user import User
from flask_login import login_user, logout_user, current_user
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash('Invalid email or password', 'error')
            return redirect(url_for('index', auth='login'))
            
        login_user(user, remember=request.form.get('remember_me'))
        
        if user.role == 'client':
            return redirect(url_for('client_dashboard'))
        elif user.role == 'freelancer':
            return redirect(url_for('freelancer_dashboard'))
        elif user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
            
    return redirect(url_for('index', auth='login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        terms = request.form.get('terms')
        
        # Validation
        errors = []
        if not full_name or not email or not password or not role:
            errors.append("All fields are required.")
        if password != confirm_password:
            errors.append("Passwords must match.")
        if not terms:
            errors.append("You must agree to the Terms of Service.")
        if role not in ['client', 'freelancer']:
            errors.append("Invalid role selected.")
        
        # Email validation
        email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
        if not email_regex.match(email):
            errors.append("Invalid email format.")
            
        if User.query.filter_by(email=email).first():
            errors.append("Please use a different email address.")
            
        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('index', auth='register'))
            
        user = User(full_name=full_name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Congratulations, you are now a registered user!', 'success')
        login_user(user)
        
        if user.role == 'client':
            return redirect(url_for('client_dashboard'))
        elif user.role == 'freelancer':
            return redirect(url_for('freelancer_dashboard'))
            
    return redirect(url_for('index', auth='register'))

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
