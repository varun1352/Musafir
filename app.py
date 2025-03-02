from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, g, Response
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import json
import re
from datetime import datetime, timedelta
import requests
from cerebras.cloud.sdk import Cerebras
from datetime import timedelta

from database import Database
# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Cerebras API configuration
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")

client = Cerebras(api_key=CEREBRAS_API_KEY)
# Upload folder configuration
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Initialize database
db = Database()

# Global variables for storing temporary itineraries
user_itinerary = []  # Stores user inputs for refining the itinerary
final_markdown = ""  # Stores the finalized itinerary in markdown format
final_json = {}     # Stores the finalized itinerary as JSON

@app.teardown_appcontext
def close_db(error):
    """Close the database connection at the end of each request."""
    if hasattr(g, 'db'):
        g.db.close_connection()

@app.before_request
def before_request():
    """Set up database connection for the request."""
    g.db = db

def login_required(f):
    """Decorator to require login for a route."""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def get_current_user():
    """Get the current logged-in user."""
    if 'user_id' in session:
        return db.get_user_by_id(session['user_id'])
    return None

def call_cerebras_api(messages):
    """Calls the Cerebras API with the given messages array."""
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3.1-8b"
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def store_json_itinerary(json_data, user_id=None):
    """Store the JSON itinerary in the database."""
    try:
        trip = json_data.get('trip', {})
        destination = trip.get('destination', 'Unknown')
        dates = trip.get('dates', {})
        start_date = dates.get('start')
        end_date = dates.get('end')

        # Create trip in database
        trip_id = db.create_trip(
            user_id=user_id,
            title=f"Trip to {destination}",
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            status='upcoming'
        )

        # Store itinerary items
        for day in trip.get('itinerary', []):
            day_num = day['day']
            for activity in day.get('activities', []):
                # Create or get place
                place_data = {
                    'name': activity['place'],
                    'description': activity['description'],
                    'latitude': 0.0,  # You would need to get real coordinates
                    'longitude': 0.0,  # You would need to get real coordinates
                }
                place_id = db.create_place(**place_data)

                # Add itinerary item
                db.add_itinerary_item(
                    trip_id=trip_id,
                    place_id=place_id,
                    day=day_num,
                    start_time=activity['time'],
                    end_time=activity['time'],  # You would calculate this from expected_time
                    notes=activity['description'],
                    order_index=day_num
                )

        return trip_id
    except Exception as e:
        print(f"Error storing itinerary: {str(e)}")
        return None

