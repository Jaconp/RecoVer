import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Get connection parameters from environment variables
dbname = os.environ.get('PGDATABASE')
user = os.environ.get('PGUSER')
password = os.environ.get('PGPASSWORD')
host = os.environ.get('PGHOST')
port = os.environ.get('PGPORT')

# Print database connection info (for debugging)
print(f"Connecting to: host={host}, port={port}, dbname={dbname}, user={user}")

# Connect to PostgreSQL server
conn = psycopg2.connect(
    host=host,
    port=port,
    user=user,
    password=password
)

conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()

# Create tables from SQL schema based on models.py
print("Initializing database schema...")

SQL_SCHEMA = """
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256),
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "item_category" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS "lost_item" (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    date_lost DATE NOT NULL,
    location_lost VARCHAR(200) NOT NULL,
    image_filename VARCHAR(200),
    contact_info VARCHAR(100),
    reward VARCHAR(100),
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL REFERENCES "user"(id),
    category_id INTEGER REFERENCES "item_category"(id),
    color VARCHAR(50),
    brand VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS "found_item" (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    date_found DATE NOT NULL,
    location_found VARCHAR(200) NOT NULL,
    image_filename VARCHAR(200),
    contact_info VARCHAR(100),
    is_claimed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL REFERENCES "user"(id),
    category_id INTEGER REFERENCES "item_category"(id),
    color VARCHAR(50),
    brand VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS "notification" (
    id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL REFERENCES "user"(id),
    lost_item_id INTEGER REFERENCES "lost_item"(id),
    found_item_id INTEGER REFERENCES "found_item"(id)
);

CREATE TABLE IF NOT EXISTS "match" (
    id SERIAL PRIMARY KEY,
    lost_item_id INTEGER NOT NULL REFERENCES "lost_item"(id),
    found_item_id INTEGER NOT NULL REFERENCES "found_item"(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    match_score FLOAT
);

-- Create admin user if no users exist
INSERT INTO "user" (username, email, password_hash, is_admin)
SELECT 'admin', 'admin@example.com', 'pbkdf2:sha256:260000$jEOtCPe1j1ZXUbE5$e59f8918cfb453cf9c1ae63dc5a92c49e78b6af26fbf0389e60e257d5dfc747a', TRUE
WHERE NOT EXISTS (SELECT 1 FROM "user" LIMIT 1);

-- Add some default categories
INSERT INTO "item_category" (name)
VALUES 
  ('Electronics'),
  ('Clothing'),
  ('Books'),
  ('Accessories'),
  ('Keys'),
  ('ID/Cards'),
  ('Other')
ON CONFLICT (name) DO NOTHING;
"""

# Execute the SQL schema
cursor.execute(SQL_SCHEMA)

# Close connection
cursor.close()
conn.close()

print("Database initialization complete!")