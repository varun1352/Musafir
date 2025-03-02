import sqlite3
import json
from datetime import datetime

DATABASE = 'musafir.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # Users Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT,
        preferences TEXT,
        email_verified BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Places Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS places (
        place_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        activities TEXT,
        photos TEXT,
        recommended_time INTEGER,
        latitude REAL,
        longitude REAL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Distances Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS distances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        place_from INTEGER NOT NULL,
        place_to INTEGER NOT NULL,
        distance_value REAL,
        travel_time INTEGER,
        FOREIGN KEY (place_from) REFERENCES places(place_id),
        FOREIGN KEY (place_to) REFERENCES places(place_id)
    )
    ''')

    # Itineraries Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS itineraries (
        itinerary_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        markdown_data TEXT,
        json_data TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')

    # EmailApprovals Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS email_approvals (
        approval_id INTEGER PRIMARY KEY AUTOINCREMENT,
        requester_id INTEGER NOT NULL,
        recipient_id INTEGER NOT NULL,
        recipient_email TEXT NOT NULL,
        token TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (requester_id) REFERENCES users(user_id),
        FOREIGN KEY (recipient_id) REFERENCES users(user_id)
    )
    ''')

    # DayPlans Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS day_plans (
        plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        day INTEGER NOT NULL,
        plan_data TEXT,
        finalized BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')

    conn.commit()
    conn.close()

# User-related functions
def create_user(username, email, password_hash, preferences):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    INSERT INTO users (username, email, password_hash, preferences)
    VALUES (?, ?, ?, ?)
    ''', (username, email, password_hash, json.dumps(preferences)))
    user_id = cur.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_user_by_email(email):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cur.fetchone()
    conn.close()
    return dict(user) if user else None

def update_user_preferences(user_id, preferences):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    UPDATE users SET preferences = ? WHERE user_id = ?
    ''', (json.dumps(preferences), user_id))
    conn.commit()
    conn.close()

def get_user_by_id(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cur.fetchone()
    conn.close()
    return dict(user) if user else None

# Place-related functions
def add_place(name, description, activities, photos, recommended_time, latitude, longitude):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    INSERT INTO places (name, description, activities, photos, recommended_time, latitude, longitude)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, description, json.dumps(activities), json.dumps(photos), recommended_time, latitude, longitude))
    place_id = cur.lastrowid
    conn.commit()
    conn.close()
    return place_id

def get_places():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM places')
    places = cur.fetchall()
    conn.close()
    return [dict(place) for place in places]

# Itinerary-related functions
def save_itinerary(user_id, markdown_data, json_data):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    INSERT INTO itineraries (user_id, markdown_data, json_data)
    VALUES (?, ?, ?)
    ''', (user_id, markdown_data, json.dumps(json_data)))
    itinerary_id = cur.lastrowid
    conn.commit()
    conn.close()
    return itinerary_id

def get_user_itineraries(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM itineraries WHERE user_id = ?', (user_id,))
    itineraries = cur.fetchall()
    conn.close()
    return [dict(itinerary) for itinerary in itineraries]

# EmailApproval-related functions
def create_email_approval(requester_id, recipient_id, recipient_email, token):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    INSERT INTO email_approvals (requester_id, recipient_id, recipient_email, token)
    VALUES (?, ?, ?, ?)
    ''', (requester_id, recipient_id, recipient_email, token))
    approval_id = cur.lastrowid
    conn.commit()
    conn.close()
    return approval_id

def update_email_approval_status(token, status):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    UPDATE email_approvals SET status = ? WHERE token = ?
    ''', (status, token))
    conn.commit()
    conn.close()

# DayPlan-related functions
def save_day_plan(user_id, day, plan_data, finalized=False):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    INSERT INTO day_plans (user_id, day, plan_data, finalized)
    VALUES (?, ?, ?, ?)
    ''', (user_id, day, json.dumps(plan_data), finalized))
    plan_id = cur.lastrowid
    conn.commit()
    conn.close()
    return plan_id

def get_user_day_plans(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM day_plans WHERE user_id = ?', (user_id,))
    day_plans = cur.fetchall()
    conn.close()
    return [dict(plan) for plan in day_plans]

def finalize_day_plan(plan_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    UPDATE day_plans SET finalized = 1 WHERE plan_id = ?
    ''', (plan_id,))
    conn.commit()
    conn.close()

def get_featured_trips():
    # Implement logic to fetch featured trips from the database
    # This is a placeholder implementation
    return [
        {
            "id": 1,
            "title": "NYC Classic Weekend",
            "duration": "3 days",
            "rating": 4.8,
            "reviews": 156,
            "image": "nyc_weekend.jpg",
            "highlights": ["Central Park", "Times Square", "Statue of Liberty"]
        },
        {
            "id": 2,
            "title": "San Francisco Bay Tour",
            "duration": "4 days",
            "rating": 4.7,
            "reviews": 98,
            "image": "sf_bay.jpg",
            "highlights": ["Golden Gate Bridge", "Alcatraz", "Fisherman's Wharf"]
        },
    ]

def get_trip_categories():
    # Implement logic to fetch trip categories from the database
    # This is a placeholder implementation
    featured_trips = get_featured_trips()
    return [
        {
            "name": "Weekend Getaways",
            "trips": featured_trips[:3]
        },
        {
            "name": "Family Adventures",
            "trips": featured_trips[1:4]
        },
        {
            "name": "Cultural Experiences",
            "trips": featured_trips[2:5]
        }
    ]

# Initialize the database
init_db()

