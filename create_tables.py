import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="Postgresql DB",
    user="postgres",
    password="Geobobo"
)


cur = conn.cursor()


create_users_table = """
CREATE TABLE IF NOT EXISTS user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(150) NOT NULL,
    last_handout_viewed INT
);
"""

create_handouts_table = """
CREATE TABLE IF NOT EXISTS handouts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(150) NOT NULL
);
"""

create_handout_progress_table = """
CREATE TABLE IF NOT EXISTS handout_progress (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    handout_id INT REFERENCES handouts(id) ON DELETE CASCADE,
    is_completed BOOLEAN DEFAULT FALSE
);
"""


cur.execute(create_users_table)
cur.execute(create_handouts_table)
cur.execute(create_handout_progress_table)


conn.commit()


cur.close()
conn.close()

