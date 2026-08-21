from flask_login import UserMixin  # Provides Flask-Login's required user methods.
class User(UserMixin):
    def __init__(self, user_data):
        self.data = user_data  # Stores the complete MongoDB user document.
        self.id = str(user_data["_id"])  # Converts MongoDB ObjectId into a string for Flask-Login.
        self.full_name = user_data.get("full_name", "")  # Gets the user's full name.
        self.email = user_data.get("email", "")  # Gets the user's email.
        self.role = user_data.get("role", "")  # Gets the user's role.
        self.is_active = user_data.get("is_active", True)  # Checks whether the account is active.
    def get_id(self):
        return self.id  # Returns the user's ID to Flask-Login.