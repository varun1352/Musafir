import random
from datetime import datetime, timedelta
import names
from faker import Faker
import json

fake = Faker()

# NYC Places with accurate coordinates
NYC_PLACES = [
    {
        "name": "Empire State Building",
        "address": "350 5th Ave, New York, NY 10118",
        "lat": 40.7484,
        "lng": -73.9857,
        "description": "Iconic 102-story skyscraper with observation decks offering panoramic city views.",
        "visit_duration": 120,  # in minutes
        "typical_times": ["09:00", "11:00", "14:00", "16:00", "19:00"],
        "category": "Landmark",
        "image_url": "/placeholder.svg?height=400&width=600&text=Empire+State+Building"
    },
    {
        "name": "Times Square",
        "address": "Manhattan, NY 10036",
        "lat": 40.7580,
        "lng": -73.9855,
        "description": "Iconic intersection known for its bright lights, Broadway theaters, and vibrant atmosphere.",
        "visit_duration": 60,
        "typical_times": ["10:00", "14:00", "16:00", "19:00", "21:00"],
        "category": "Entertainment",
        "image_url": "/placeholder.svg?height=400&width=600&text=Times+Square"
    },
    {
        "name": "Central Park",
        "address": "Central Park, New York, NY",
        "lat": 40.7829,
        "lng": -73.9654,
        "description": "Sprawling urban park with various attractions including Belvedere Castle and Bethesda Fountain.",
        "visit_duration": 180,
        "typical_times": ["08:00", "10:00", "14:00", "16:00"],
        "category": "Park",
        "image_url": "/placeholder.svg?height=400&width=600&text=Central+Park"
    },
    {
        "name": "Metropolitan Museum of Art",
        "address": "1000 5th Ave, New York, NY 10028",
        "lat": 40.7794,
        "lng": -73.9632,
        "description": "World-renowned art museum featuring extensive collections spanning 5,000 years of culture.",
        "visit_duration": 180,
        "typical_times": ["10:00", "12:00", "14:00", "16:00"],
        "category": "Museum",
        "image_url": "/placeholder.svg?height=400&width=600&text=Metropolitan+Museum"
    },
    {
        "name": "Rockefeller Center",
        "address": "45 Rockefeller Plaza, New York, NY 10111",
        "lat": 40.7587,
        "lng": -73.9787,
        "description": "Historic complex known for its Art Deco architecture, shops, and observation deck.",
        "visit_duration": 120,
        "typical_times": ["09:00", "11:00", "14:00", "16:00", "19:00"],
        "category": "Landmark",
        "image_url": "/placeholder.svg?height=400&width=600&text=Rockefeller+Center"
    },
    {
        "name": "Brooklyn Bridge",
        "address": "Brooklyn Bridge, New York, NY 10038",
        "lat": 40.7061,
        "lng": -73.9969,
        "description": "Historic bridge offering stunning views of Manhattan and Brooklyn.",
        "visit_duration": 60,
        "typical_times": ["08:00", "10:00", "16:00", "19:00"],
        "category": "Landmark",
        "image_url": "/placeholder.svg?height=400&width=600&text=Brooklyn+Bridge"
    },
    {
        "name": "One World Trade Center",
        "address": "285 Fulton St, New York, NY 10007",
        "lat": 40.7127,
        "lng": -74.0134,
        "description": "Tallest building in the Western Hemisphere with observation deck offering city views.",
        "visit_duration": 120,
        "typical_times": ["09:00", "11:00", "14:00", "16:00", "19:00"],
        "category": "Landmark",
        "image_url": "/placeholder.svg?height=400&width=600&text=One+World+Trade"
    },
    {
        "name": "High Line",
        "address": "New York, NY 10011",
        "lat": 40.7480,
        "lng": -74.0048,
        "description": "Elevated park built on a former railway line featuring gardens and art installations.",
        "visit_duration": 90,
        "typical_times": ["10:00", "12:00", "15:00", "17:00"],
        "category": "Park",
        "image_url": "/placeholder.svg?height=400&width=600&text=High+Line"
    }
]

def generate_itinerary(places, date):
    """Generate a random itinerary for a day."""
    num_places = random.randint(2, 4)
    selected_places = random.sample(places, num_places)
    
    itinerary = []
    current_time = datetime.strptime("09:00", "%H:%M")
    
    for place in selected_places:
        valid_times = [
            datetime.strptime(t, "%H:%M") 
            for t in place["typical_times"]
            if datetime.strptime(t, "%H:%M") >= current_time
        ]
        
        if valid_times:
            visit_time = min(valid_times)
            end_time = visit_time + timedelta(minutes=place["visit_duration"])
            
            itinerary.append({
                "place": place,
                "start_time": visit_time.strftime("%H:%M"),
                "end_time": end_time.strftime("%H:%M"),
                "date": date.strftime("%Y-%m-%d")
            })
            
            current_time = end_time + timedelta(minutes=30)
    
    return itinerary

def create_dummy_data(db):
    """Initialize database with dummy places and users."""
    try:
        # First, insert all places
        for place in NYC_PLACES:
            db.execute("""
                INSERT INTO places (name, description, latitude, longitude, 
                                  image_url, address, place_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                place["name"], place["description"], place["lat"], 
                place["lng"], place["image_url"], place["address"], 
                place["category"]
            ))
        
        # Generate 100 users with their trips
        for _ in range(100):
            # Create user
            first_name = names.get_first_name()
            last_name = names.get_last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            
            db.execute("""
                INSERT INTO users (name, email, password_hash, joined_date)
                VALUES (?, ?, ?, ?)
            """, (
                f"{first_name} {last_name}",
                email,
                "pbkdf2:sha256:150000$dummy_hash",  # Dummy hash for testing
                datetime.now().strftime("%Y-%m-%d")
            ))
            user_id = db.lastrowid()
            
            # Add preferences
            preferences = random.sample([
                "Cultural", "Adventure", "Photography", "Food", 
                "History", "Art", "Architecture", "Nature"
            ], random.randint(2, 4))
            
            for pref in preferences:
                db.execute("""
                    INSERT INTO user_preferences (user_id, preference_type, preference_value)
                    VALUES (?, ?, ?)
                """, (user_id, "travel_style", pref))
            
            # Create trips for next three days
            now = datetime.now()
            for day in range(3):
                trip_date = now + timedelta(days=day)
                
                # Create trip
                db.execute("""
                    INSERT INTO trips (user_id, title, destination, start_date, 
                                     end_date, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    "NYC Trip",
                    "New York",
                    trip_date.strftime("%Y-%m-%d"),
                    trip_date.strftime("%Y-%m-%d"),
                    "upcoming",
                    now.strftime("%Y-%m-%d"),
                    now.strftime("%Y-%m-%d")
                ))
                trip_id = db.lastrowid()
                
                # Generate and add itinerary items
                itinerary = generate_itinerary(NYC_PLACES, trip_date)
                for i, item in enumerate(itinerary):
                    place = item["place"]
                    db.execute("""
                        INSERT INTO itinerary_items (trip_id, place_id, day, 
                                                   start_time, end_time, order_index)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        trip_id,
                        NYC_PLACES.index(place) + 1,  # place_id
                        1,
                        item["start_time"],
                        item["end_time"],
                        i + 1
                    ))
        
        db.commit()
        print("Successfully initialized database with dummy data")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        db.rollback()

