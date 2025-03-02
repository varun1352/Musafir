from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, g
import os
import json
import secrets
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import requests
from database import Database
#from flask_oauthlib.client import OAuth # Removed

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Initialize database
db = Database()

@app.teardown_appcontext
def close_db(error):
    """Close the database connection at the end of each request."""
    if hasattr(g, 'db'):
        g.db.close_connection()

@app.before_request
def before_request():
    """Set up database connection for the request."""
    g.db = db

# Setup OAuth
#oauth = OAuth(app) # Removed
#google = oauth.remote_app( # Removed
#    'google',
#    consumer_key=os.environ.get('GOOGLE_CLIENT_ID', ''),
#    consumer_secret=os.environ.get('GOOGLE_CLIENT_SECRET', ''),
#    request_token_params={
#        'scope': 'email profile'
#    },
#    base_url='https://www.googleapis.com/oauth2/v1/',
#    request_token_url=None,
#    access_token_method='POST',
#    access_token_url='https://accounts.google.com/o/oauth2/token',
#    authorize_url='https://accounts.google.com/o/oauth2/auth',
#)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Helper functions
def login_required(f):
    """Decorator to require login for a route."""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login')) # Changed from google_auth to login
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def get_current_user():
    """Get the current logged-in user."""
    if 'user_id' in session:
        return db.get_user_by_id(session['user_id'])
    return None

# Routes
@app.route('/')
def index():
    user = get_current_user()
    return render_template('index.html', user=user)

@app.route('/about')
def about():
    user = get_current_user()
    return render_template('about.html', user=user)

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
            
            # Check if user already exists
            existing_user = g.db.get_user_by_email(email)
            if existing_user:
                flash('Email already registered. Please log in.', 'warning')
                return redirect(url_for('login'))
            
            # Hash the password
            password_hash = generate_password_hash(password)
            
            # Create user
            user_id = g.db.create_user(name, email, password_hash)
            
            if user_id:
                # Add user preference
                g.db.add_user_preference(user_id, 'travel_style', preference)
                
                # Log the user in
                session['user_id'] = user_id
                flash('Account created successfully!', 'success')
                return redirect(url_for('profile'))
            else:
                flash('Error creating account. Please try again.', 'error')
        except Exception as e:
            app.logger.error(f"Error during signup: {str(e)}")
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

#@app.route('/auth/google') # Removed
#def google_auth():
#    user = get_current_user()
#    if user:
#        return redirect(url_for('profile'))
#    return render_template('google_auth.html', user=user)

#@app.route('/auth/google/redirect') # Removed
#def google_auth_redirect():
#    return google.authorize(callback=url_for('google_callback', _external=True))

#@app.route('/auth/google/callback') # Removed
#def google_callback():
#    resp = google.authorized_response()
#    if resp is None or resp.get('access_token') is None:
#        flash('Access denied: reason={} error={}'.format(
#            request.args.get('error_reason'),
#            request.args.get('error_description')
#        ), 'error')
#        return redirect(url_for('google_auth'))
#    
#    session['google_token'] = (resp['access_token'], '')
#    user_info = google.get('userinfo')
#    
#    # Check if user exists
#    google_id = user_info.data['id']
#    email = user_info.data['email']
#    
#    user = db.get_user_by_google_id(google_id)
#    if not user:
#        # Check if email exists
#        user = db.get_user_by_email(email)
#        if user:
#            # Update existing user with Google ID
#            db.update_user(user['id'], google_id=google_id)
#        else:
#            # Create new user
#            name = user_info.data.get('name', email.split('@')[0])
#            profile_image = user_info.data.get('picture')
#            
#            user_id = db.create_user(
#                name=name,
#                email=email,
#                google_id=google_id,
#                profile_image=profile_image
#            )
#            
#            if not user_id:
#                flash('Error creating account. Please try again.', 'error')
#                return redirect(url_for('google_auth'))
#            
#            user = db.get_user_by_id(user_id)
#    
#    # Log the user in
#    session['user_id'] = user['id']
#    flash('Logged in successfully!', 'success')
#    return redirect(url_for('profile'))

