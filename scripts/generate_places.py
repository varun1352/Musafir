import json
import requests
from cerebras.cloud.sdk import Cerebras
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Cerebras client
client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY"))

def get_image_url(place_name):
    """Get an image URL for a place using Cerebras."""
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant that provides image URLs for tourist places."},
            {"role": "user", "content": f"Give me a high-quality image URL for {place_name} in New York City. The image should be a real photograph, not AI-generated."}
        ]
        
        response = client.chat.completions.create(
            messages=messages,
            model="llama3.1-8b"
        )
        
        # Extract URL from response
        url = response.choices[0].message.content.strip()
        
        # Try to download the image to verify it works
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return url
        except:
            pass
            
    except Exception as e:
        print(f"Error getting image for {place_name}: {str(e)}")
    
    # Return placeholder if no image found
    return f"/placeholder.svg?height=400&width=600&text={place_name}"

# Define iconic NYC places with accurate coordinates
iconic_places = [
    {
        "name": "Empire State Building",
        "address": "350 5th Ave, New York, NY 10118",
        "lat": 40.7484,
        "lng": -73.9857,
        "description": "Iconic 102-story skyscraper with observation decks offering panoramic city views.",
        "visit_duration": 120,  # in minutes
        "typical_times": ["09:00", "11:00", "14:00", "16:00", "19:00"],
        "category": "Landmark"
    },
    {
        "name": "Times Square",
        "address": "Manhattan, NY 10036",
        "lat": 40.7580,
        "lng": -73.9855,
        "description": "Iconic intersection known for its bright lights, Broadway theaters, and vibrant atmosphere.",
        "visit_duration": 60,
        "typical_times": ["10:00", "14:00", "16:00", "19:00", "21:00"],
        "category": "Entertainment"
    },
    {
        "name": "Central Park",
        "address": "Central Park, New York, NY",
        "lat": 40.7829,
        "lng": -73.9654,
        "description": "Sprawling urban park with various attractions including Belvedere Castle and Bethesda Fountain.",
        "visit_duration": 180,
        "typical_times": ["08:00", "10:00", "14:00", "16:00"],
        "category": "Park"
    },
    {
        "name": "Metropolitan Museum of Art",
        "address": "1000 5th Ave, New York, NY 10028",
        "lat": 40.7794,
        "lng": -73.9632,
        "description": "World-renowned art museum featuring extensive collections spanning 5,000 years of culture.",
        "visit_duration": 180,
        "typical_times": ["10:00", "12:00", "14:00", "16:00"],
        "category": "Museum"
    },
    {
        "name": "Rockefeller Center",
        "address": "45 Rockefeller Plaza, New York, NY 10111",
        "lat": 40.7587,
        "lng": -73.9787,
        "description": "Historic complex known for its Art Deco architecture, shops, and observation deck.",
        "visit_duration": 120,
        "typical_times": ["09:00", "11:00", "14:00", "16:00", "19:00"],
        "category": "Landmark"
    },
    {
        "name": "Brooklyn Bridge",
        "address": "Brooklyn Bridge, New York, NY 10038",
        "lat": 40.7061,
        "lng": -73.9969,
        "description": "Historic bridge offering stunning views of Manhattan and Brooklyn.",
        "visit_duration": 60,
        "typical_times": ["08:00", "10:00", "16:00", "19:00"],
        "category": "Landmark"
    },
    {
        "name": "One World Trade Center",
        "address": "285 Fulton St, New York, NY 10007",
        "lat": 40.7127,
        "lng": -74.0134,
        "description": "Tallest building in the Western Hemisphere with observation deck offering city views.",
        "visit_duration": 120,
        "typical_times": ["09:00", "11:00", "14:00", "16:00", "19:00"],
        "category": "Landmark"
    },
    {
        "name": "High Line",
        "address": "New York, NY 10011",
        "lat": 40.7480,
        "lng": -74.0048,
        "description": "Elevated park built on a former railway line featuring gardens and art installations.",
        "visit_duration": 90,
        "typical_times": ["10:00", "12:00", "15:00", "17:00"],
        "category": "Park"
    }
]

def main():
    # Add images to places
    for place in iconic_places:
        place["image_url"] = get_image_url(place["name"])
    
    # Save to JSON file
    with open('nyc_places.json', 'w') as f:
        json.dump(iconic_places, f, indent=2)
    
    print(f"Generated {len(iconic_places)} places with images")

if __name__ == "__main__":
    main()

