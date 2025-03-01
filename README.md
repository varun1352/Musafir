

# Musafir

Musafir is a hackathon project built for the "The Future of Travel Technology" track. This project redefines travel by offering a dynamic itinerary builder, personalized recommendations, and a community-driven travel experience. Whether users input their desired itinerary or build one interactively through a swiping interface, Musafir leverages an LLM to generate tailored travel plans and helps connect like-minded travelers.

## Features

- **Dynamic Itinerary Creation:**  
  Users can input a detailed itinerary or select a recommended travel plan which is then processed by an LLM to output a structured JSON itinerary.

- **Interactive Travel Graph:**  
  Visualize travel plans as a 3D graph (powered by 3js) where each node represents a travel destination along with time slots. Click on any node to see other users attending that location.

- **Tinder-Style Location Swiping:**  
  Find your next destination with a swipe interface that offers personalized recommendations based on your preferences and available time slots.

- **Community Connection:**  
  Discover and connect with fellow travelers via in-app messaging, facilitating meet-ups and shared experiences.

## Tech Stack

- **Backend:**  
  - Flask (Python) for API and backend logic  
  - SQLite for the database  
  - Cerebras API for LLM integration

- **Frontend:**  
  - React for building the user interface  
  - 3js for interactive graph visualization

## Project Structure

```
Musafir/
├── backend/
│   ├── app.py              # Flask application entry point
│   ├── config.py           # Application configuration (DB, API keys, etc.)
│   ├── models.py           # Database models (SQLAlchemy)
│   ├── routes/
│   │   ├── __init__.py     # Initialize and register Flask blueprints
│   │   ├── auth.py         # Authentication endpoints (signup, login)
│   │   ├── itinerary.py    # Itinerary management and LLM integration endpoints
│   │   └── messaging.py    # Messaging endpoints for user interactions
│   ├── utils/
│   │   └── helpers.py      # Helper functions (e.g., graph operations)
│   └── templates/          # (Optional) Jinja templates if needed
├── frontend/
│   ├── public/             # Public assets (HTML, favicon, etc.)
│   └── src/
│       ├── components/
│       │   ├── Signup.js           # User signup component
│       │   ├── ItineraryInput.js   # Itinerary input component
│       │   ├── GraphView.js        # 3js-based graph visualization component
│       │   └── LocationSwiper.js   # Tinder-style location selector
│       ├── App.js              # Main React component
│       ├── index.js            # React entry point
│       └── styles/             # CSS or styled-components files
├── database/
│   └── schema.sql          # SQL script for creating the database schema
├── requirements.txt        # Python dependencies (Flask, SQLAlchemy, etc.)
└── README.md               # This file
```

## Setup & Installation

### Prerequisites

- **Backend:**  
  - Python 3.7+
  - Virtualenv (recommended)

- **Frontend:**  
  - Node.js and npm

### Backend Setup

1. **Create a virtual environment and install dependencies:**

   ```bash
   cd Musafir/backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r ../requirements.txt
   ```

2. **Initialize the database:**

   You can run the SQL commands in `database/schema.sql` using your preferred SQLite tool, or automate this with Flask migrations if desired.

3. **Run the Flask application:**

   ```bash
   export FLASK_APP=app.py
   export FLASK_ENV=development  # Optional: for auto-reload during development
   flask run
   ```

### Frontend Setup

1. **Install dependencies and start the React app:**

   ```bash
   cd Musafir/frontend
   npm install
   npm start
   ```

2. **Development:**  
   The React app will open in your default browser, where you can interact with the components.

## Future Enhancements

- **Real-time Data & Geolocation:** Integrate real-time location data and map APIs for a more dynamic user experience.
- **Advanced LLM Integration:** Expand beyond basic itinerary planning by integrating additional features from the Cerebras API.
- **User Profiles & Itinerary Sharing:** Enhance social interactions by allowing users to share and rate itineraries.

## License

This project is for educational and hackathon purposes.

## Acknowledgments

Special thanks to the organizers of the hackathon and to all contributors who helped shape the vision behind Musafir.
