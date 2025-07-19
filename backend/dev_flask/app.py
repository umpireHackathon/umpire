#!/usr/bin/python3
"""
Starting the Flask app for Umpire
"""

import os
import folium
from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_cors import CORS
import requests
from werkzeug.exceptions import HTTPException
from flasgger import Swagger
from flasgger.utils import swag_from
from backend.dev_flask.views import app_views  # Blueprint registration

# Read environment variables (optional: use dotenv if needed)
HOST = os.getenv("UMPIRE_HOST", "localhost")
PORT = int(os.getenv("UMPIRE_FLASK_PORT", 5000))

if not HOST or not PORT:
    raise ValueError("UMPIRE_HOST and UMPIRE_FLASK_PORT must be set in the environment or .env file")

# Initialize Flask app
app = Flask(__name__)
app.url_map.strict_slashes = False  # Globally disable strict slashes

# Register Blueprints
app.register_blueprint(app_views)

# Setup CORS - allow localhost during dev, use '*' if needed for open testing
CORS(app, resources={r"/*": {"origins": "*"}})

# Swagger UI config
app.config['SWAGGER'] = {
    'title': 'Umpire Restful API',
    'uiversion': 3
}
Swagger(app)

# Optional: Hook before each request (currently unused)
@app.before_request
def before_request():
    pass

# Fixed: Proper HTTP error handling
@app.errorhandler(HTTPException)
def handle_http_exception(e):
    """
    Handles HTTP exceptions and returns JSON response
    """
    response = jsonify({
        "error": e.name,
        "message": e.description
    })
    response.status_code = e.code
    return response

@app.route('/', strict_slashes=False)
def index():
    """
    Basic welcome endpoint
    """
    # Create default map centered on Accra
    accra_map = folium.Map(location=[5.6037, -0.1870], zoom_start=12)

    # Resolve static/ path
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    os.makedirs(static_dir, exist_ok=True)

    # Save default map
    accra_map_path = os.path.join(static_dir, 'accra_map.html')
    accra_map.save(accra_map_path)
    
    # Fetch terminals for the map
    try:
        terms = requests.get('http://127.0.0.1:5000/api/terminals', timeout=5).json()
    except Exception as e:
        print(f"Error fetching terminals: {str(e)}")
        terms = []

    # Render template with icon and default map
    return render_template("index.html", icon='assets/logo.svg', accra_map='accra_map.html', terminals=terms)



# Entry point
if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=True)
