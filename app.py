from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# ------------------ Importing Handout Data ------------------
from handout_data import handouts

# ------------------ Flask Application Setup ------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Needed for session management

# ------------------ Database Setup ------------------
db = SQLAlchemy(app)

# ------------------ Flask-Login Manager Setup ------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if not logged in

# ------------------ User Model ------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    handout_progress = db.relationship('HandoutProgress', backref='user', lazy=True)

# ------------------ Handout Model ------------------
class Handout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)

# ------------------ Handout Progress Model ------------------
class HandoutProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    handout_id = db.Column(db.Integer, db.ForeignKey('handout.id'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)  # Track if the handout is completed

# ------------------ Database Initialization ------------------
with app.app_context():
    db.create_all()


# ------------------ User Loader for Flask-Login ------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------------ Main Route ------------------
@app.route('/')
def main():
    if current_user.is_authenticated:
        # Get the progress for the current user
        progress = HandoutProgress.query.filter_by(user_id=current_user.id).all()

        # Create a dictionary to store the progress
        user_progress = {p.handout_id: p.is_completed for p in progress}
    else:
        user_progress = {}  # Default to empty dictionary for logged-out users

    # Get all handouts
    handouts = Handout.query.all()

    return render_template('main.html', handouts=handouts, user_progress=user_progress)

# ------------------ Registration Route ------------------
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    # Check if the email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash("Email already registered. Please use a different email.", "error")
        return redirect(url_for('main'))

    # Create a new user and add to the database
    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    flash("Registration successful!", "success")
    return redirect(url_for('main'))

# ------------------ Login Route ------------------
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()

    if user and user.password == password:
        login_user(user)
        flash("Login successful!", "success")
        return redirect(url_for('main'))
    else:
        flash("Login failed. Check your email and password.", "error")
        return redirect(url_for('main'))

# ------------------ Dashboard Route ------------------
@app.route('/dashboard')
@login_required
def dashboard():
    # Get the progress for the current user
    progress = HandoutProgress.query.filter_by(user_id=current_user.id).all()

    # Create a dictionary to store the progress
    progress_dict = {p.handout_id: p.is_completed for p in progress}

    # Get all handouts
    handouts = Handout.query.all()

    return render_template('dashboard.html', handouts=handouts, progress=progress_dict)

# ------------------ Logout Route ------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))  # Redirect to the main page after logging out

# ------------------ Handout Route ------------------
@app.route('/handout/<int:handout_id>')
@login_required
def handout(handout_id):
    # Fetch the handout data
    handout_data = handouts.get(handout_id, None)

    if not handout_data:
        return "Handout not found", 404

    return render_template('handout.html', handout=handout_data, handout_id=handout_id)

# ------------------ Update Progress Route ------------------
@app.route('/update_progress', methods=['POST'])
@login_required
def update_progress():
    data = request.get_json()
    handout_id = data.get('handout_id')
    is_completed = data.get('is_completed')

    # Check if progress already exists
    progress = HandoutProgress.query.filter_by(user_id=current_user.id, handout_id=handout_id).first()

    if progress:
        progress.is_completed = is_completed
    else:
        progress = HandoutProgress(user_id=current_user.id, handout_id=handout_id, is_completed=is_completed)
        db.session.add(progress)

    db.session.commit()

    return {"message": "Progress updated successfully"}

# ------------------ Main Execution ------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create the database and tables
    app.run(debug=True, port=5001)
