#!/usr/bin/python3
"""Renders maps info"""

import uuid
import folium
import requests
from backend.dev_flask.views import app_views

from backend.dev_flask.views.terminal import get_terminal
from backend.models import storage
from backend.models import Vehicle

from flask import app, jsonify, request
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest

from .commons import (fetch_data, fetch_data_id, fetch_process,
                      reach_endpoint, allows)

@app_views.route('/map_with_location', strict_slashes=False, methods=allows)
def map_with_location():
    """
    Generate map with user's location marked
    """
    # # Get lat and lon from query parameters
    # lat = request.args.get('lat', type=float, default=5.6037)
    # lon = request.args.get('lon', type=float, default=-0.1870)
    lat = 5.6037
    lon = -0.1870

    # Create map (center on user's location if valid, else Accra)
    if lat and lon and -90 <= lat <= 90 and -180 <= lon <= 180:
        map_center = [lat, lon]
    else:
        map_center = [lat, lon]
        print("Invalid coordinates, using default Accra location")

    folium_map = folium.Map(location=map_center, zoom_start=16)

    # Create map with explicit ID
    map_id = f"map_{uuid.uuid4().hex}"
    folium_map = folium.Map(location=map_center, zoom_start=16, tiles="OpenStreetMap", attr="Map", id=map_id)

    # Add user marker and beaming circle if location is valid
    if lat is not None and lon is not None and -90 <= lat <= 90 and -180 <= lon <= 180:
        # Add user marker
        folium.Marker(
            location=[lat, lon],
            popup="Your Location",
            icon=folium.Icon(color="red", icon="user")
        ).add_to(folium_map)

        # Add beaming circle (blue stroke, red fill with random color changes)
        circle_id = f"circle_{uuid.uuid4().hex}" 
        folium.Circle(
            location=[lat, lon],
            radius=70,  # Base radius
            color="#0000FF",  # Blue stroke
            weight=3,  # Thicker stroke for visibility
            fill=True,
            fill_color="#AA0000",  # Initial red fill
            fill_opacity=0.4,  # Fill opacity
            opacity=1.0,  # Full stroke opacity
            id=circle_id  # Unique ID for JavaScript targeting
        ).add_to(folium_map)

        # Add custom JS for beaming effect and random color changes

    # Fetch bus terminals from /api/terminals endpoint
    try:
        terminals = requests.get('http://127.0.0.1:5000/api/terminals', timeout=5).json()
        for terminal in terminals:
            term_lat = terminal.get('latitude')
            term_lon = terminal.get('longitude')
            term_name = terminal.get('name', f"Terminal at {term_lat}, {term_lon}")
            if term_lat and term_lon and -90 <= term_lat <= 90 and -180 <= term_lon <= 180:
                folium.Marker(
                    location=[term_lat, term_lon],
                    popup=term_name,
                    icon=folium.Icon(color="blue", icon="bus", prefix="fa")
                ).add_to(folium_map)
            else:
                print(f"Invalid terminal coordinates: {term_name}, lat={term_lat}, lon={term_lon}")
    except Exception as e:
        print(f"Error fetching terminals: {str(e)}")

    return folium_map.get_root().render()