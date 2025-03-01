from flask import Flask, render_template, request, jsonify
from models.database import init_db  # Function to initialize your SQLite database

app = Flask(__name__)
app.config.from_pyfile('config.py')

# Initialize the database (ensure init_db sets up tables as needed)
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/itinerary', methods=['GET', 'POST'])
def itinerary():
    if request.method == 'POST':
        # For now, simply echo back the itinerary data
        itinerary_text = request.form.get('itinerary')
        # This is where you would call your LLM API and process the trip plan
        json_itinerary = {"status": "success", "itinerary": itinerary_text}
        return jsonify(json_itinerary)
    return render_template('itinerary.html')

@app.route('/map')
def map_view():
    return render_template('map_view.html')

@app.route('/dynamic')
def dynamic_plan():
    return render_template('dynamic_plan.html')

if __name__ == '__main__':
    app.run(debug=True)
