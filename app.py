import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# ------------------ Importing Handout Data ------------------
from handout_data import handouts

# ------------------ Flask Application Setup ------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'AKPAKP' 

# ------------------ PostgreSQL Connection Setup ------------------
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="Postgresql DB",
        user="postgres",
        password="Geobobo77$"
    )
    return conn

# ------------------ Flask-Login Manager Setup ------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if not logged in

# ------------------ User Loader for Flask-Login ------------------
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, username, email FROM user WHERE id = %s', (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        user_obj = UserMixin()
        user_obj.id = user[0]
        user_obj.username = user[1]
        user_obj.email = user[2]
        return user_obj
    return None

# ------------------ Main Route ------------------
@app.route('/')
def main():
    user_progress = {}

    if current_user.is_authenticated:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT handout_id, is_completed FROM handout_progress WHERE user_id = %s', (current_user.id,))
        progress = cur.fetchall()
        cur.close()
        conn.close()

        user_progress = {p[0]: p[1] for p in progress}

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, title FROM handouts')
    handouts = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('main.html', handouts=handouts, user_progress=user_progress)

# ------------------ Registration Route ------------------
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id FROM users WHERE email = %s', (email,))
    existing_user = cur.fetchone()

    if existing_user:
        flash("Email already registered. Please use a different email.", "error")
        cur.close()
        conn.close()
        return redirect(url_for('main'))

    cur.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)',
                (username, email, password))
    conn.commit()
    cur.close()
    conn.close()

    flash("Registration successful!", "success")
    return redirect(url_for('main'))

# ------------------ Login Route ------------------
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, password FROM users WHERE email = %s', (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and user[1] == password:
        user_obj = UserMixin()
        user_obj.id = user[0]
        login_user(user_obj)
        flash("Login successful!", "success")
        return redirect(url_for('main'))
    else:
        flash("Login failed. Check your email and password.", "error")
        return redirect(url_for('main'))

# ------------------ Logout Route ------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))  

# ------------------ Handout Route ------------------
@app.route('/handout/<int:handout_id>')
@login_required
def handout(handout_id):
    handout_data = handouts.get(handout_id, None)
    if not handout_data:
        return "Handout not found", 404

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE users SET last_handout_viewed = %s WHERE id = %s', (handout_id, current_user.id))
    conn.commit()
    cur.close()
    conn.close()

    return render_template('handout.html', handout=handout_data, handout_id=handout_id)

# ------------------ Update Progress Route ------------------
@app.route('/update_progress', methods=['POST'])
@login_required
def update_progress():
    data = request.get_json()
    handout_id = data.get('handout_id')
    is_completed = data.get('is_completed')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id FROM handout_progress WHERE user_id = %s AND handout_id = %s', (current_user.id, handout_id))
    progress = cur.fetchone()

    if progress:
        cur.execute('UPDATE handout_progress SET is_completed = %s WHERE id = %s', (is_completed, progress[0]))
    else:
        cur.execute('INSERT INTO handout_progress (user_id, handout_id, is_completed) VALUES (%s, %s, %s)',
                    (current_user.id, handout_id, is_completed))
    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Progress updated successfully"}

# ------------------ Main Execution ------------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)