#@google.tokengetter # Removed
#def get_google_oauth_token():
#    return session.get('google_token')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    #session.pop('google_token', None) # Removed
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    user_id = session['user_id']
    profile_data = db.get_user_profile_data(user_id)
    
    if not profile_data:
        flash('User not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('profile.html', user=profile_data['user'], trips=profile_data['trips'], preferences=profile_data['preferences'])

@app.route('/map_view')
def map_view():
    user = get_current_user()
    
    # For demo purposes, use the first trip if available
    trip_id = request.args.get('trip_id')
    if not trip_id and user:
        trips = db.get_user_trips(user['id'])
        if trips:
            trip_id = trips[0]['id']
    
    map_data = None
    if trip_id:
        map_data = db.get_trip_map_data(trip_id)
    
    return render_template('map_view.html', user=user, map_data=map_data)

@app.route('/day_planner')
def day_planner():
    user = get_current_user()
    return render_template('dynamic_plan.html', user=user)

@app.route('/explore')
def explore():
    user = get_current_user()
    
    # Sample data for the explore page
    featured = [
        {
            'title': 'Tokyo Adventure',
            'image': 'tokyo.jpg',
            'duration': '7 days',
            'rating': 4.8,
            'reviews': 124,
            'highlights': ['Mt. Fuji', 'Shibuya', 'Temples']
        },
        {
            'title': 'Paris Romance',
            'image': 'paris.jpg',
            'duration': '5 days',
            'rating': 4.7,
            'reviews': 98,
            'highlights': ['Eiffel Tower', 'Louvre', 'Seine River']
        },
        {
            'title': 'New York City',
            'image': 'nyc.jpg',
            'duration': '4 days',
            'rating': 4.6,
            'reviews': 156,
            'highlights': ['Times Square', 'Central Park', 'Museums']
        }
    ]
    
    categories = [
        {
            'name': 'Adventure Trips',
            'trips': [
                {
                    'title': 'Hiking in Nepal',
                    'image': 'nepal.jpg',
                    'duration': '10 days',
                    'rating': 4.9
                },
                {
                    'title': 'Safari in Kenya',
                    'image': 'kenya.jpg',
                    'duration': '8 days',
                    'rating': 4.8
                },
                {
                    'title': 'Amazon Rainforest',
                    'image': 'amazon.jpg',
                    'duration': '6 days',
                    'rating': 4.7
                },
                {
                    'title': 'Iceland Road Trip',
                    'image': 'iceland.jpg',
                    'duration': '7 days',
                    'rating': 4.9
                }
            ]
        },
        {
            'name': 'Beach Getaways',
            'trips': [
                {
                    'title': 'Bali Paradise',
                    'image': 'bali.jpg',
                    'duration': '6 days',
                    'rating': 4.8
                },
                {
                    'title': 'Maldives Luxury',
                    'image': 'maldives.jpg',
                    'duration': '5 days',
                    'rating': 4.9
                },
                {
                    'title': 'Greek Islands',
                    'image': 'greece.jpg',
                    'duration': '8 days',
                    'rating': 4.7
                },
                {
                    'title': 'Caribbean Cruise',
                    'image': 'caribbean.jpg',
                    'duration': '7 days',
                    'rating': 4.6
                }
            ]
        }
    ]
    
    return render_template('explore.html', user=user, featured=featured, categories=categories)

@app.route('/travel_planner')
@login_required
def travel_planner():
    user = get_current_user()
    return render_template('travelPlanner.html', user=user)

@app.route('/process_text', methods=['POST'])
@login_required
def process_text():
    data = request.json
    user_message = data.get('message', '')
    
    # Get or create a chat session
    user_id = session['user_id']
    chat_sessions = db.get_user_chat_sessions(user_id)
    
    if chat_sessions:
        session_id = chat_sessions[0]['id']
    else:
        session_id = db.create_chat_session(user_id)
    
    # Save user message
    db.add_chat_message(session_id, 'user', user_message)
    
    # Process the message (in a real app, this would call an LLM API)
    # For now, just return a simple response
    response = f"I've received your travel plans for: '{user_message}'. I'll help you create an itinerary based on this information. What specific activities are you interested in?"
    
    # Save bot response
    db.add_chat_message(session_id, 'bot', response)
    
    return jsonify({'response': response})

@app.route('/upload_pdf', methods=['POST'])
@login_required
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'response': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'response': 'No selected file'}), 400
    
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # In a real app, process the PDF here
        response = f"I've received your PDF: '{filename}'. I'll analyze it and extract the itinerary information. Is there anything specific you'd like to modify or add to this existing plan?"
        
        # Save the message in chat
        user_id = session['user_id']
        chat_sessions = db.get_user_chat_sessions(user_id)
        
        if chat_sessions:
            session_id = chat_sessions[0]['id']
        else:
            session_id = db.create_chat_session(user_id)
        
        db.add_chat_message(session_id, 'bot', response)
        
        return jsonify({'response': response})
    
    return jsonify({'response': 'Invalid file type. Please upload a PDF.'}), 400

