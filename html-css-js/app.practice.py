import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

#activity_log table: 
#CREATE TABLE activity_log (
#    id SERIAL PRIMARY KEY,
#    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
#    action_type VARCHAR(100) NOT NULL,
#    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#);

#users table: 
#CREATE TABLE users (
#    id SERIAL PRIMARY KEY,
#    username VARCHAR(150) NOT NULL,
#    email VARCHAR(150) UNIQUE NOT NULL,
#    password TEXT NOT NULL,
#    role VARCHAR(50) NOT NULL DEFAULT 'user',
#    last_login TIMESTAMP
#);

#Add a deactivated feature, first add deactivated column to users table: 
#ALTER TABLE uesrs ADD COLUMN deactivated BOOLEAN DEFAULT FALSE; 

#profile_views table 
#CREATE TABLE profile_views (
#    id SERIAL PRIMARY KEY,
#    viewer_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
#    viewed_profile_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
#    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#);

#Notes: SERIAL (auto_incrementing integer type, unique)
#REFERENCES users(id), establishes a foreign key relationship between the
#column and the id column of the users table, value in this column MUST 
#match an existing id in the users table 
#TIMESTAMP DEFAULT CURRENT_TIMESTAMP, sets def value of vol to current date
#and time 
#VARCHAR(150), string of up to 150 chars 
#NOT NULL, cannot contain null values, every user must have a username 




app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Database connection setup
def get_db_connection():
    conn = psycopg2.connect(
        dbname='flask_app_db',
        user='your_username',
        password='your_password',
        host='localhost'
    )
    return conn

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, email, role):
        self.id = id
        self.username = username
        self.email = email
        self.role = role


@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, username, email, role FROM users WHERE id = %s', (user_id,))
    user_data = cur.fetchone()
    cur.close()
    conn.close()
    if user_data:
        return User(id=user_data[0], username=user_data[1], email=user_data[2], role=user_data[3])
    return None

#LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, username, email, password, role, deactivated FROM users WHERE email = %s', (email,))
        user_data = cur.fetchone()

        if user_data: 
            deactivated=user_data[5]
            if deactivated: 
                flash('Your account has been deactivated')
                return redirect(url_for('login'))

            if check_password_hash(user_data[3], password):
                user_obj = User(id=user_data[0], username=user_data[1], email=user_data[2], role=user_data[4])
                login_user(user_obj)

                current_timestamp=datetime.now()
                cur.execute('UPDATE users SET last_login=%s WHERE id=%s', (current_timestamp, user_data[0]))
                cur.execute('INSERT INTO activity_log (user_id, action_type) VALUES (%s, %s)', (user_data[0], 'login'))
                conn.commit()

                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password', 'danger')
        else: 
            flash('Invalid email or password')
        cur.close()
        conn.close()

    return render_template('login.html')






#reactivate account route
@app.route('reactivate_account', methods=['POST'])
def reactivate_account(): 
    if request.method=='POST': 
        email=request.form['email']
        
        conn=get_db_connection()
        cur=conn.cursor()

        cur.execute('SELECT id from users WHERE email=%s AND deactivated=TRUE', (email, ))
        user_data=cur.fetchone()
        if user_data: 
            cur.execute('UPDATE users SET deactivated=FALSE WHERE id=%s', (user_data[0], ))
            conn.commit()

            flash('Reactivated account')
            cur.close()
            conn.close()
            return redirect(url_for('login'))
        else: 
            flash('Account not found or already active')
        cur.close()
        conn.close()
    return render_template('reactivate_account.html')

#deactive account route 
@app.route('deactivate_account', methods=['POST'])
@login_required 
def deactivate_account(): 
    conn=get_db_connection()
    cur=conn.cursor()

    cur.execute('UPDATE users SET deactivated=TRUE WHERE id=%s', (current_user.id))
    conn.commit()

    cur.close()
    conn.close()

    flash('Your account has been deactivated')
    logout_user()
    return redirect(url_for('login'))

