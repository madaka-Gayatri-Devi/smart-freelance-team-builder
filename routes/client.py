from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database.mongodb import get_db
from bson.objectid import ObjectId
import datetime

client = Blueprint("client", __name__)

@client.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "client":
        flash("Access denied.", "danger")
        return redirect(url_for("home"))
        
    db = get_db()
    user_id_str = current_user.id
    
    # Calculate actual stats from database
    active_projects = db.projects.count_documents({"client_id": user_id_str, "status": "In Progress"})
    completed_projects = db.projects.count_documents({"client_id": user_id_str, "status": "Completed"})
    teams_count = db.teams.count_documents({"client_id": user_id_str})
    
    payments = db.payments.find({"client_id": user_id_str, "status": "Paid"})
    total_spent = sum(p.get("amount", 0) for p in payments)
    
    stats = {
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "teams_count": teams_count,
        "total_spent": total_spent
    }
    
    projects = list(db.projects.find({"client_id": user_id_str}).sort("_id", -1).limit(5))
    
    recommended_freelancers = []
    if projects:
        # Simplistic recommendation: just fetch some real freelancers who have completed profiles
        # (Could be expanded later to match actual project skills)
        recommended_freelancers = list(db.users.find({"role": "freelancer", "profile_completed": True}).limit(3))
        
    # Derive recent activity from projects
    recent_activity = []
    for p in projects[:3]:
        recent_activity.append({
            "type": "Project Created",
            "title": f"You created the project '{p.get('title')}'",
            "date": p.get("created_at", datetime.datetime.utcnow()).strftime("%b %d, %Y") if hasattr(p.get("created_at"), "strftime") else "Recently"
        })
    
    return render_template("client/dashboard.html", user=current_user, stats=stats, projects=projects, recommended_freelancers=recommended_freelancers, recent_activity=recent_activity)

@client.route("/projects")
@login_required
def projects():
    if current_user.role != "client":
        flash("Access denied.", "danger")
        return redirect(url_for("home"))
        
    db = get_db()
    user_id_str = current_user.id
    
    all_projects = list(db.projects.find({"client_id": user_id_str}).sort("_id", -1))
    
    open_projects = [p for p in all_projects if p.get("status") == "Open"]
    active_projects = [p for p in all_projects if p.get("status") == "In Progress"]
    completed_projects = [p for p in all_projects if p.get("status") == "Completed"]
    
    return render_template("client/projects.html", 
                          open_projects=open_projects, 
                          active_projects=active_projects, 
                          completed_projects=completed_projects)

@client.route("/projects/new", methods=["GET", "POST"])
@login_required
def new_project():
    if current_user.role != "client":
        flash("Access denied.", "danger")
        return redirect(url_for("home"))
        
    if request.method == "POST":
        import os
        from werkzeug.utils import secure_filename
        from flask import current_app
        
        db = get_db()
        
        title = request.form.get("title")
        category = request.form.get("category")
        experience_level = request.form.get("experience_level")
        description = request.form.get("description")
        
        budget_type = request.form.get("budget_type")
        budget = request.form.get("budget") if budget_type == "Fixed Price" else None
        budget_min = request.form.get("budget_min") if budget_type == "Hourly Rate" else None
        budget_max = request.form.get("budget_max") if budget_type == "Hourly Rate" else None
        
        deadline = request.form.get("deadline")
        duration = request.form.get("duration")
        
        skills = request.form.getlist("skills[]")
        work_type = request.form.get("work_type")
        team_size = request.form.get("team_size")
        
        # Remove empty deliverables
        deliverables_raw = request.form.getlist("deliverables[]")
        deliverables = [d for d in deliverables_raw if d.strip()]
        
        preferred_start_date = request.form.get("preferred_start_date")
        
        if not title or not description or not category or not experience_level:
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for("client.new_project"))
            
        project_data = {
            "title": title,
            "category": category,
            "experience_level": experience_level,
            "description": description,
            "budget_type": budget_type,
            "budget": budget,
            "budget_min": budget_min,
            "budget_max": budget_max,
            "deadline": deadline,
            "duration": duration,
            "skills": skills,
            "work_type": work_type,
            "team_size": team_size,
            "deliverables": deliverables,
            "preferred_start_date": preferred_start_date,
            "status": "Open",
            "client_id": current_user.id,
            "client_name": current_user.full_name,
            "freelancer_id": None,
            "created_at": datetime.datetime.utcnow(),
            "attachments": []
        }
        
        # Handle file attachments
        if 'attachments' in request.files:
            files = request.files.getlist('attachments')
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'projects')
            os.makedirs(upload_folder, exist_ok=True)
            
            for file in files:
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    # use timestamp to ensure uniqueness
                    unique_filename = f"{datetime.datetime.now().strftime('%Y%md%H%M%S')}_{current_user.id}_{filename}"
                    file_path = os.path.join(upload_folder, unique_filename)
                    file.save(file_path)
                    project_data["attachments"].append({
                        "filename": filename,
                        "path": f"uploads/projects/{unique_filename}"
                    })
        
        db.projects.insert_one(project_data)
        flash("Project created successfully!", "success")
        return redirect(url_for("client.dashboard"))
        
    return render_template("client/create_project.html")

