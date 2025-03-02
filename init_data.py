import random
from datetime import datetime, timedelta
import names
from faker import Faker
import requests

fake = Faker()

# Default placeholder image URL if the image URL is not valid
DEFAULT_IMAGE_URL = "https://via.placeholder.com/400x600.png?text=NYC+Placeholder"

# List of iconic NYC places with proper coordinates and details.
NYC_PLACES = [
    {
        "name": "Empire State Building",
        "address": "350 5th Ave, New York, NY 10118",
        "lat": 40.7484,
        "lng": -73.9857,
        "description": "Iconic skyscraper with observation decks offering panoramic views.",
        "visit_duration": 120,  # in minutes
        "typical_times": ["09:00", "11:00", "14:00", "16:00", "19:00"],
        "category": "Landmark",
        "image_url": "https://example.com/empire.jpg"
    },
    {
        "name": "Times Square",
        "address": "Manhattan, NY 10036",
        "lat": 40.7580,
        "lng": -73.9855,
        "description": "Bustling intersection known for its bright lights and theaters.",
        "visit_duration": 60,
        "typical_times": ["10:00", "14:00", "16:00", "19:00", "21:00"],
        "category": "Entertainment",
        "image_url": "https://example.com/timessquare.jpg"
    },
    {
        "name": "Central Park",
        "address": "Central Park, New York, NY",
        "lat": 40.7829,
        "lng": -73.9654,
        "description": "Sprawling urban park featuring lakes, gardens, and scenic trails.",
        "visit_duration": 180,
        "typical_times": ["08:00", "10:00", "14:00", "16:00"],
        "category": "Park",
        "image_url": "https://example.com/centralpark.jpg"
    },
    {
        "name": "Metropolitan Museum of Art",
        "address": "1000 5th Ave, New York, NY 10028",
        "lat": 40.7794,
        "lng": -73.9632,
        "description": "World-renowned art museum with collections spanning 5,000 years.",
        "visit_duration": 180,
        "typical_times": ["10:00", "12:00", "14:00", "16:00"],
        "category": "Museum",
        "image_url": "https://example.com/met.jpg"
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
        "image_url": "https://example.com/brooklynbridge.jpg"
    },
    {
        "name": "One World Trade Center",
        "address": "285 Fulton St, New York, NY 10007",
        "lat": 40.7127,
        "lng": -74.0134,
        "description": "Tallest building in the Western Hemisphere with breathtaking views.",
        "visit_duration": 120,
        "typical_times": ["09:00", "11:00", "14:00", "16:00", "19:00"],
        "category": "Landmark",
        "image_url": "https://example.com/oneworld.jpg"
    },
    {
        "name": "High Line",
        "address": "New York, NY 10011",
        "lat": 40.7480,
        "lng": -74.0048,
        "description": "Elevated park built on a former rail line featuring gardens and art.",
        "visit_duration": 90,
        "typical_times": ["10:00", "12:00", "15:00", "17:00"],
        "category": "Park",
        "image_url": "https://example.com/highline.jpg"
    }
]

def is_image_url_valid(url):
    """Check if an image URL is reachable via a HEAD request."""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def generate_itinerary(places, date):
    """
    Generate a random itinerary for a given day.
    Selects between 2 to 4 places (randomly) from the list.
    """
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

def create_dummy_data(cursor):
    """Initialize database with dummy data for testing."""
    
    # Insert places
    for place in NYC_PLACES:
        image_url = place.get("image_url")
        if not image_url or not is_image_url_valid(image_url):
            image_url = DEFAULT_IMAGE_URL
        cursor.execute("""
            INSERT OR IGNORE INTO places (name, description, latitude, longitude, image_url, address, place_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            place["name"],
            place["description"],
            place["lat"],
            place["lng"],
            image_url,
            place["address"],
            place["category"]
        ))
    
    # Generate 100 users with trips and itineraries for the next three days in NYC
    for _ in range(100):
        first_name = names.get_first_name()
        last_name = names.get_last_name()
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"
        full_name = f"{first_name} {last_name}"
        joined_date = datetime.now().strftime("%Y-%m-%d")
        dummy_password = "pbkdf2:sha256:150000$dummy"  # Dummy hash
        
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, joined_date)
            VALUES (?, ?, ?, ?)
        """, (full_name, email, dummy_password, joined_date))
        user_id = cursor.lastrowid
        
        # Assign 2-4 random preferences
        preferences = random.sample([
            "Cultural", "Adventure", "Photography", "Food",
            "History", "Art", "Architecture", "Nature"
        ], random.randint(2, 4))
        for pref in preferences:
            cursor.execute("""
                INSERT INTO user_preferences (user_id, preference_type, preference_value)
                VALUES (?, ?, ?)
            """, (user_id, "travel_style", pref))
        
        # Create one trip per user spanning the next three days
        now = datetime.now()
        start_date = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = (now + timedelta(days=3)).strftime("%Y-%m-%d")
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO trips (user_id, title, destination, start_date, end_date, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, f"NYC Trip by {full_name}", "New York", start_date, end_date, "upcoming", now_str, now_str))
        trip_id = cursor.lastrowid
        
        # For each of the three days, generate itinerary items
        for day_offset in range(3):
            trip_date = now + timedelta(days=1+day_offset)
            itinerary = generate_itinerary(NYC_PLACES, trip_date)
            for i, item in enumerate(itinerary):
                # Retrieve the place id based on the name
                cursor.execute("SELECT id FROM places WHERE name = ?", (item["place"]["name"],))
                row = cursor.fetchone()
                if row:
                    place_id = row["id"]
                    cursor.execute("""
                        INSERT INTO itinerary_items (trip_id, place_id, day, start_time, end_time, notes, order_index)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        trip_id,
                        place_id,
                        day_offset + 1,
                        item["start_time"],
                        item["end_time"],
                        f"Visit {item['place']['name']}",
                        i + 1
                    ))
    
    cursor.connection.commit()
    print("Successfully initialized database with dummy data")
