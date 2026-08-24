import os
import sys
from getpass import getpass
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone
from dotenv import load_dotenv
from database.mongodb import init_db, get_db
import click

# Load environment variables
load_dotenv()

@click.command()
@click.option('--name', prompt='Full Name', help='Full name of the admin')
@click.option('--email', prompt='Email Address', help='Email of the admin')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Password')
def create_admin(name, email, password):
    """Create the initial admin user."""
    click.echo("--- Create Admin User ---")
    
    email = email.strip().lower()
    
    if len(password) < 8:
        click.secho("Password must be at least 8 characters long. Aborting.", fg="red")
        sys.exit(1)
        
    # Initialize DB connection
    init_db()
    db = get_db()
    
    # Check if user exists
    existing_user = db.users.find_one({"email": email})
    if existing_user:
        click.secho(f"A user with email {email} already exists.", fg="red")
        sys.exit(1)
        
    # Create user
    user_data = {
        "full_name": name,
        "email": email,
        "password_hash": generate_password_hash(password),
        "role": "admin",
        "terms_accepted": True,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    try:
        db.users.insert_one(user_data)
        click.secho(f"Admin user '{email}' created successfully!", fg="green")
    except Exception as e:
        click.secho(f"Error creating admin user: {str(e)}", fg="red")

if __name__ == "__main__":
    create_admin()
