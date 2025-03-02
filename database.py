import sqlite3
import os
from datetime import datetime
import json
from threading import local

class Database:
    _thread_local = local()

    def __init__(self, db_path='musafir.db'):
        self.db_path = db_path
        self.initialize_db()

    def get_connection(self):
        if not hasattr(self._thread_local, 'connection'):
            self._thread_local.connection = sqlite3.connect(self.db_path)
            self._thread_local.connection.row_factory = sqlite3.Row
        return self._thread_local.connection

    def close_connection(self):
        if hasattr(self._thread_local, 'connection'):
            self._thread_local.connection.close()
            del self._thread_local.connection

    def __del__(self):
        self.close_connection()

    def _check_table_schema(self, cursor, table_name, expected_columns):
        """Verify table schema matches expected columns."""
        cursor.execute(f"PRAGMA table_info({table_name})")
        actual_columns = {row[1] for row in cursor.fetchall()}
        missing_columns = set(expected_columns) - actual_columns
        
        if missing_columns:
            raise Exception(f"Table '{table_name}' is missing columns: {missing_columns}")

    def initialize_db(self):
        """Initialize the database with all required tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            google_id TEXT UNIQUE,
            profile_image TEXT,
            joined_date TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1
        )
        ''')

        # User preferences table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            preference_type TEXT NOT NULL,
            preference_value TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, preference_type, preference_value)
        )
        ''')

        # Trips table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            destination TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')

        # Places table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            image_url TEXT,
            rating REAL,
            address TEXT,
            place_type TEXT,
            external_id TEXT,
            UNIQUE(latitude, longitude, name)
        )
        ''')

        # Place details table (for additional data like highlights, activities)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS place_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            place_id INTEGER NOT NULL,
            detail_type TEXT NOT NULL,
            detail_value TEXT NOT NULL,
            FOREIGN KEY (place_id) REFERENCES places (id),
            UNIQUE(place_id, detail_type, detail_value)
        )
        ''')

        # Itinerary items table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS itinerary_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL,
            place_id INTEGER NOT NULL,
            day INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            notes TEXT,
            order_index INTEGER NOT NULL,
            FOREIGN KEY (trip_id) REFERENCES trips (id),
            FOREIGN KEY (place_id) REFERENCES places (id)
        )
        ''')

        # Distance matrix for travel times between places
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS distances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origin_place_id INTEGER NOT NULL,
            destination_place_id INTEGER NOT NULL,
            distance_km REAL NOT NULL,
            duration_minutes INTEGER NOT NULL,
            travel_mode TEXT NOT NULL,
            FOREIGN KEY (origin_place_id) REFERENCES places (id),
            FOREIGN KEY (destination_place_id) REFERENCES places (id),
            UNIQUE(origin_place_id, destination_place_id, travel_mode)
        )
        ''')

        # Chat sessions for travel planning
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            trip_id INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (trip_id) REFERENCES trips (id)
        )
        ''')

        # Chat messages
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
        )
        ''')

        # Verify table schemas
        self._check_table_schema(cursor, 'users', [
            'id', 'name', 'email', 'password_hash', 'google_id', 
            'profile_image', 'joined_date', 'is_active'
        ])

        # Insert sample data if the database is new
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            self._insert_sample_data()

        conn.commit()

    def _insert_sample_data(self):
        """Insert sample data for testing purposes."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Sample users
        cursor.execute('''
        INSERT INTO users (name, email, password_hash, joined_date)
        VALUES (?, ?, ?, ?)
        ''', ('John Doe', 'john@example.com', 'pbkdf2:sha256:150000$abc123', datetime.now().strftime('%Y-%m-%d')))
        
        user_id = cursor.lastrowid
        
        # Sample preferences
        preferences = ['Adventure', 'Cultural', 'Food', 'Photography']
        for pref in preferences:
            cursor.execute('''
            INSERT INTO user_preferences (user_id, preference_type, preference_value)
            VALUES (?, ?, ?)
            ''', (user_id, 'travel_style', pref))
        
        # Sample trip
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
        INSERT INTO trips (user_id, title, destination, start_date, end_date, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, 'New York Adventure', 'New York', '2023-07-01', '2023-07-07', 'upcoming', now, now))
        
        trip_id = cursor.lastrowid
        
        # Sample places
        places = [
            ('Central Park', 'Iconic urban park with various attractions', 40.7829, -73.9654, '/static/images/central_park.jpg', 4.8, 'New York, NY', 'park', 'cp123'),
            ('Metropolitan Museum of Art', 'One of the world\'s largest art museums', 40.7794, -73.9632, '/static/images/met.jpg', 4.9, 'New York, NY', 'museum', 'met123'),
            ('Times Square', 'Iconic intersection known for bright lights', 40.7580, -73.9855, '/static/images/times_square.jpg', 4.6, 'New York, NY', 'landmark', 'ts123')
        ]
        
        for place in places:
            cursor.execute('''
            INSERT INTO places (name, description, latitude, longitude, image_url, rating, address, place_type, external_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', place)
            
            place_id = cursor.lastrowid
            
            # Sample place details
            if place[0] == 'Central Park':
                details = [
                    ('highlight', 'Bethesda Fountain'),
                    ('highlight', 'Belvedere Castle'),
                    ('highlight', 'The Lake'),
                    ('activity', 'Walking Tours'),
                    ('activity', 'Boating'),
                    ('activity', 'Zoo Visit')
                ]
                
                for detail_type, detail_value in details:
                    cursor.execute('''
                    INSERT INTO place_details (place_id, detail_type, detail_value)
                    VALUES (?, ?, ?)
                    ''', (place_id, detail_type, detail_value))
        
        # Sample itinerary items
        itinerary_items = [
            (trip_id, 1, 1, '09:00', '11:00', 'Morning walk through the park', 1),
            (trip_id, 2, 1, '12:00', '15:00', 'Explore the art collections', 2),
            (trip_id, 3, 1, '16:00', '18:00', 'Experience the vibrant atmosphere', 3)
        ]
        
        for item in itinerary_items:
            cursor.execute('''
            INSERT INTO itinerary_items (trip_id, place_id, day, start_time, end_time, notes, order_index)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', item)
        
        conn.commit()

    # User-related methods
    def create_user(self, name, email, password_hash=None, google_id=None, profile_image=None):
        """Create a new user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        joined_date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            cursor.execute('''
            INSERT INTO users (name, email, password_hash, google_id, profile_image, joined_date)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, email, password_hash, google_id, profile_image, joined_date))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # User already exists
            return None

    def get_user_by_email(self, email):
        """Get a user by email."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        return cursor.fetchone()

    def get_user_by_google_id(self, google_id):
        """Get a user by Google ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE google_id = ?', (google_id,))
        return cursor.fetchone()

    def get_user_by_id(self, user_id):
        """Get a user by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return cursor.fetchone()

    def update_user(self, user_id, **kwargs):
        """Update user information."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.append(user_id)
        
        cursor.execute(f'''
        UPDATE users
        SET {set_clause}
        WHERE id = ?
        ''', values)
        conn.commit()
        return cursor.rowcount > 0

    def get_user_preferences(self, user_id):
        """Get all preferences for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT preference_type, preference_value
        FROM user_preferences
        WHERE user_id = ?
        ''', (user_id,))
        
        preferences = {}
        for row in cursor.fetchall():
            pref_type = row['preference_type']
            pref_value = row['preference_value']
            
            if pref_type not in preferences:
                preferences[pref_type] = []
            
            preferences[pref_type].append(pref_value)
        
        return preferences

    def add_user_preference(self, user_id, preference_type, preference_value):
        """Add a preference for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO user_preferences (user_id, preference_type, preference_value)
            VALUES (?, ?, ?)
            ''', (user_id, preference_type, preference_value))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Preference already exists
            return False

    # Trip-related methods
    def create_trip(self, user_id, title, destination, start_date, end_date, status='upcoming'):
        """Create a new trip."""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
        INSERT INTO trips (user_id, title, destination, start_date, end_date, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, title, destination, start_date, end_date, status, now, now))
        conn.commit()
        return cursor.lastrowid

    def get_user_trips(self, user_id):
        """Get all trips for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM trips
        WHERE user_id = ?
        ORDER BY start_date DESC
        ''', (user_id,))
        return cursor.fetchall()

    def get_trip_by_id(self, trip_id):
        """Get a trip by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM trips WHERE id = ?', (trip_id,))
        return cursor.fetchone()

    def update_trip(self, trip_id, **kwargs):
        """Update trip information."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        kwargs['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.append(trip_id)
        
        cursor.execute(f'''
        UPDATE trips
        SET {set_clause}
        WHERE id = ?
        ''', values)
        conn.commit()
        return cursor.rowcount > 0

    # Place-related methods
    def create_place(self, name, latitude, longitude, description=None, image_url=None, 
                    rating=None, address=None, place_type=None, external_id=None):
        """Create a new place."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO places (name, description, latitude, longitude, image_url, rating, address, place_type, external_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, description, latitude, longitude, image_url, rating, address, place_type, external_id))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Place already exists, get its ID
            cursor.execute('''
            SELECT id FROM places
            WHERE latitude = ? AND longitude = ? AND name = ?
            ''', (latitude, longitude, name))
            result = cursor.fetchone()
            return result['id'] if result else None

    def get_place_by_id(self, place_id):
        """Get a place by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM places WHERE id = ?', (place_id,))
        place = cursor.fetchone()
        
        if place:
            # Get place details
            cursor.execute('''
            SELECT detail_type, detail_value
            FROM place_details
            WHERE place_id = ?
            ''', (place_id,))
            
            details = {}
            for row in cursor.fetchall():
                detail_type = row['detail_type']
                detail_value = row['detail_value']
                
                if detail_type not in details:
                    details[detail_type] = []
                
                details[detail_type].append(detail_value)
            
            place_dict = dict(place)
            place_dict.update(details)
            return place_dict
        
        return None

    def add_place_detail(self, place_id, detail_type, detail_value):
        """Add a detail to a place."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO place_details (place_id, detail_type, detail_value)
            VALUES (?, ?, ?)
            ''', (place_id, detail_type, detail_value))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Detail already exists
            return False

    def search_places(self, query, limit=10):
        """Search for places by name or description."""
        conn = self.get_connection()
        cursor = conn.cursor()
        search_term = f"%{query}%"
        
        cursor.execute('''
        SELECT * FROM places
        WHERE name LIKE ? OR description LIKE ?
        LIMIT ?
        ''', (search_term, search_term, limit))
        
        return cursor.fetchall()

    # Itinerary-related methods
    def add_itinerary_item(self, trip_id, place_id, day, start_time, end_time, notes=None, order_index=None):
        """Add an item to an itinerary."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # If order_index is not provided, put it at the end
        if order_index is None:
            cursor.execute('''
            SELECT MAX(order_index) as max_order
            FROM itinerary_items
            WHERE trip_id = ? AND day = ?
            ''', (trip_id, day))
            
            result = cursor.fetchone()
            order_index = (result['max_order'] or 0) + 1
        
        cursor.execute('''
        INSERT INTO itinerary_items (trip_id, place_id, day, start_time, end_time, notes, order_index)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (trip_id, place_id, day, start_time, end_time, notes, order_index))
        conn.commit()
        return cursor.lastrowid

    def get_trip_itinerary(self, trip_id):
        """Get the full itinerary for a trip."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT i.*, p.name, p.latitude, p.longitude, p.image_url, p.rating
        FROM itinerary_items i
        JOIN places p ON i.place_id = p.id
        WHERE i.trip_id = ?
        ORDER BY i.day, i.order_index
        ''', (trip_id,))
        
        itinerary = {}
        for item in cursor.fetchall():
            day = item['day']
            
            if day not in itinerary:
                itinerary[day] = []
            
            itinerary[day].append(dict(item))
        
        return itinerary

    def update_itinerary_item(self, item_id, **kwargs):
        """Update an itinerary item."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.append(item_id)
        
        cursor.execute(f'''
        UPDATE itinerary_items
        SET {set_clause}
        WHERE id = ?
        ''', values)
        conn.commit()
        return cursor.rowcount > 0

    def delete_itinerary_item(self, item_id):
        """Delete an itinerary item."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM itinerary_items WHERE id = ?', (item_id,))
        conn.commit()
        return cursor.rowcount > 0

    # Chat-related methods
    def create_chat_session(self, user_id, trip_id=None):
        """Create a new chat session."""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
        INSERT INTO chat_sessions (user_id, trip_id, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        ''', (user_id, trip_id, now, now))
        conn.commit()
        return cursor.lastrowid

    def add_chat_message(self, session_id, sender, message):
        """Add a message to a chat session."""
        conn = self.get_connection()
        cursor = conn.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
        INSERT INTO chat_messages (session_id, sender, message, timestamp)
        VALUES (?, ?, ?, ?)
        ''', (session_id, sender, message, timestamp))
        
        # Update the session's updated_at timestamp
        cursor.execute('''
        UPDATE chat_sessions
        SET updated_at = ?
        WHERE id = ?
        ''', (timestamp, session_id))
        
        conn.commit()
        return cursor.lastrowid

    def get_chat_messages(self, session_id):
        """Get all messages for a chat session."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM chat_messages
        WHERE session_id = ?
        ORDER BY timestamp
        ''', (session_id,))
        
        return cursor.fetchall()

    def get_user_chat_sessions(self, user_id):
        """Get all chat sessions for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM chat_sessions
        WHERE user_id = ?
        ORDER BY updated_at DESC
        ''', (user_id,))
        
        return cursor.fetchall()

    # Distance-related methods
    def add_distance(self, origin_id, destination_id, distance_km, duration_minutes, travel_mode='driving'):
        """Add a distance between two places."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO distances (origin_place_id, destination_place_id, distance_km, duration_minutes, travel_mode)
            VALUES (?, ?, ?, ?, ?)
            ''', (origin_id, destination_id, distance_km, duration_minutes, travel_mode))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Distance already exists, update it
            cursor.execute('''
            UPDATE distances
            SET distance_km = ?, duration_minutes = ?
            WHERE origin_place_id = ? AND destination_place_id = ? AND travel_mode = ?
            ''', (distance_km, duration_minutes, origin_id, destination_id, travel_mode))
            conn.commit()
            return True

    def get_distance(self, origin_id, destination_id, travel_mode='driving'):
        """Get the distance between two places."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM distances
        WHERE origin_place_id = ? AND destination_place_id = ? AND travel_mode = ?
        ''', (origin_id, destination_id, travel_mode))
        
        return cursor.fetchone()

    # Helper methods for profile page
    def get_user_profile_data(self, user_id):
        """Get all data needed for the user profile page."""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        trips = self.get_user_trips(user_id)
        preferences = self.get_user_preferences(user_id)
        
        # Format the data for the template
        profile_data = {
            'user': dict(user),
            'trips': [dict(trip) for trip in trips],
            'preferences': preferences.get('travel_style', [])
        }
        
        return profile_data

    # Helper methods for map view
    def get_trip_map_data(self, trip_id):
        """Get all data needed for the map view."""
        trip = self.get_trip_by_id(trip_id)
        if not trip:
            return None
        
        itinerary = self.get_trip_itinerary(trip_id)
        
        # Format the data for the template
        map_data = {
            'trip': dict(trip),
            'days': []
        }
        
        for day, items in itinerary.items():
            day_data = {
                'date': (datetime.strptime(trip['start_date'], '%Y-%m-%d') + 
                        timedelta(days=day-1)).strftime('%Y-%m-%d'),
                'places': []
            }
            
            for item in items:
                place_data = {
                    'name': item['name'],
                    'lat': item['latitude'],
                    'lng': item['longitude'],
                    'time': f"{item['start_time']} - {item['end_time']}",
                    'description': item['notes'] or '',
                    'rating': item['rating'],
                    'image': item['image_url'] or '/placeholder.svg?height=200&width=300',
                    'visitors': []  # This would need to be populated from another source
                }
                day_data['places'].append(place_data)
            
            map_data['days'].append(day_data)
        
        return map_data

    # Helper methods for dynamic planning
    def get_place_suggestions(self, latitude, longitude, radius_km=5, limit=10, exclude_place_ids=None):
        """Get place suggestions for dynamic planning."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Simple distance calculation (not accurate for large distances)
        # For production, use a proper geospatial database or API
        lat_range = radius_km / 111.0  # 1 degree latitude is approximately 111 km
        lon_range = radius_km / (111.0 * cos(radians(latitude)))
        
        query = '''
        SELECT * FROM places
        WHERE latitude BETWEEN ? AND ?
        AND longitude BETWEEN ? AND ?
        '''
        
        params = [
            latitude - lat_range, latitude + lat_range,
            longitude - lon_range, longitude + lon_range
        ]
        
        if exclude_place_ids:
            placeholders = ','.join(['?'] * len(exclude_place_ids))
            query += f' AND id NOT IN ({placeholders})'
            params.extend(exclude_place_ids)
        
        query += ' LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        places = cursor.fetchall()
        
        # Enhance places with details
        result = []
        for place in places:
            place_dict = dict(place)
            
            # Get place details
            cursor.execute('''
            SELECT detail_type, detail_value
            FROM place_details
            WHERE place_id = ?
            ''', (place['id'],))
            
            details = {}
            for row in cursor.fetchall():
                detail_type = row['detail_type']
                detail_value = row['detail_value']
                
                if detail_type not in details:
                    details[detail_type] = []
                
                details[detail_type].append(detail_value)
            
            place_dict.update(details)
            result.append(place_dict)
        
        return result

    # Helper methods for itinerary generation
    def generate_markdown_itinerary(self, trip_id):
        """Generate a markdown itinerary for a trip."""
        trip = self.get_trip_by_id(trip_id)
        if not trip:
            return None
        
        itinerary = self.get_trip_itinerary(trip_id)
        
        # Build the markdown content
        md_content = f"# {trip['title']} Itinerary\n\n"
        md_content += f"**Destination:** {trip['destination']}\n"
        md_content += f"**Dates:** {trip['start_date']} to {trip['end_date']}\n\n"
        
        for day, items in sorted(itinerary.items()):
            day_date = (datetime.strptime(trip['start_date'], '%Y-%m-%d') + 
                       timedelta(days=day-1)).strftime('%Y-%m-%d')
            day_name = (datetime.strptime(day_date, '%Y-%m-%d')).strftime('%A')
            
            md_content += f"## Day {day}: {day_name}, {day_date}\n\n"
            
            for item in items:
                md_content += f"### {item['start_time']} - {item['end_time']}: {item['name']}\n\n"
                
                if item['notes']:
                    md_content += f"{item['notes']}\n\n"
                
                # Add place details if available
                place = self.get_place_by_id(item['place_id'])
                if place and place.get('description'):
                    md_content += f"{place['description']}\n\n"
                
                if place and place.get('highlight'):
                    md_content += "**Highlights:**\n\n"
                    for highlight in place['highlight']:
                        md_content += f"- {highlight}\n"
                    md_content += "\n"
                
                if place and place.get('activity'):
                    md_content += "**Suggested Activities:**\n\n"
                    for activity in place['activity']:
                        md_content += f"- {activity}\n"
                    md_content += "\n"
        
        return md_content

