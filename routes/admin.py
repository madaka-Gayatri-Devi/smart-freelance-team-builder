from flask import Blueprint, render_template
from flask_login import login_required, current_user

admin = Blueprint("admin", __name__)

@admin.route("/dashboard")
@login_required
def dashboard():
    return render_template("client/dashboard.html", user=current_user)