@app.route('/finalize_trip', methods=['POST'])
@login_required
def finalize_trip():
    user_id = session['user_id']
    
    # In a real app, generate the itinerary from chat history
    # For now, create a sample trip and itinerary
    
    # Create a trip
    trip_id = db.create_trip(
        user_id=user_id,
        title="New York Adventure",
        destination="New York",
        start_date=(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        end_date=(datetime.now() + timedelta(days=35)).strftime('%Y-%m-%d')
    )
    
    # Add sample places if they don't exist
    places = [
        {
            'name': 'Central Park',
            'description': 'Iconic urban park with various attractions',
            'lat': 40.7829,
            'lng': -73.9654,
            'image': '/static/images/central_park.jpg',
            'rating': 4.8
        },
        {
            'name': 'Metropolitan Museum of Art',
            'description': 'One of the world\'s largest art museums',
            'lat': 40.7794,
            'lng': -73.9632,
            'image': '/static/images/met.jpg',
            'rating': 4.9
        },
        {
            'name': 'Times Square',
            'description': 'Iconic intersection known for bright lights',
            'lat': 40.7580,
            'lng': -73.9855,
            'image': '/static/images/times_square.jpg',
            'rating': 4.6
        }
    ]
    
    place_ids = []
    for place_data in places:
        place_id = db.create_place(
            name=place_data['name'],
            latitude=place_data['lat'],
            longitude=place_data['lng'],
            description=place_data['description'],
            image_url=place_data.get('image'),
            rating=place_data.get('rating')
        )
        place_ids.append(place_id)
    
    # Add itinerary items
    db.add_itinerary_item(trip_id, place_ids[0], 1, '09:00', '11:00', 'Morning walk through the park')
    db.add_itinerary_item(trip_id, place_ids[1], 1, '12:00', '15:00', 'Explore the art collections')
    db.add_itinerary_item(trip_id, place_ids[2], 1, '16:00', '18:00', 'Experience the vibrant atmosphere')
    
    # Store the trip ID in session for the itinerary view
    session['current_trip_id'] = trip_id
    
    return jsonify({'finalized': True, 'trip_id': trip_id})

@app.route('/view_itinerary')
@login_required
def view_itinerary():
    user = get_current_user()
    
    # Get the trip ID from session or query parameter
    trip_id = session.get('current_trip_id') or request.args.get('trip_id')
    
    if not trip_id:
        flash('No itinerary selected', 'warning')
        return redirect(url_for('profile'))
    
    # Generate markdown itinerary
    itinerary_md = db.generate_markdown_itinerary(trip_id)
    
    if not itinerary_md:
        flash('Itinerary not found', 'error')
        return redirect(url_for('profile'))
    
    return render_template('itinerary.html', user=user, itinerary=itinerary_md)

@app.route('/api/places/nearby', methods=['GET'])
def api_places_nearby():
    lat = float(request.args.get('lat', 40.7128))
    lng = float(request.args.get('lng', -74.0060))
    radius = float(request.args.get('radius', 5))
    
    places = db.get_place_suggestions(lat, lng, radius)
    
    return jsonify({
        'places': [dict(place) for place in places]
    })

@app.route('/api/itinerary/<int:trip_id>', methods=['GET'])
def api_get_itinerary(trip_id):
    itinerary = db.get_trip_itinerary(trip_id)
    
    if not itinerary:
        return jsonify({'error': 'Itinerary not found'}), 404
    
    return jsonify({
        'itinerary': itinerary
    })

@app.route('/api/itinerary/<int:trip_id>/add', methods=['POST'])
@login_required
def api_add_itinerary_item(trip_id):
    data = request.json
    
    place_id = data.get('place_id')
    day = data.get('day', 1)
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    notes = data.get('notes')
    
    if not all([place_id, start_time, end_time]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    item_id = db.add_itinerary_item(trip_id, place_id, day, start_time, end_time, notes)
    
    if not item_id:
        return jsonify({'error': 'Failed to add itinerary item'}), 500
    
    return jsonify({
        'success': True,
        'item_id': item_id
    })

if __name__ == '__main__':
    app.run(debug=True)

