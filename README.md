# Musafir - The Future of Travel Technology

Musafir is an innovative web application designed for the hackathon track **"The Future of Travel Technology."** Our goal is to redefine travel by combining AI-driven itinerary planning with interactive, community-based travel experiences. Whether you’re a Gen-Z explorer or a seasoned traveler, Musafir helps you plan, refine, and share personalized travel itineraries in real time.

---

## Table of Contents

- [Features](#features)
- [Architecture & Tech Stack](#architecture--tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Database Design](#database-design)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **AI-Powered Itinerary Planning:**  
  Use our chat-based interface powered by a language model (e.g., Llama 3.1-8b via Cerebras API) to generate, refine, and finalize your travel plans with natural, Markdown-formatted responses.

- **Dynamic Itinerary Extraction:**  
  Finalized itineraries are extracted both in a human-friendly Markdown format and as structured JSON for backend processing and storage.

- **Interactive Map View:**  
  Visualize your itinerary on an interactive map built with Leaflet.js. See all planned places, routes between them, and even find fellow travelers attending the same events.

- **Tinder-Style Day Planning:**  
  A dynamic “plan your day” interface that lets you swipe through available destinations, select preferred time slots, and build a day-to-day travel plan.

- **Google OAuth Authentication:**  
  Secure signup and login with Google, ensuring a smooth onboarding process.

- **Real-Time Community Features:**  
  Discover and connect with nearby travelers attending the same events or locations, with options to send connection requests via email.

---

## Architecture & Tech Stack

- **Frontend:**  
  - HTML, CSS, JavaScript (with [Leaflet.js](https://leafletjs.com/) for maps)
  - Jinja templating for dynamic pages
- **Backend:**  
  - Python & Flask for the web server and REST API endpoints
  - Cerebras API for AI-powered itinerary generation
- **Database:**  
  - SQLite (via custom Database class in Python)
  - Tables for users, places, itineraries, chat sessions, and more
- **Authentication:**  
  - Google OAuth integration using Flask-OAuthlib

---

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/musafir.git
   cd musafir
   ```

2. **Create and Activate a Virtual Environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**

   Create a `.env` file in the root directory and set the following variables:

   ```env
   SECRET_KEY=your_secret_key
   CEREBRAS_API_KEY=your_cerebras_api_key
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   ```

5. **Initialize the Database:**

   The database is automatically initialized with required tables and dummy data when you run the application.

---

## Usage

1. **Run the Application:**

   ```bash
   python app.py
   ```

2. **Access the App:**

   Open your browser and go to [http://127.0.0.1:5000](http://127.0.0.1:5000).

3. **Plan Your Trip:**

   - **Signup/Login:** Use Google OAuth or create an account.
   - **Chat Interface:** Interact with the AI travel assistant to input your travel preferences and itinerary details.
   - **Finalize Itinerary:** Finalize your plan to generate both Markdown and JSON outputs.
   - **Map & Day Planner:** View your itinerary on an interactive map, explore nearby travelers, and refine your day plan.

---

## Project Structure

```plaintext
.
├── README.md                # This file
├── api
│   └── llm_api.py           # API integration with the LLM
├── app.py                   # Main Flask application
├── config.py                # Configuration file for environment variables
├── database.py              # Database initialization and query functions
├── models                   # Data models for users, places, distances, etc.
│   ├── __init__.py
│   ├── database.py
│   ├── distance_model.py
│   ├── place_model.py
│   └── user_model.py
├── requirements.txt         # Python dependencies
├── static                   # Static files: CSS, images, JavaScript
│   ├── css
│   │   └── main.css
│   ├── images
│   └── js
│       ├── dynamic_plan.js  # JavaScript for day planning and map interaction
│       └── map.js           # JavaScript for map view
├── templates                # HTML templates using Jinja2
│   ├── base.html
│   ├── dynamic_plan.html
│   ├── google_auth.html
│   ├── index.html
│   ├── itinerary.html
│   ├── map_view.html
│   ├── profile.html
│   ├── signup.html
│   └── travelPlanner.html
├── uploads                  # Folder for uploaded files (e.g., PDFs)
└── utils                    # Utility scripts
    ├── graph_utils.py
    └── itinerary_parser.py
```

---

## Database Design

The database schema includes tables for:

- **Users:** Storing account details and preferences.
- **Places:** Destinations with geolocation, description, and images.
- **Itineraries:** Finalized itineraries in Markdown and JSON formats.
- **Chat Sessions & Messages:** To store conversation history with the AI assistant.
- **Contact Requests:** For managing email-based connection requests.
- **Day Plans:** For dynamic “tinderizing” day planning.

Refer to the [Database Schema](#database-design-details) section for more details.

### Database Schema Details

- **Users Table:**  
  Stores user details, including email, password hash, and preferences.

- **Places Table:**  
  Contains information about travel destinations with latitude, longitude, images, and ratings.

- **Itineraries Table:**  
  Stores finalized itineraries with both Markdown and JSON representations.

- **Chat Sessions & Messages:**  
  Captures user conversations with the AI travel assistant.

- **Contact Requests Table:**  
  Manages email-based connection requests between users.

- **Day Plans Table:**  
  Supports the interactive “plan your day” feature.

---

## Contributing

Contributions are welcome! If you'd like to contribute:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push the branch: `git push origin feature/my-feature`
5. Open a pull request.

Please follow the [Code of Conduct](CODE_OF_CONDUCT.md) and ensure your code adheres to the project style guidelines.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgements

- **Cerebras** for their API that powers our AI itinerary generation.
- **Leaflet.js** for providing an awesome mapping library.
- **Flask** for being a lightweight and flexible web framework.
- **Faker & names** for helping generate realistic dummy data.
- And of course, all our users and contributors who make Musafir possible!