@client.route("/project/<project_id>")
@login_required
def view_project(project_id):
    if current_user.role != "client":
        flash("Access denied.", "danger")
        return redirect(url_for("home"))
        
    db = get_db()
    try:
        project = db.projects.find_one({"_id": ObjectId(project_id), "client_id": current_user.id})
    except:
        project = None
        
    if not project:
        flash("Project not found.", "danger")
        return redirect(url_for("client.projects"))
        
    return render_template("client/view_project.html", project=project)

@client.route("/find-freelancers")
@login_required
def find_freelancers():
    if current_user.role != "client":
        flash("Access denied.", "danger")
        return redirect(url_for("home"))
        
    db = get_db()
    # Fetch freelancers who have completed their profiles
    freelancers = list(db.users.find({"role": "freelancer", "profile_completed": True}))
    
    return render_template("client/find_freelancers.html", freelancers=freelancers)

@client.route("/freelancer/<freelancer_id>")
@login_required
def view_freelancer(freelancer_id):
    if current_user.role != "client":
        flash("Access denied.", "danger")
        return redirect(url_for("home"))
        
    db = get_db()
    try:
        freelancer = db.users.find_one({"_id": ObjectId(freelancer_id), "role": "freelancer"})
    except:
        freelancer = None
        
    if not freelancer:
        flash("Freelancer not found.", "danger")
        return redirect(url_for("client.find_freelancers"))
        
    return render_template("client/view_freelancer.html", freelancer=freelancer)

@client.route("/profile")
@login_required
def profile():
    if current_user.role != "client":
        flash("Access denied.", "danger")
        return redirect(url_for("home"))
        
    db = get_db()
    user_data = db.users.find_one({"_id": ObjectId(current_user.id)})
    return render_template("client/profile.html", user=current_user, user_data=user_data)

@client.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if current_user.role != "client":
        flash("Access denied.", "danger")
        return redirect(url_for("home"))
        
    db = get_db()
    
    if request.method == "POST":
        import os
        from werkzeug.utils import secure_filename
        from flask import current_app
        
        company_name = request.form.get("company_name", "")
        industry = request.form.get("industry", "")
        company_website = request.form.get("company_website", "")
        company_size = request.form.get("company_size", "")
        location = request.form.get("location", "")
        phone = request.form.get("phone", "")
        bio = request.form.get("bio", "")
        
        profile_data = {
            "company_name": company_name,
            "industry": industry,
            "company_website": company_website,
            "company_size": company_size,
            "location": location,
            "phone": phone,
            "bio": bio,
            "profile_completed": True
        }
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                # create a unique filename to prevent overwrites
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
        
        flash("Profile updated successfully!", "success")
        return redirect(url_for("client.profile"))
        
    user_data = db.users.find_one({"_id": ObjectId(current_user.id)})
    return render_template("client/edit_profile.html", user=current_user, user_data=user_data)

@client.route("/profile/delete", methods=["POST"])
@login_required
def delete_profile():
    if current_user.role != "client":
        flash("Access denied.", "danger")
        return redirect(url_for("home"))
        
    db = get_db()
    # Delete the user
    db.users.delete_one({"_id": ObjectId(current_user.id)})
    
    # Alternatively we could delete projects too, but leaving them might be safer depending on business logic, 
    # but the instructions said "Remove or appropriately handle associated profile data."
    db.projects.delete_many({"client_id": current_user.id})
    
    from flask_login import logout_user
    logout_user()
    
    flash("Your account has been deleted.", "info")
    return redirect(url_for("home"))
