from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database.mongodb import get_db
from bson.objectid import ObjectId

freelancer = Blueprint("freelancer", __name__)

@freelancer.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "freelancer":
        flash("Access denied.", "danger")
        return redirect(url_for("home"))
        
    db = get_db()
    user_id_str = current_user.id
    
    # Calculate actual stats from database
    active_projects = db.projects.count_documents({"freelancer_id": user_id_str, "status": "In Progress"})
    completed_projects = db.projects.count_documents({"freelancer_id": user_id_str, "status": "Completed"})
    
    # Example logic for teams and earnings
    teams_count = db.teams.count_documents({"members.user_id": user_id_str})
    
    # Assuming payments are stored with amount and freelancer_id
    payments = db.payments.find({"freelancer_id": user_id_str, "status": "Paid"})
    total_earnings = sum(p.get("amount", 0) for p in payments)
    
    user_data = db.users.find_one({"_id": ObjectId(user_id_str)})
    rating = user_data.get("rating", 0) if user_data else 0

    stats = {
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "teams_count": teams_count,
        "total_earnings": total_earnings,
        "rating": rating
    }

    recent_projects = list(db.projects.find({"freelancer_id": user_id_str}).sort("_id", -1).limit(5))

    return render_template("freelancer/dashboard.html", user=current_user, stats=stats, recent_projects=recent_projects)

@freelancer.route("/profile/setup", methods=["GET", "POST"])
@login_required
def profile_setup():
    if current_user.role != "freelancer":
        flash("Access denied.", "danger")
        return redirect(url_for("home"))
        
    if current_user.profile_completed:
        return redirect(url_for("freelancer.dashboard"))

    if request.method == "POST":
        db = get_db()
        
        skills = request.form.getlist("skills[]")
        
        # Experience
        exp_titles = request.form.getlist("exp_title[]")
        exp_companies = request.form.getlist("exp_company[]")
        exp_starts = request.form.getlist("exp_start[]")
        exp_ends = request.form.getlist("exp_end[]")
        exp_currents = request.form.getlist("exp_current[]")
        exp_descs = request.form.getlist("exp_desc[]")
        
        experiences = []
        for i in range(len(exp_titles)):
            if exp_titles[i]:
                experiences.append({
                    "title": exp_titles[i],
                    "company": exp_companies[i],
                    "start_date": exp_starts[i] if i < len(exp_starts) else "",
                    "end_date": exp_ends[i] if i < len(exp_ends) else "",
                    "current": str(i) in exp_currents,
                    "description": exp_descs[i] if i < len(exp_descs) else ""
                })
                
        # Portfolio
        port_titles = request.form.getlist("port_title[]")
        port_techs = request.form.getlist("port_tech[]")
        port_urls = request.form.getlist("port_url[]")
        port_descs = request.form.getlist("port_desc[]")
        
        portfolios = []
        for i in range(len(port_titles)):
            if port_titles[i]:
                portfolios.append({
                    "title": port_titles[i],
                    "technologies": port_techs[i] if i < len(port_techs) else "",
                    "url": port_urls[i] if i < len(port_urls) else "",
                    "description": port_descs[i] if i < len(port_descs) else ""
                })

        import os
        from werkzeug.utils import secure_filename
        from flask import current_app
        
        profile_data = {
            "professional_title": request.form.get("professional_title", ""),
            "location": request.form.get("location", ""),
            "bio": request.form.get("bio", ""),
            "availability": request.form.get("availability", "Available"),
            "hourly_rate": request.form.get("hourly_rate", ""),
            "skills": skills,
            "experiences": experiences,
            "portfolios": portfolios,
            "profile_completed": True
        }
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                unique_filename = f"{current_user.id}_{filename}"
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, unique_filename)
                file.save(file_path)
                profile_data['profile_picture'] = f"uploads/avatars/{unique_filename}"
        
        db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": profile_data}
        )
        
        current_user.profile_completed = True
        flash("Profile completed successfully!", "success")
        return redirect(url_for("freelancer.dashboard"))

    return render_template("freelancer/profile_setup.html", user=current_user)

