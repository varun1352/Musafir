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
from dotenv import load_dotenv
from database import Database

load_dotenv()

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

# Add this new function
def geocode_address(address):
    """Convert an address to geographic coordinates (latitude and longitude)."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': address,
        'format': 'json'
    }
    
    headers = {
        'User-Agent': 'Musafir Travel App (your_email@example.com)'  # Replace with your app name and email
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data:
            latitude = float(data[0]['lat'])
            longitude = float(data[0]['lon'])
            return latitude, longitude
        else:
            print(f"No geocoding results found for address: {address}")
            return None, None
    
    except requests.exceptions.RequestException as e:
        print(f"Error: Unable to connect to the geocoding service. Details: {e}")
        return None, None
    except ValueError as ve:
        print(f"Error: {ve}")
        return None, None

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
            'image': 'images/cultural1.jpg',
            'travelers': 1200,
            'trips': 450
        },
        {
            'name': 'Paris, France',
            'description': 'Discover the city of lights and romance',
            'image': 'images/paris1.jpg',
            'travelers': 980,
            'trips': 380
        },
        {
            'name': 'New York, USA',
            'description': 'The city that never sleeps awaits your adventure',
            'image': 'images/nyc.jpg',
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
            Use Markdown formatting for better readability. But one very important thing to follow is that you will only suggest places which have specific addreses whcih are accessible in your knowledge and only sureshort addresses which would actually give lat-long when the system runs the geocoding api on the provided addresses. SKIP PLACES LIKE LIBERY ISLAND AND STATURE OF LIBERY, PARKS, WEIRD OPEN PALCES WHICH DONT HAVE A SPECIFIC ADDRESS. Very important thing to follow is that you will only suggest places which have specific addreses whcih are accessible in your knowledge and only sureshort addresses which would actually give lat-long when the system runs the geocoding api on the provided addresses. But one very important thing to follow is that you will only suggest places which have specific addreses whcih are accessible in your knowledge and only sureshort addresses which would actually give lat-long when the system runs the geocoding api on the provided addresses"""},
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

# Update the finalize_trip function
@app.route("/finalize_trip", methods=["POST"])
def finalize_trip():
    """Generates final itinerary in both Markdown and JSON formats."""
    try:
        global final_markdown, final_json
        
        # If this is a dynamic plan submission
        if request.json.get('dynamic_plan'):
            places = request.json.get('places', [])
            # Convert dynamic plan to itinerary format
            itinerary_text = "Here's your trip itinerary:\n\n"
            for place in places:
                itinerary_text += f"- Visit {place['name']}\n"
                itinerary_text += f"  * {place['description']}\n"
                itinerary_text += f"  * Time: {place['time']}\n\n"
            
            combined_itinerary = itinerary_text
        else:
            combined_itinerary = "\n".join(user_itinerary)

        # Generate Markdown itinerary with addresses
        messages_markdown = [
            {"role": "system", "content": (
                "You are an expert travel planner. Generate a structured markdown itinerary. "
                "For each place, include its full address in parentheses after the place name.  Also in the itinerary only include the place which has an actual address otherwise skip the places which have generic named addresses. SO FOR THE ADDRESS ATTRIBUTE IN THE JSON FOR EACH OF THE LOCATION IF THE LOCATION THAT YOU HAVE THOUGHT OF DOESNT HAVE AN ADDRESS THAT WOULD BE VIABLE TO DETECT THEN JUST SKIP THAT AND USE SOME OTHER PLACE THAT WOUDL AHVE A PERFECT. THESE PLACES wouldnt work for geocoding because we also need to extract the lat long ahead so places like statue of liberty would be difficult because theres no official address of the liberty island. "
                "Example: '## Central Park (Central Park, New York, NY 10022, USA)'"
            )},
            {"role": "user", "content": f"Create a detailed itinerary with addresses for:\n\n{combined_itinerary}"}
        ]

        final_markdown = call_cerebras_api(messages_markdown)

        # Generate JSON itinerary with addresses
        json_prompt = (
            "Generate a JSON itinerary with full addresses. Output format:\n"
            "{\n"
            "  \"trip\": {\n"
            "    \"destination\": \"<city, country>\",\n"
            "    \"dates\": {\"start\": \"YYYY-MM-DD\", \"end\": \"YYYY-MM-DD\"},\n"
            "    \"itinerary\": [\n"
            "      {\n"
            "        \"day\": <number>,\n"
            "        \"date\": \"YYYY-MM-DD\",\n"
            "        \"activities\": [\n"
            "          {\n"
            "            \"time\": \"<time>\",\n"
            "            \"place\": \"<place name>\",\n"
            "            \"address\": \"<full address>\",\n"
            "            \"description\": \"<details>\",\n"
            "            \"expected_time\": \"<duration>\"\n"
            "          }\n"
            "        ]\n"
            "      }\n"
            "    ]\n"
            "  }\n"
            "}\n\n"
            f"Based on this plan:\n\n{combined_itinerary}"
        )

        messages_json = [
            {"role": "system", "content": "You are an expert travel planner."},
            {"role": "user", "content": json_prompt}
        ]
        
        json_response = call_cerebras_api(messages_json)
        if json_response:
            json_match = re.search(r'(\{[\s\S]*\})', json_response)
            if json_match:
                json_str = json_match.group(1)
                final_json = json.loads(json_str)
                
                # Add geocoding for each activity
                for day in final_json['trip']['itinerary']:
                    for activity in day['activities']:
                        lat, lon = geocode_address(activity['address'])
                        if lat and lon:
                            activity['latitude'] = lat
                            activity['longitude'] = lon
                
                # Store in database if user is logged in
                if 'user_id' in session:
                    trip_id = db.store_json_itinerary(final_json, session['user_id'])
                    if trip_id:
                        session['current_trip_id'] = trip_id
                        return jsonify({"finalized": True, "trip_id": trip_id})

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

