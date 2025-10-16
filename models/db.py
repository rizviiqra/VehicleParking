import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Defining path of my database file
database = 'parking_app.db'

def init_db():
    """
    Initializing the SQLite database:
    - Connecting to the databiase.
    - Creating 'users', 'parking_lots', 'parking_spots', and 'reserved_spots' tables if they don't exist.
    - Inserts a default 'admin' user if one doesn't already exist.
    """
    conn = None # Initialize conn to None
    try:
        # Connecting to the SQLite database. If the file doesn't exist, it will be created.
        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        print(f"Connected to database: {database}")

        # 1. Now creating users table which stores user credentials and roles.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user' -- 'user' or 'admin'
            )
        ''')
        print("Table 'users' done.")

        # 2. Create 'parking_lots' table. Stores info about parking lots.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parking_lots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prime_location_name TEXT NOT NULL UNIQUE,
                price_per_hour REAL NOT NULL,
                address TEXT,
                pincode TEXT,
                maximum_number_of_spots INTEGER NOT NULL
            )
        ''')
        print("Table 'parking_lots' done.")

        # 3. Create 'parking_spots' table. Stores individual parking spots linked to a parking lot.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parking_spots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lot_id INTEGER NOT NULL,
                spot_number INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'available', -- 'available' or 'occupied'
                FOREIGN KEY (lot_id) REFERENCES parking_lots(id) ON DELETE CASCADE,
                UNIQUE(lot_id, spot_number) -- Ensures each spot number is unique within a given lot
            )
        ''')
        print("Table 'parking_spots' ensured.")

        # 4. Create 'reserved_spots' table (or 'parking_transactions')
        # Records each parking reservation/transaction.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reserved_spots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                spot_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                parking_timestamp TEXT NOT NULL, -- Store as ISO 8601 string (e.g., YYYY-MM-DD HH:MM:SS)
                leaving_timestamp TEXT,          -- NULLable, updated when vehicle leaves
                parking_cost_per_unit REAL NOT NULL, -- Price at the time of parking
                total_cost REAL,                 -- NULLable, calculated upon leaving
                FOREIGN KEY (spot_id) REFERENCES parking_spots(id) ON DELETE RESTRICT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT
            )
        ''')
        print("Table 'reserved_spots' ensured.")

        # Insert default 'admin' user if not exists.
        admin_username = 'admin_123'
        admin_password_raw = 'admin#0123' # Default password for the admin
        admin_password_hash = generate_password_hash(admin_password_raw)

        cursor.execute("SELECT id FROM users WHERE username = ?", (admin_username,))
        admin_exists = cursor.fetchone()

        if not admin_exists:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                           (admin_username, admin_password_hash, 'admin'))
            print(f"Default admin user '{admin_username}' created with password '{admin_password_raw}'.")
        else:
            print(f"Admin user '{admin_username}' already exists.")

        # Commit all changes to the database
        conn.commit()
        print("Database initialization complete.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback() # Rollback changes if an error occurs
    finally:
        if conn:
            conn.close() # Always close the connection

if __name__ == '__main__':
    # This block runs only when db.py is executed directly
    # You might want to delete the old database file for a clean start during development
    if os.path.exists(database):
        os.remove(database)
        print(f"Existing database '{database}' removed for a clean start.")
    
    init_db()

