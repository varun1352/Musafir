from flask import Flask, render_template, request, jsonify, redirect, url_for
from models.database import init_db  # Function to initialize your SQLite database

app = Flask(__name__)
app.config.from_pyfile('config.py')

# Initialize the database
init_db()

@app.route('/')
def index():
    return render_template('index.html')

# Google Auth page
@app.route('/google-auth')
def google_auth():
    return render_template('google_auth.html')

# Placeholder for Google OAuth redirect
@app.route('/google-auth/redirect')
def google_auth_redirect():
    # In a real implementation, you would redirect to the Google OAuth endpoint here.
    # After a successful OAuth process, you would then redirect the user to the signup page.
    return redirect(url_for('signup'))

# Signup page with user preferences
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Process signup form data
        username = request.form.get('username')
        email = request.form.get('email')
        preference = request.form.get('preference')
        # Here you would add code to save the user details to your database
        # For now, simply redirect to the index page
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/itinerary', methods=['GET', 'POST'])
def itinerary():
    if request.method == 'POST':
        itinerary_text = request.form.get('itinerary')
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
