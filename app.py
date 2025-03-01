CEREBRAS_API_URL = "https://api.cerebras.net/v1/generate"  # Replace with the actual API endpoint
CEREBRAS_API_KEY = ""  # Replace with your API key

import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from cerebras.cloud.sdk import Cerebras

# Initialize Flask app
app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Initialize Cerebras API client
client = Cerebras(api_key=CEREBRAS_API_KEY)

user_itinerary = []  # Stores user inputs for refining the itinerary
final_itinerary = ""  # Stores the finalized itinerary

def call_cerebras_api(messages):
    """Calls the Cerebras API with the given messages array."""
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3.1-8b"
        )
        return chat_completion.choices[0].message.content  # ✅ Corrected
    except Exception as e:
        return f"Error: {str(e)}"

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
        {"role": "system", "content": "You are a travel assistant helping users plan a structured travel itinerary."},
        {"role": "user", "content": f"Refine this trip itinerary based on the following user input:\n\n{user_text}\n\nEnsure clarity and keep a structured format."}
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
        {"role": "system", "content": "You are a travel assistant that processes uploaded PDF itineraries."},
        {"role": "user", "content": f"Extract and summarize the travel itinerary from this uploaded PDF file: {file.filename}. Structure it properly and retain all relevant details."}
    ]

    extracted_itinerary = call_cerebras_api(messages)
    user_itinerary.append(extracted_itinerary)

    return jsonify({"response": extracted_itinerary})

@app.route("/finalize_trip", methods=["POST"])
def finalize_trip():
    """Generates a final markdown-formatted itinerary."""
    global final_itinerary

    combined_itinerary = "\n".join(user_itinerary)

    messages = [
        {"role": "system", "content": "You are an expert travel planner. Your task is to generate a structured, well-formatted markdown travel itinerary."},
        {"role": "user", "content": f"Generate a final, markdown-formatted itinerary based on this travel plan:\n\n{combined_itinerary}\n\n"
                                     "Use clear headers, bullet points, and markdown elements for easy readability. The final itinerary should look like a well-structured travel guide."}
    ]

    final_itinerary = call_cerebras_api(messages)
    print(final_itinerary)

    return jsonify({"finalized": True})

@app.route("/view_itinerary")
def view_itinerary():
    """Displays the finalized itinerary in markdown format."""
    return render_template("itinerary.html", itinerary=final_itinerary)

if __name__ == "__main__":
    app.run(debug=True)