#Display username profile route
@app.route('/profile', methods=['GET'])
def profile(): 
    return render_template('profile.html', username=current_user.username)

#Change password (with verification) route 
@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password(): 
    if request.method == 'POST': 
        current_password = request.form.get('current_password')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT password FROM users WHERE id = %s', (current_user.id,))
        current_hashed_password = cur.fetchone()[0]
        cur.close()
        conn.close()

        if check_password_hash(current_hashed_password, current_password): 
            new_password = request.form.get('new_password')
            new_password_hash = generate_password_hash(new_password)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('UPDATE users SET password = %s WHERE id = %s', (new_password_hash, current_user.id))
            conn.commit()  # Fixed typo here
            flash('Your password has been updated successfully', 'success')
        else: 
            flash('Current password is incorrect', 'danger')
        
        cur.close()
        conn.close()
        return redirect(url_for('profile'))

#Admins can manage user roles, promoting or demoting other users 
@app.route('/manage_roles', methods=['POST', 'GET'])
def manage_roles(): 
    if current_user.role!='admin': 
        flash('You do not have access to this page')
        redirect(url_for('main'))

    if request.method=='POST': 
        user_id=request.form.get('user_id')
        action=request.form.get('action')
        if action=='delete': 
            if user_id==str(current_user.id): 
                flash('Cannot delete own account')
            else: 
                conn=get_db_connection()
                curr=conn.curr()
                curr.execute('DELETE from users WHERE id=%s', (user_id))
                conn.commit()
                curr.close()
                conn.close()
                flash('User deleted successfully!')
        elif action=='update':
            new_role=request.form.get('new_role')
            conn=get_db_connection()
            cur=conn.cursor()
            cur.execute('UPDATE users SET role=%s WHERE id=%s', (new_role, user_id))
            conn.commit()
            cur.close()
            conn.close()
            flash('User role updated successfully!')
        return redirect(url_for('manage_roles'))
    elif request.method=='GET': 
        conn=get_db_connection()
        curr=conn.cursor()
        curr.execute('SELECT id, username, role FROm users')
        users=curr.fetchall()
        curr.close()
        conn.close()
        return render_template('manage_roles.html', users=users)




#REGISTER 
def password_strength(password): 
    if len(password)<9: 
        return False, 'Password must be at least 9 characters long'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'user')

        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM users WHERE email = %s', (email,))
        existing_user = cur.fetchone()
        if existing_user:
            flash('Email already registered!', 'danger')
        else:
            is_valid, message=password_strength(password)
            if not is_valid: 
                flash(message)
                return redirect(url_for('register'))
            hashed_password = generate_password_hash(password)
            cur.execute('INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)',
                        (username, email, hashed_password, role))
            conn.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        
        cur.close()
        conn.close()

    return render_template('register.html')


#GET ACTIVITY LOG AT DASHBOARD ROUTE, LAST 5 LOGINS
@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT action_type, timestamp FROM activity_log WHERE user_id = %s AND action_type = %s ORDER BY timestamp DESC LIMIT 5', (current_user.id, 'login'))
    recent_logins = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('dashboard.html', username=current_user.username, role=current_user.role, recent_logins=recent_logins)


#SEARCH QUERY ROUTE (PREFIX SQL)
@app.route('/search', methods=['GET'])
def search(): 
    query=request.args.get('query')
    conn=get_db_connection()
    cur=conn.cursor()

    search_query=f'%{query}%'
    cur.execute('SELECT id, username, email FROM users WHERE username LIKE %s OR email LIKE %s', (search_query, search_query))
    results=cur.fetchall()
    cur.close()
    conn.close()

    return render_template('search_results.html', user_data=results)


@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('admin.html')

@app.route('/logout')
@login_required
def logout():
    conn=get_db_connection()
    cur=conn.cursor()

    cur.execute('INSERT INTO activity_log (user_id, action) VALUES', (current_user.id, 'logout'))
    conn.committ()

    cur.close()
    conn.close()

    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
