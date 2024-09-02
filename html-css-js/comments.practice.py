from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Database connection setup
def get_db_connection():
    conn = psycopg2.connect(
        dbname='your_database_name',
        user='your_username',
        password='your_password',
        host='localhost'
    )
    return conn

# SQL Table Creation (Run these in your PostgreSQL environment):
# CREATE TABLE users (
#     id SERIAL PRIMARY KEY,
#     username VARCHAR(150) NOT NULL,
#     email VARCHAR(150) UNIQUE NOT NULL,
#     password TEXT NOT NULL
# );

# CREATE TABLE items (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(100) NOT NULL
# );

# CREATE TABLE comments (
#     id SERIAL PRIMARY KEY,
#     user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
#     item_id INTEGER REFERENCES items(id) ON DELETE CASCADE,
#     comment TEXT NOT NULL,
#     timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

@app.route('/')
def index():
    return 'Welcome to the Comment System!'

#ROUTE 1: Allows logged_in users to submit a comment on a specific item
@app.route('/add_comment/<int:item_id>', methods=['POST'])
def add_comments(item_id): 
    current_user_id=current_user.id 
    comment=request.form.get('comment_form')

    conn=get_db_connection()
    cur=conn.cursor()
    cur.execute('INSERT INTO comments (user_id, item_id, comment) VALUES (%s, %s, %s)',
                (current_user_id, item_id, comment))
    conn.commit()

    cur.close()
    conn.close()
    flash('Your comment has been added')
    return redirect(url_for('view_item'))

@app.route('/display_comments/<int: item_id>', methods=['GET'])
def display_comments(item_id): 
    conn=get_db_connection()
    cur=conn.cursor()

    cur.execute('SELECT * FROM items WHERE id=%s', (item_id))
    item=cur.fetchone()

    cur.execute('SELECT comments.comment, users.username, comments.timestamp FROM comments JOIN users on comments.user_id=users.id WHERE comments.item_id=%s ORDER BY comments.timestamp DESC', (item_id))
    comments=cur.fetchall()
    cur.close()
    conn.close()

    return render_template('item.html', item=item, comments=comments)

#SELECT comments.comment, users.username, comments.timestamp FROM comments
#JOIN users on comment.users_id=users.id WHERE comments.item_id=%s ORDER BY
#timestamp DESC, (item_id)    SQL query to get info about an item, its 
#comments, those comments usernames, and those comments timestamps 

if __name__ == '__main__':
    app.run(debug=True)
