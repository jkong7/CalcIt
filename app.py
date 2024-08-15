from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Needed for session management
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if not logged in

# Update the User model to add a relationship with HandoutProgress
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    # New relationship: one user can have many handout progress records
    handout_progress = db.relationship('HandoutProgress', backref='user', lazy=True)

class Handout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)

class HandoutProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    handout_id = db.Column(db.Integer, db.ForeignKey('handout.id'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)  # Track if the handout is completed

with app.app_context():
    db.create_all()

def initialize_handouts():
    handouts = [
        "Definition of the Derivative",
        "Derivative Properties",
        "The Chain Rule",
        "Implicit Differentiation"
        # Add more handouts here if needed
    ]
    for title in handouts:
        existing_handout = Handout.query.filter_by(title=title).first()
        if not existing_handout:
            new_handout = Handout(title=title)
            db.session.add(new_handout)
    db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    # Check if the email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return "Email already registered. Please use a different email."

    # Create a new user and add to the database
    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return "Registration successful!"

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()

    if user and user.password == password:
        login_user(user)
        return redirect(url_for('main'))  # Redirect back to the home page
    else:
        return "Login failed. Check your email and password."

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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))  # Redirect to the main page after logging out

@app.route('/handout/<int:handout_id>')
@login_required
def handout(handout_id):
    # For now, use placeholder data; later, this can be fetched from a database
    handouts = {
        1: {"title": "Handout 1", "description": "Description for Handout 1", "key_concepts": ["Concept A", "Concept B"], "image": "handout1.png"},
        2: {"title": "Handout 2", "description": "Description for Handout 2", "key_concepts": ["Concept C", "Concept D"], "image": "handout2.png"},
        # Add more handouts as needed
    }
    
    handout_data = handouts.get(handout_id, None)
    
    if not handout_data:
        return "Handout not found", 404

    return render_template('handout.html', handout=handout_data)

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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create the database and tables
        initialize_handouts()  # Initialize the handout data
    app.run(debug=True, port=5001)
