import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv
import json

load_dotenv()

# Cerebras API configuration
CEREBRAS_API_URL = "https://api.cerebras.net/v1/generate"
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")

app = Flask(__name__)

# Set up upload folder for PDFs
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Initialize Cerebras API client
client = Cerebras(api_key=CEREBRAS_API_KEY)

# Global variables for storing itineraries
user_itinerary = []   # Stores user inputs for refining the itinerary
final_markdown = ""   # Stores the finalized itinerary in markdown format
final_json = {}       # Stores the finalized itinerary as JSON

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
    For example:
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

# -----------------------------
# Core Routes & Travel Planner
# -----------------------------

@app.route("/")
def index():
    return render_template("travelPlanner.html")

@app.route("/process_text", methods=["POST"])
def process_text():
    """Handles user messages to refine the itinerary."""
    user_text = request.json.get("message", "")
    if not user_text:
        return jsonify({"error": "No message provided"}), 400

    user_itinerary.append(user_text)

    messages = [
        {
            "role": "system",
            "content": "You are a travel assistant helping users plan a structured travel itinerary."
        },
        {
            "role": "user",
            "content": f"Refine this trip itinerary based on the following user input:\n\n{user_text}\n\nEnsure clarity and keep a structured format."
        }
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
        {
            "role": "system",
            "content": "You are a travel assistant that processes uploaded PDF itineraries."
        },
        {
            "role": "user",
            "content": f"Extract and summarize the travel itinerary from this uploaded PDF file: {file.filename}. Structure it properly and retain all relevant details."
        }
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
         The JSON itinerary includes a new attribute "expected_time" for each activity.
    Returns both in a JSON response to the client.
    """
    global final_markdown, final_json

    combined_itinerary = "\n".join(user_itinerary)

    # 1. Generate Markdown itinerary
    messages_markdown = [
        {
            "role": "system",
            "content": "You are an expert travel planner. Your task is to generate a structured, well-formatted markdown travel itinerary."
        },
        {
            "role": "user",
            "content": f"Generate a final, markdown-formatted itinerary based on this travel plan:\n\n{combined_itinerary}\n\nUse clear headers, bullet points, and markdown elements for easy readability. The final itinerary should look like a well-structured travel guide."
        }
    ]
    final_markdown = call_cerebras_api(messages_markdown)

    # 2. Generate JSON itinerary
    json_prompt = (
        "Generate a valid JSON itinerary for the following trip plan. Output only valid JSON (do not include any markdown formatting, headers, or code fences). "
        "The JSON must exactly follow this structure:\n\n"
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

    # Cleanup code fences if present
    if json_response.startswith("```") and json_response.endswith("```"):
        json_response = json_response.strip("`").strip()

    try:
        final_json = json.loads(json_response)
    except Exception as e:
        final_json = {
            "error": "Failed to parse JSON itinerary",
            "raw_response": json_response
        }

    # Store JSON in DB (placeholder)
    store_json_itinerary(final_json)

    return jsonify({
        "finalized": True,
        "markdown": final_markdown,
        "json_itinerary": final_json
    })

# -----------------------------------
# (Optional) Remove or Keep if not needed
# -----------------------------------
@app.route("/view_itinerary")
def view_itinerary():
    """Displays the finalized itinerary in markdown format."""
    return render_template("itinerary.html", itinerary=final_markdown)

# -----------------------------------
# New Authentication and Signup Routes
# -----------------------------------
@app.route("/google-auth")
def google_auth():
    return render_template("google_auth.html")

@app.route("/google-auth/redirect")
def google_auth_redirect():
    return redirect(url_for('signup'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Save user info to DB if needed
        return redirect(url_for("index"))
    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=True)
