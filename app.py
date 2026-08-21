from flask import Flask, render_template, redirect, url_for
from config import Config
from models import db
from models.user import User
from routes.auth import auth_bp
from flask_login import LoginManager, login_required, current_user

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp)

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/client/dashboard')
@login_required
def client_dashboard():
    if current_user.role != 'client':
        return redirect(url_for('index'))
    return render_template('client/dashboard.html')

@app.route('/freelancer/dashboard')
@login_required
def freelancer_dashboard():
    if current_user.role != 'freelancer':
        return redirect(url_for('index'))
    return render_template('freelancer/dashboard.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    return render_template('admin/dashboard.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