@freelancer.route("/profile")
@login_required
def profile():
    if current_user.role != "freelancer":
        flash("Access denied.", "danger")
        return redirect(url_for("home"))
        
    db = get_db()
    user_data = db.users.find_one({"_id": ObjectId(current_user.id)})
    return render_template("freelancer/profile.html", user=current_user, user_data=user_data)

@freelancer.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if current_user.role != "freelancer":
        flash("Access denied.", "danger")
        return redirect(url_for("home"))
        
    db = get_db()
    if request.method == "POST":
        skills = request.form.getlist("skills[]")
        
        # Experience
        exp_titles = request.form.getlist("exp_title[]")
        exp_companies = request.form.getlist("exp_company[]")
        exp_starts = request.form.getlist("exp_start[]")
        exp_ends = request.form.getlist("exp_end[]")
        exp_currents = request.form.getlist("exp_current[]")
        exp_descs = request.form.getlist("exp_desc[]")
        
        experiences = []
        for i in range(len(exp_titles)):
            if exp_titles[i]:
                experiences.append({
                    "title": exp_titles[i],
                    "company": exp_companies[i],
                    "start_date": exp_starts[i] if i < len(exp_starts) else "",
                    "end_date": exp_ends[i] if i < len(exp_ends) else "",
                    "current": str(i) in exp_currents,
                    "description": exp_descs[i] if i < len(exp_descs) else ""
                })
                
        # Portfolio
        port_titles = request.form.getlist("port_title[]")
        port_techs = request.form.getlist("port_tech[]")
        port_urls = request.form.getlist("port_url[]")
        port_descs = request.form.getlist("port_desc[]")
        
        portfolios = []
        for i in range(len(port_titles)):
            if port_titles[i]:
                portfolios.append({
                    "title": port_titles[i],
                    "technologies": port_techs[i] if i < len(port_techs) else "",
                    "url": port_urls[i] if i < len(port_urls) else "",
                    "description": port_descs[i] if i < len(port_descs) else ""
                })

        import os
        from werkzeug.utils import secure_filename
        from flask import current_app
        
        profile_data = {
            "professional_title": request.form.get("professional_title", ""),
            "location": request.form.get("location", ""),
            "bio": request.form.get("bio", ""),
            "availability": request.form.get("availability", "Available"),
            "hourly_rate": request.form.get("hourly_rate", ""),
            "skills": skills,
            "experiences": experiences,
            "portfolios": portfolios
        }
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                unique_filename = f"{current_user.id}_{filename}"
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, unique_filename)
                file.save(file_path)
                profile_data['profile_picture'] = f"uploads/avatars/{unique_filename}"
        
        db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": profile_data}
        )
        
        flash("Profile updated successfully.", "success")
        return redirect(url_for("freelancer.profile"))

    user_data = db.users.find_one({"_id": ObjectId(current_user.id)})
    return render_template("freelancer/edit_profile.html", user=current_user, user_data=user_data)

@freelancer.route("/projects")
@login_required
def projects():
    if current_user.role != "freelancer":
        flash("Access denied.", "danger")
        return redirect(url_for("home"))
        
    db = get_db()
    # Find projects assigned to this freelancer
    all_projects = list(db.projects.find({"freelancer_id": current_user.id}).sort("_id", -1))
    
    active_projects = [p for p in all_projects if p.get("status") == "In Progress"]
    completed_projects = [p for p in all_projects if p.get("status") == "Completed"]

    return render_template("freelancer/projects.html", active_projects=active_projects, completed_projects=completed_projects)

@freelancer.route("/find-projects")
@login_required
def find_projects():
    if current_user.role != "freelancer":
        flash("Access denied.", "danger")
        return redirect(url_for("home"))
        
    db = get_db()
    # Find open projects
    open_projects = list(db.projects.find({"status": "Open"}).sort("_id", -1))
    
    return render_template("freelancer/find_projects.html", projects=open_projects)
