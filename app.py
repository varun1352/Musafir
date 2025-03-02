import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv
import json
import re
load_dotenv()

# Cerebras API configuration
CEREBRAS_API_URL = "https://api.cerebras.net/v1/generate"  # Replace with the actual API endpoint if needed
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")  # Ensure your .env file has this variable

# Initialize Flask app
app = Flask(__name__)

# Set up upload folder for PDFs
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Initialize Cerebras API client
client = Cerebras(api_key=CEREBRAS_API_KEY)

# Global variables for storing itineraries
user_itinerary = []  # Stores user inputs for refining the itinerary
final_markdown = ""  # Stores the finalized itinerary in markdown format
final_json = {}      # Stores the finalized itinerary as JSON

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

def store_json_itinerary(json_data):
    """
    Placeholder function to store the JSON itinerary in the database.
    Here, you would connect to your database and insert the JSON data.
    For example, using SQLite:
    
    import sqlite3
    conn = sqlite3.connect('musafir.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO itineraries (user_id, itinerary_data) VALUES (?, ?)", (user_id, json.dumps(json_data)))
    conn.commit()
    conn.close()
    """
    print("Storing JSON itinerary to the database:")
    print(json.dumps(json_data, indent=2))
    # TODO: Add actual DB insertion code here.

# ----------------كنولوجيا المعلومات-------------
# Core Routes & Travel Planner
# -----------------------------

@app.route("/")
def index():
    # Main landing page (using travelPlanner.html as before)
    return render_template("travelPlanner.html")

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
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    messages = [
        {"role": "system", "content": "You are a travel assistant that processes uploaded PDF itineraries. Format your responses using Markdown for better readability."},
        {"role": "user", "content": f"Extract and summarize the travel itinerary from this uploaded PDF file: {file.filename}. Structure it properly with Markdown formatting and retain all relevant details."}
    ]

    extracted_itinerary = call_cerebras_api(messages)
    user_itinerary.append(extracted_itinerary)

    return jsonify({"response": extracted_itinerary})

@app.route("/finalize_trip", methods=["POST"])
def finalize_trip():
    """
    Generates two outputs when finalizing the trip:
      1. A Markdown-formatted itinerary for display.
      2. A JSON itinerary for backend processing and database storage.
    """
    global final_markdown, final_json

    # Combine all user itinerary inputs into one text block.
    combined_itinerary = "\n".join(user_itinerary)

    # 1. Generate Markdown itinerary
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

    # Use regex to extract the JSON object from the response.
    # This regex captures everything from the first '{' to the last '}'.
    json_match = re.search(r'(\{[\s\S]*\})', json_response)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_str = json_response.strip()

    try:
        final_json = json.loads(json_str)
    except Exception as e:
        print("Error parsing JSON itinerary:", e)
        final_json = {"error": "Failed to parse JSON itinerary", "raw_response": json_response}

    print("Final JSON itinerary:", json.dumps(final_json, indent=2))
    store_json_itinerary(final_json)

    return jsonify({"finalized": True})

@app.route("/view_itinerary")
def view_itinerary():
    """Displays the finalized itinerary in markdown format."""
    return render_template("itinerary.html", itinerary=final_markdown)

# -----------------------------------
# New Authentication and Signup Routes
# -----------------------------------

@app.route("/google-auth")
def google_auth():
    """Displays the Google authentication page."""
    return render_template("google_auth.html")

@app.route("/google-auth/redirect")
def google_auth_redirect():
    """
    Placeholder for Google OAuth redirect.
    In a production system, you'd handle OAuth flow here.
    For now, simulate redirection to the signup page.
    """
    return redirect(url_for('signup'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Signup page that collects basic user info along with travel preferences via descriptive radio buttons.
    """
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        preference = request.form.get("preference")
        # Here you would typically save the user details to a database.
        # For now, we'll just redirect the user to the home page after signup.
        return redirect(url_for("index"))
    return render_template("signup.html")

@app.route('/map')
def map_view():
    return render_template('map_view.html')

@app.route('/day-planner')
def day_planner():
    return render_template('dynamic_plan.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Add these new routes to your existing app.py

@app.route('/profile')
def profile():
    # In a real app, you'd get this from your database
    user_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "joined": "January 2025",
        "trips": [
            {
                "id": 1,
                "destination": "New York City",
                "dates": "Jul 1-3, 2023",
                "status": "completed"
            },
            {
                "id": 2,
                "destination": "San Francisco",
                "dates": "Aug 15-20, 2023",
                "status": "upcoming"
            }
        ],
        "preferences": ["Adventure", "Cultural"]
    }
    return render_template('profile.html', user=user_data)

@app.route('/explore')
def explore():
    # Static featured itineraries
    featured_trips = [
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
        # Add more featured trips
    ]
    
    categories = [
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
    
    return render_template('explore.html', featured=featured_trips, categories=categories)

# -----------------------------
# Main entry point
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)