# Add this new route to handle placeholder images
@app.route('/placeholder.svg')
def placeholder():
    """Generate a placeholder SVG image."""
    width = request.args.get('width', 300)
    height = request.args.get('height', 200)
    
    svg = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#f0f0f0"/>
        <text x="50%" y="50%" font-family="Arial" font-size="14" 
              fill="#666" text-anchor="middle" dy=".3em">
            {width}x{height}
        </text>
    </svg>'''
    
    return Response(svg, mimetype='image/svg+xml')

@app.route('/')
def index():
    user = get_current_user()
    
    # Sample data for popular destinations
    popular_destinations = [
        {
            'name': 'Tokyo, Japan',
            'description': 'Experience the perfect blend of tradition and modernity',
            'image': '/placeholder.svg?height=200&width=300',
            'travelers': 1200,
            'trips': 450
        },
        {
            'name': 'Paris, France',
            'description': 'Discover the city of lights and romance',
            'image': '/placeholder.svg?height=200&width=300',
            'travelers': 980,
            'trips': 380
        },
        {
            'name': 'New York, USA',
            'description': 'The city that never sleeps awaits your adventure',
            'image': '/placeholder.svg?height=200&width=300',
            'travelers': 850,
            'trips': 320
        }
    ]
    
    testimonials = [
        {
            'name': 'Sarah Johnson',
            'text': 'Musafir made planning my trip to Japan so easy!',
            'avatar': '/placeholder.svg?height=48&width=48',
            'trip': 'Tokyo Adventure'
        },
        {
            'name': 'Michael Chen',
            'text': 'The interactive map feature helped me discover hidden gems in Paris.',
            'avatar': '/placeholder.svg?height=48&width=48',
            'trip': 'Paris Explorer'
        },
        {
            'name': 'Emma Davis',
            'text': 'Made some great friends during my trip to New York!',
            'avatar': '/placeholder.svg?height=48&width=48',
            'trip': 'NYC Weekend'
        }
    ]
    
    return render_template('index.html', 
                         user=user,
                         popular_destinations=popular_destinations,
                         testimonials=testimonials)

@app.route('/travel_planner')
def travel_planner():
    """Renders the travel planner page with chat interface."""
    user = get_current_user()
    return render_template('travelPlanner.html', user=user)

@app.route("/process_text", methods=["POST"])
def process_text():
    """Handles user messages to refine the itinerary."""
    user_text = request.json.get("message", "")
    if not user_text:
        return jsonify({"error": "No message provided"}), 400

    user_itinerary.append(user_text)

    messages = [
        {"role": "system", "content": "You are a travel assistant helping users plan a structured travel itinerary. Format your responses using Markdown for better readability. Use headers, bullet points, and emphasis where appropriate."},
        {"role": "user", "content": f"Refine this trip itinerary based on the following user input:\n\n{user_text}\n\nEnsure clarity and keep a structured format with proper Markdown formatting."}
    ]

    itinerary_response = call_cerebras_api(messages)
    return jsonify({"response": itinerary_response})

@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    """Handles PDF uploads and extracts structured itinerary."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not file.filename.endswith('.pdf'):
            return jsonify({"error": "File must be a PDF"}), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        messages = [
            {"role": "system", "content": """You are a travel assistant that processes uploaded PDF itineraries.
            Extract the key information and format it as a clear, structured itinerary.
            Use Markdown formatting for better readability."""},
            {"role": "user", "content": f"Extract and structure the travel itinerary from this PDF: {filename}"}
        ]

        response = call_cerebras_api(messages)
        if response:
            user_itinerary.append(response)
            return jsonify({"response": response})
        else:
            return jsonify({"error": "Failed to process PDF"}), 500

    except Exception as e:
        print(f"Error in upload_pdf: {str(e)}")
        return jsonify({"error": "An error occurred processing your PDF"}), 500

@app.route("/finalize_trip", methods=["POST", "GET"])
def finalize_trip():
    """Generates final itinerary in both Markdown and JSON formats."""
    try:
        global final_markdown, final_json
        
        combined_itinerary = "\n".join(user_itinerary)

        # Generate Markdown itinerary
        messages_markdown = [
            {"role": "system", "content": (
                "You are an expert travel planner. Your task is to generate a structured, well-formatted markdown travel itinerary. "
                "Use proper Markdown syntax with headers (# for main headers, ## for subheaders), bullet points, emphasis (**bold** and *italic*), and horizontal rules (---) where appropriate."
            )},
            {"role": "user", "content": (
                f"Generate a final, markdown-formatted itinerary based on this travel plan:\n\n{combined_itinerary}\n\n"
                "Use clear headers, bullet points, and markdown elements for easy readability. The final itinerary should look like a well-structured travel guide."
            )}
        ]

        final_markdown = call_cerebras_api(messages_markdown)
        print("Final Markdown itinerary:", final_markdown)

        # Generate JSON itinerary
        # 2. Generate JSON itinerary
        json_prompt = (
            "Generate a JSON itinerary for the following trip plan. Output only valid JSON without any extra text or markdown formatting. "
            "Ensure the output exactly follows this structure:\n\n"
            "{\n"
            "  \"trip\": {\n"
            "    \"destination\": \"<destination>\",\n"
            "    \"dates\": {\"start\": \"<YYYY-MM-DD>\", \"end\": \"<YYYY-MM-DD>\"},\n"
            "    \"itinerary\": [\n"
            "      {\n"
            "        \"day\": <day number>,\n"
            "        \"date\": \"<YYYY-MM-DD>\",\n"
            "        \"activities\": [\n"
            "          {\"time\": \"<time>\", \"place\": \"<place>\", \"description\": \"<details>\", \"expected_time\": \"<duration>\"}\n"
            "        ]\n"
            "      }\n"
            "    ]\n"
            "  }\n"
            "}\n\n"
            "Based on this travel plan:\n\n" + combined_itinerary
        )
        messages_json = [
            {"role": "system", "content": "You are an expert travel planner."},
            {"role": "user", "content": json_prompt}
        ]
        json_response = call_cerebras_api(messages_json)
        print("Raw JSON response:", json_response)

        if json_response:
            json_match = re.search(r'(\{[\s\S]*\})', json_response)
            if json_match:
                json_str = json_match.group(1)
                final_json = json.loads(json_str)
                
                # Store in database if user is logged in
                if 'user_id' in session:
                    trip_id = store_json_itinerary(final_json, session['user_id'])
                    if trip_id:
                        session['current_trip_id'] = trip_id

                return jsonify({"finalized": True})

        return jsonify({"error": "Failed to generate itinerary"}), 500

    except Exception as e:
        print(f"Error in finalize_trip: {str(e)}")
        return jsonify({"error": "An error occurred finalizing your trip"}), 500

@app.route("/view_itinerary")
def view_itinerary():
    """Displays the finalized itinerary."""
    user = get_current_user()
    trip_id = session.get('current_trip_id')
    
    if trip_id:
        # Get itinerary from database
        itinerary_md = db.generate_markdown_itinerary(trip_id)
        trip = db.get_trip_by_id(trip_id)  # Retrieve the trip details
        if itinerary_md:
            return render_template("itinerary.html", user=user, itinerary=itinerary_md, trip=trip)
    
    # Fallback to stored markdown with no trip details
    return render_template("itinerary.html", user=user, itinerary=final_markdown, trip=None)

@app.route('/map_view')
def map_view():
    user = get_current_user()
    trip_id = request.args.get('trip_id')
    
    if trip_id:
        map_data = db.get_trip_map_data(trip_id)
    else:
        map_data = None
    
    return render_template('map_view.html', user=user, map_data=map_data)

@app.route('/day_planner')
def day_planner():
    user = get_current_user()
    return render_template('dynamic_plan.html', user=user)

@app.route('/about')
def about():
    user = get_current_user()
    return render_template('about.html', user=user)

@app.route('/profile')
@login_required
def profile():
    user_id = session['user_id']
    profile_data = db.get_user_profile_data(user_id)
    
    if not profile_data:
        flash('User not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('profile.html', 
                         user=profile_data['user'],
                         trips=profile_data['trips'],
                         preferences=profile_data['preferences'])

@app.route('/explore')
def explore():
    user = get_current_user()
    
    # Sample featured trips (in production, get from database)
    featured = [
        {
            'title': 'Tokyo Adventure',
            'image': '/placeholder.svg?height=200&width=300',
            'duration': '7 days',
            'rating': 4.8,
            'reviews': 124,
            'highlights': ['Mt. Fuji', 'Shibuya', 'Temples']
        },
        {
            'title': 'Paris Romance',
            'image': '/placeholder.svg?height=200&width=300',
            'duration': '5 days',
            'rating': 4.7,
            'reviews': 98,
            'highlights': ['Eiffel Tower', 'Louvre', 'Seine River']
        }
    ]
    
    categories = [
        {
            'name': 'Adventure Trips',
            'trips': featured
        },
        {
            'name': 'Cultural Experiences',
            'trips': featured
        }
    ]
    
    return render_template('explore.html', 
                         user=user,
                         featured=featured,
                         categories=categories)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            name = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            preference = request.form.get('preference')
            
            if not all([name, email, password, preference]):
                flash('All fields are required.', 'error')
                return redirect(url_for('signup'))
            
            # Check if user exists
            existing_user = db.get_user_by_email(email)
            if existing_user:
                flash('Email already registered. Please log in.', 'warning')
                return redirect(url_for('login'))
            
            # Create user
            password_hash = generate_password_hash(password)
            user_id = db.create_user(name, email, password_hash)
            
            if user_id:
                # Add preference
                db.add_user_preference(user_id, 'travel_style', preference)
                
                # Log user in
                session['user_id'] = user_id
                flash('Account created successfully!', 'success')
                return redirect(url_for('profile'))
            else:
                flash('Error creating account. Please try again.', 'error')
        except Exception as e:
            print(f"Error during signup: {str(e)}")
            flash('An error occurred. Please try again.', 'error')
    
    return render_template('signup.html', user=None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = db.get_user_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('profile'))
        
        flash('Invalid email or password', 'error')
    
    return render_template('login.html', user=get_current_user())

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)

