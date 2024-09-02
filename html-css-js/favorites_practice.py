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

# CREATE TABLE favorites (
#     user_id INTEGER REFERENCES users(id),
#     item_id INTEGER REFERENCES items(id),
#     PRIMARY KEY (user_id, item_id)
# );

@app.route('/')
def index():
    return 'Welcome to the Favorites App!'

@app.route('/add_to_favorites/<int:item_id>', methods=['POST'])
@login_required
def add_to_favorites(item_id):
    user_id = current_user.id
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if the item is already in the user's favorites
    cur.execute('SELECT * FROM favorites WHERE user_id = %s AND item_id = %s', (user_id, item_id))
    already_favorited = cur.fetchone()
    
    if already_favorited:
        flash('Item is already in your favorites.', 'info')
    else:
        # Add the item to the favorites table
        cur.execute('INSERT INTO favorites (user_id, item_id) VALUES (%s, %s)', (user_id, item_id))
        conn.commit()
        flash('Item added to favorites!', 'success')
    
    cur.close()
    conn.close()
    
    return redirect(url_for('view_item', item_id=item_id))

@app.route('/favorites', methods=['GET'])
@login_required
def view_favorites():
    user_id = current_user.id
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get all favorite items for the current user
    cur.execute('SELECT items.id, items.name FROM items JOIN favorites ON items.id = favorites.item_id WHERE favorites.user_id = %s', (user_id,))
    favorite_items = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('favorites.html', favorite_items=favorite_items)

@app.route('/remove_from_favorites/<int:item_id>', methods=['POST'])
@login_required
def remove_from_favorites(item_id):
    user_id = current_user.id
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Remove the item from the user's favorites
    cur.execute('DELETE FROM favorites WHERE user_id = %s AND item_id = %s', (user_id, item_id))
    conn.commit()
    
    cur.close()
    conn.close()
    
    flash('Item removed from favorites.', 'success')
    return redirect(url_for('favorites'))

if __name__ == '__main__':
    app.run(debug=True)