# Add the dynamic planning route
@app.route('/dynamic_plan')
@login_required
def dynamic_plan():
    """Renders the dynamic planning page."""
    user = get_current_user()
    return render_template('dynamic_plan.html', user=user)

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
            'image': 'images/cultural2.jpg',
            'duration': '7 days',
            'rating': 4.8,
            'reviews': 124,
            'highlights': ['Mt. Fuji', 'Shibuya', 'Temples']
        },
        {
            'title': 'Paris Romance',
            'image': 'images/paris1.jpg',
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

# Add these new routes
@app.route('/api/request_contact', methods=['POST'])
@login_required
def request_contact():
    """Handle contact request between travelers."""
    try:
        traveler_id = request.json.get('traveler_id')
        if not traveler_id:
            return jsonify({"error": "No traveler specified"}), 400

        # Create contact request
        token = db.create_contact_request(session['user_id'], traveler_id)
        if not token:
            return jsonify({"error": "Contact request already exists"}), 400

        # Get user details
        from_user = db.get_user_by_id(session['user_id'])
        to_user = db.get_user_by_id(traveler_id)

        if not to_user or not to_user['email']:
            return jsonify({"error": "Unable to send request"}), 400

        # Send email
        approval_link = url_for('approve_contact', token=token, _external=True)
        send_contact_request_email(to_user['email'], from_user['name'], approval_link)

        return jsonify({"success": True})

    except Exception as e:
        print(f"Error in request_contact: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500

@app.route('/approve_contact/<token>')
def approve_contact(token):
    """Handle contact request approval."""
    try:
        request = db.get_contact_request_by_token(token)
        if not request:
            flash('Invalid or expired request', 'error')
            return redirect(url_for('index'))

        if request['status'] != 'pending':
            flash('This request has already been processed', 'info')
            return redirect(url_for('index'))

        if db.approve_contact_request(token):
            # Get user details
            from_user = db.get_user_by_id(request['from_user_id'])
            to_user = db.get_user_by_id(request['to_user_id'])

            # Send email to requester with the approved user's email
            send_approval_email(from_user['email'], to_user['name'], to_user['email'])
            
            flash('Contact request approved! The other traveler will be notified.', 'success')
        else:
            flash('Unable to process request', 'error')

        return redirect(url_for('index'))

    except Exception as e:
        print(f"Error in approve_contact: {str(e)}")
        flash('An error occurred', 'error')
        return redirect(url_for('index'))

def send_contact_request_email(to_email, from_name, approval_link):
    """Send contact request email."""
    # TODO: Implement email sending
    # For now, just print the email content
    print(f"""
    To: {to_email}
    Subject: New Contact Request from {from_name}
    
    You have received a contact request from {from_name} on Musafir.
    
    To approve sharing your contact details, click here:
    {approval_link}
    """)

def send_approval_email(to_email, approved_name, approved_email):
    """Send approval notification email."""
    # TODO: Implement email sending
    # For now, just print the email content
    print(f"""
    To: {to_email}
    Subject: Contact Request Approved
    
    Good news! {approved_name} has approved your contact request.
    
    You can now reach them at: {approved_email}
    """)

if __name__ == "__main__":
    app.run(debug=True)

