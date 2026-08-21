from flask import Blueprint, render_template
from flask_login import login_required, current_user

freelancer = Blueprint("freelancer", __name__)

@freelancer.route("/dashboard")
@login_required
def dashboard():
    return render_template("client/dashboard.html", user=current_user)
