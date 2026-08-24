from flask import Blueprint, render_template
from flask_login import login_required, current_user

client = Blueprint("client", __name__)


@client.route("/dashboard")
@login_required
def dashboard():
    return render_template(
        "client/dashboard.html",
        user=current_user
    )


@client.route("/create-project")
@login_required
def create_project():
    return render_template(
        "client/create_project.html",
        user=current_user
    )


@client.route("/freelancers")
@login_required
def freelancers():
    return render_template(
        "client/freelancers.html",
        user=current_user
    )


@client.route("/freelancer/<int:freelancer_id>")
@login_required
def freelancer_profile(freelancer_id):

    freelancers_data = {
        1: {
            "name": "Sarah Johnson",
            "initials": "SJ",
            "role": "UI/UX Designer",
            "rating": "4.9",
            "reviews": "42",
            "experience": "5+ Years",
            "projects": "42",
            "rate": "$65/hr",
            "availability": "Available",
            "about": "Creating intuitive and scalable digital experiences with a focus on user needs and business goals.",
            "skills": [
                "Figma",
                "UX Research",
                "Design Systems",
                "Prototyping"
            ]
        },

        2: {
            "name": "Michael Thomas",
            "initials": "MT",
            "role": "React Developer",
            "rating": "4.8",
            "reviews": "35",
            "experience": "4 Years",
            "projects": "28",
            "rate": "$55/hr",
            "availability": "Available",
            "about": "Full-stack developer specializing in fast, responsive web applications using modern technologies.",
            "skills": [
                "React",
                "Node.js",
                "MongoDB",
                "TypeScript"
            ]
        },

        3: {
            "name": "David Rodriguez",
            "initials": "DR",
            "role": "Backend Developer",
            "rating": "4.9",
            "reviews": "56",
            "experience": "7 Years",
            "projects": "56",
            "rate": "$80/hr",
            "availability": "Busy",
            "about": "Backend architect specializing in scalable APIs, microservices, and database optimization.",
            "skills": [
                "Python",
                "Flask",
                "PostgreSQL",
                "AWS"
            ]
        },

        4: {
            "name": "Emily Chen",
            "initials": "EC",
            "role": "Data Scientist",
            "rating": "5.0",
            "reviews": "31",
            "experience": "6 Years",
            "projects": "34",
            "rate": "$90/hr",
            "availability": "Available",
            "about": "Helping businesses turn complex data into useful insights through machine learning and analytics.",
            "skills": [
                "Python",
                "Machine Learning",
                "AI",
                "TensorFlow"
            ]
        }
    }

    freelancer = freelancers_data.get(freelancer_id)

    if not freelancer:
        return "Freelancer not found", 404

    return render_template(
        "client/freelancer_profile.html",
        user=current_user,
        freelancer=freelancer
    )