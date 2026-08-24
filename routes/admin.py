from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database.mongodb import get_db
from bson.objectid import ObjectId
import datetime
from functools import wraps

admin = Blueprint("admin", __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

@admin.route("/dashboard")
@login_required
@admin_required
def dashboard():
    db = get_db()
    
    total_users = db.users.count_documents({})
    total_clients = db.users.count_documents({"role": "client"})
    total_freelancers = db.users.count_documents({"role": "freelancer"})
    
    total_projects = db.projects.count_documents({})
    active_projects = db.projects.count_documents({"status": "In Progress"})
    completed_projects = db.projects.count_documents({"status": "Completed"})
    active_teams = db.teams.count_documents({})
    
    recent_users = list(db.users.find().sort("created_at", -1).limit(5))
    recent_projects = list(db.projects.find().sort("created_at", -1).limit(5))
    
    stats = {
        "total_users": total_users,
        "total_clients": total_clients,
        "total_freelancers": total_freelancers,
        "total_projects": total_projects,
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "active_teams": active_teams
    }
    
    return render_template("admin/dashboard.html", stats=stats, recent_users=recent_users, recent_projects=recent_projects)

@admin.route("/users")
@login_required
@admin_required
def users():
    db = get_db()
    role_filter = request.args.get("role")
    query = {}
    if role_filter in ["client", "freelancer", "admin"]:
        query["role"] = role_filter
        
    users_list = list(db.users.find(query).sort("created_at", -1))
    return render_template("admin/users.html", users=users_list, current_filter=role_filter)

@admin.route("/clients")
@login_required
@admin_required
def clients():
    db = get_db()
    clients_list = list(db.users.find({"role": "client"}).sort("created_at", -1))
    
    # Enrich with project counts
    for c in clients_list:
        c["project_count"] = db.projects.count_documents({"client_id": str(c["_id"])})
        
    return render_template("admin/clients.html", clients=clients_list)

@admin.route("/freelancers")
@login_required
@admin_required
def freelancers():
    db = get_db()
    freelancers_list = list(db.users.find({"role": "freelancer"}).sort("created_at", -1))
    return render_template("admin/freelancers.html", freelancers=freelancers_list)

@admin.route("/projects")
@login_required
@admin_required
def projects():
    db = get_db()
    status_filter = request.args.get("status")
    query = {}
    if status_filter:
        query["status"] = status_filter
        
    projects_list = list(db.projects.find(query).sort("created_at", -1))
    return render_template("admin/projects.html", projects=projects_list, current_filter=status_filter)

@admin.route("/project/<project_id>")
@login_required
@admin_required
def project_detail(project_id):
    db = get_db()
    try:
        project = db.projects.find_one({"_id": ObjectId(project_id)})
    except Exception:
        project = None
        
    if not project:
        flash("Project not found.", "danger")
        return redirect(url_for("admin.projects"))
        
    client_user = db.users.find_one({"_id": ObjectId(project.get("client_id"))}) if project.get("client_id") else None
        
    return render_template("admin/project_detail.html", project=project, client_user=client_user)

@admin.route("/project/<project_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_project(project_id):
    db = get_db()
    try:
        db.projects.delete_one({"_id": ObjectId(project_id)})
        flash("Project deleted successfully.", "success")
    except Exception:
        flash("Error deleting project.", "danger")
    return redirect(url_for("admin.projects"))

@admin.route("/user/<user_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_user(user_id):
    db = get_db()
    # Prevent admin from deactivating themselves
    if str(current_user.id) == str(user_id):
        flash("You cannot deactivate your own account.", "danger")
        return redirect(request.referrer or url_for("admin.users"))
        
    try:
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            new_status = not user.get("is_active", True)
            db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"is_active": new_status}})
            action = "activated" if new_status else "deactivated"
            flash(f"User {action} successfully.", "success")
    except Exception:
        flash("Error updating user status.", "danger")
        
    return redirect(request.referrer or url_for("admin.users"))

@admin.route("/user/<user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    db = get_db()
    # Prevent admin from deleting themselves
    if str(current_user.id) == str(user_id):
        flash("You cannot delete your own account.", "danger")
        return redirect(request.referrer or url_for("admin.users"))
        
    try:
        db.users.delete_one({"_id": ObjectId(user_id)})
        flash("User deleted successfully.", "success")
    except Exception:
        flash("Error deleting user.", "danger")
        
    return redirect(request.referrer or url_for("admin.users"))

@admin.route("/analytics")
@login_required
@admin_required
def analytics():
    db = get_db()
    
    # User distribution
    clients_count = db.users.count_documents({"role": "client"})
    freelancers_count = db.users.count_documents({"role": "freelancer"})
    admins_count = db.users.count_documents({"role": "admin"})
    
    # Project status distribution
    open_count = db.projects.count_documents({"status": "Open"})
    in_progress_count = db.projects.count_documents({"status": "In Progress"})
    completed_count = db.projects.count_documents({"status": "Completed"})
    
    data = {
        "user_distribution": [clients_count, freelancers_count, admins_count],
        "project_distribution": [open_count, in_progress_count, completed_count]
    }
    
    return render_template("admin/analytics.html", data=data)

@admin.route("/profile", methods=["GET", "POST"])
@login_required
@admin_required
def profile():
    db = get_db()
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        
        db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {"full_name": full_name, "email": email, "updated_at": datetime.datetime.utcnow()}}
        )
        flash("Profile updated successfully.", "success")
        return redirect(url_for("admin.profile"))
        
    admin_data = db.users.find_one({"_id": ObjectId(current_user.id)})
    return render_template("admin/profile.html", admin_data=admin_data)
