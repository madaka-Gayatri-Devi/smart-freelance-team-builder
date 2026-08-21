from flask import Blueprint, render_template
from flask_login import login_required, current_user

client = Blueprint("client", __name__)

@client.route("/dashboard")
@login_required
def dashboard():
    return render_template("client/dashboard.html", user=current_user)
