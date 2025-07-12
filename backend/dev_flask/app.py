#!/usr/bin/python3
"""
starting a Flask app
"""
import os
from dotenv import load_dotenv
from flask_cors import CORS
from flask import Flask
from werkzeug.exceptions import HTTPException
from flasgger import Swagger
from flasgger.utils import swag_from
from backend.dev_flask.views import app_views

load_dotenv()

host = os.getenv("UMPIRE_HOST", "localhost")
port = int(os.getenv("UMPIRE_FLASK_PORT", 5000))
if not host or not port:
    raise ValueError("UMPIRE_HOST and UMPIRE_FLASK_PORT must be set in .env file")


# Initialize Flask application
app = Flask(__name__)

# set global strict slashes
app.url_map.strict_slashes = False

# BluePrint of app_views defined in api/v1/views
app.register_blueprint(app_views)

# Ensuring cross-origin resource sharing among components
CORS(app, resources={'/*': {'origins': host}})

app.config['SWAGGER'] = {
    'title': 'Umpire Restful API',
    'uiversion': 3
}

Swagger(app)

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    """
    Handle HTTP exceptions and return a JSON response.
    This function is called when an HTTP exception occurs.
    """
    response = e.get_response()
    response.data = {
        "error": e.name,
        "message": e.description
    }
    response.content_type = "application/json"
    return response


@app.route('/', strict_slashes=False)
def index():
    """
    Returns a simple greeting message.
    This function is mapped to the root URL ('/') of the Flask application.
    """
    return "Welcome to the Umpire API! Use /backend/flask for API access."


if __name__ == '__main__':
    app.run(host=host, port=port)