import json
import random
from datetime import datetime, timedelta
import names
from faker import Faker
import sqlite3

fake = Faker()

def load_places():
    """Load the places data from JSON file."""
    with open('nyc_places.json', 'r') as f:
        return json.load(f)

def generate_itinerary(places, date):
    """Generate a random itinerary for a day."""
    # Pick 2-4 random places
    num_places = random.randint(2, 4)
    selected_places = random.sample(places, num_places)
    
    # Sort by typical visit times to create a logical sequence
    itinerary = []
    current_time = datetime.strptime("09:00", "%H:%M")
    
    for place in selected_places:
        # Pick a time slot that works
        valid_times = [
            datetime.strptime(t, "%H:%M") 
            for t in place["typical_times"]
            if datetime.strptime(t, "%H:%M") >= current_time
        ]
        
        if valid_times:
            visit_time = min(valid_times)
            end_time = visit_time + timedelta(minutes=place["visit_duration"])
            
            itinerary.append({
                "place_id": places.index(place) + 1,
                "start_time": visit_time.strftime("%H:%M"),
                "end_time": end_time.strftime("%H:%M"),
                "date": date.strftime("%Y-%m-%d")
            })
            
            current_time = end_time + timedelta(minutes=30)  # Add travel time
    
    return itinerary

def generate_users(num_users, places):
    """Generate sample users with their trips."""
    users = []
    now = datetime.now()
    
    for _ in range(num_users):
        # Generate user details
        first_name = names.get_first_name()
        last_name = names.get_last_name()
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"
        
        # Generate trips for next three days
        trips = []
        for day in range(3):
            date = now + timedelta(days=day)
            itinerary = generate_itinerary(places, date)
            
            if itinerary:  # Only add if we have valid places to visit
                trips.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "itinerary": itinerary
                })
        
        user = {
            "name": f"{first_name} {last_name}",
            "email": email,
            "password_hash": "pbkdf2:sha256:150000$dummy_hash",  # Dummy hash for testing
            "joined_date": now.strftime("%Y-%m-%d"),
            "trips": trips,
            "preferences": random.sample([
                "Cultural", "Adventure", "Photography", "Food", 
                "History", "Art", "Architecture", "Nature"
            ], random.randint(2, 4))
        }
        
        users.append(user)
    
    return users

def insert_into_database(users, places):
    """Insert the generated data into the SQLite database."""
    conn = sqlite3.connect('musafir.db')
    cursor = conn.cursor()
    
    try:
        # First, insert places if they don't exist
        for i, place in enumerate(places, 1):
            cursor.execute('''
            INSERT OR IGNORE INTO places (
                id, name, description, latitude, longitude, 
                image_url, address, place_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                i, place["name"], place["description"], 
                place["lat"], place["lng"], place["image_url"],
                place["address"], place["category"]
            ))
        
        # Then insert users and their data
        for user in users:
            # Insert user
            cursor.execute('''
            INSERT INTO users (
                name, email, password_hash, joined_date
            ) VALUES (?, ?, ?, ?)
            ''', (
                user["name"], user["email"], 
                user["password_hash"], user["joined_date"]
            ))
            user_id = cursor.lastrowid
            
            # Insert preferences
            for pref in user["preferences"]:
                cursor.execute('''
                INSERT INTO user_preferences (
                    user_id, preference_type, preference_value
                ) VALUES (?, ?, ?)
                ''', (user_id, "travel_style", pref))
            
            # Insert trips and itineraries
            for trip in user["trips"]:
                cursor.execute('''
                INSERT INTO trips (
                    user_id, title, destination, start_date, 
                    end_date, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, "NYC Trip", "New York",
                    trip["date"], trip["date"], "upcoming",
                    user["joined_date"], user["joined_date"]
                ))
                trip_id = cursor.lastrowid
                
                # Insert itinerary items
                for i, item in enumerate(trip["itinerary"]):
                    cursor.execute('''
                    INSERT INTO itinerary_items (
                        trip_id, place_id, day, start_time,
                        end_time, order_index
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        trip_id, item["place_id"], 1,
                        item["start_time"], item["end_time"], i + 1
                    ))
        
        conn.commit()
        print(f"Successfully inserted {len(users)} users and their data")
        
    except Exception as e:
        print(f"Error inserting data: {str(e)}")
        conn.rollback()
    
    finally:
        conn.close()

def main():
    # Load places
    places = load_places()
    
    # Generate users
    users = generate_users(100, places)  # Generate 100 users
    
    # Insert into database
    insert_into_database(users, places)

if __name__ == "__main__":
    main()

