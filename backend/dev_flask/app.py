#!/usr/bin/python3
"""
Starting the Flask app for Umpire
<a target="_blank" href="https://icons8.com/icon/M8to8q11r1v5/bus-stop">Bus Stop</a> icon by <a target="_blank" href="https://icons8.com">Icons8</a>
"""

import os
import random
import folium
from folium.features import CustomIcon
from folium.features import DivIcon
from folium.elements import Element
from flask import Flask, json, jsonify, request, render_template, redirect, url_for, current_app
from flask_cors import CORS
import requests
from werkzeug.exceptions import HTTPException
from flasgger import Swagger
from flasgger.utils import swag_from
from api.v1.views import app_views
from api.v1.views.commons import fetch_data_url  # Blueprint registration

# Read environment variables (optional: use dotenv if needed)
HOST = os.getenv("UMPIRE_HOST", "localhost")
PORT = int(os.getenv("UMPIRE_FLASK_PORT", 5000))
BASE_URL = os.getenv("BASE_URL", "/api")
BSTOPS_URL = BASE_URL + "/bstops"
TERMINALS_URL = BASE_URL + "/terminals"
VEHICLES_URL = BASE_URL + "/vehicles"
ROUTES_URL = BASE_URL + "/routes"

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


@app.route('/update_map', methods=['POST'])
def update_map():
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

    # Create a custom icon for terminals
    terminal_icon = CustomIcon(
        icon_image=os.path.join(static_dir, 'assets/terminal.png'),
        icon_size=(20, 20),
        icon_anchor=(10, 10),  # Center the icon
        popup_anchor=(0, -10),  # Adjust popup position        
    )
    bus_stop_icon = CustomIcon(
        icon_image=os.path.join(static_dir, 'assets/bus_stop.png'),
        icon_size=(20, 20),
        icon_anchor=(10, 10),  # Center the icon
        popup_anchor=(0, -10),  # Adjust popup position
    )

    css_link = url_for('static', filename='../static/css/map.css')
    js_link = url_for('static', filename='../static/js/map.js')
    style = f'<link rel="stylesheet" href="{css_link}" />'
    script = f'<script src="{js_link}"></script>'

    data = request.json
    user_lat = data.get('lat')
    user_lng = data.get('lng')
    user_action = data.get('action', 'show_location')
    
    # set default for now:
    user_lat = 5.6037  # Default latitude for Accra
    user_lng = -0.1870  # Default longitude for Accra

    m = folium.Map(location=[user_lat, user_lng], zoom_start=15)
    m.get_root().header.add_child(Element(style))
    
    # SOLUTION 1: Pass data via JavaScript variables
    # Create a script that defines global variables with the coordinates
    data_script = f"""
    <script>
        // Global variables accessible to your custom JavaScript
        window.mapData = {{
            userLat: {user_lat},
            userLng: {user_lng},
            userAction: '{user_action}',
            terminals: [],
            stops: []
        }};
        
        // Function to get map data
        window.getMapData = function() {{
            return window.mapData;
        }};
    </script>
    """
    
    m.get_root().header.add_child(Element(data_script))
    m.get_root().header.add_child(Element(script))

    # Collect terminal and stop data for JavaScript access
    terminals_data = []
    stops_data = []

    if user_action and user_action == 'my_location':
        # Center map on user's location
        m.location = [user_lat, user_lng]
        m.zoom_start = 15
        # Add regular marker first
        folium.Marker([user_lat, user_lng]).add_to(m)
    
        # Add circle for pulsating effect
        folium.Circle(
            location=[user_lat, user_lng],
            radius=20,
            color='#3186cc',
            fill=True,
            fill_color='#3186cc',
            fill_opacity=0.7,
            className='pulsating-circle'
        ).add_to(m)
        
    if user_action and user_action == 'show_routes':
        pass

    if user_action and user_action == 'show_terminals':
        # Fetch terminals from the API
        terminals = fetch_data_url(TERMINALS_URL)
        if isinstance(terminals, list) and len(terminals) > 0:
            for terminal in terminals:
                # Store terminal data for JavaScript access
                if 'latitude' in terminal and 'longitude' in terminal:
                    terminals_data.append({
                    'id': terminal['id'],
                    'name': terminal['name'],
                    'latitude': terminal['latitude'],
                    'longitude': terminal['longitude']
                })
                
                html_icon = f"""
                            <div class="my-terminal-icon" id="icon_{terminal['id']}" 
                                 data-lat="{terminal['latitude']}" 
                                 data-lng="{terminal['longitude']}"
                                 data-name="{terminal['name']}">
                                <img src='../static/assets/terminal.png' style='width:25px;height:25px;'/>
                            </div>
                            """
                folium.Marker(
                    location=[terminal['latitude'], terminal['longitude']],
                    popup=terminal['name'],
                    icon=DivIcon(
                        html=html_icon,
                        icon_size=(30, 30),
                        icon_anchor=(15, 15)  # center the icon
                    )
                ).add_to(m)
        else:
            folium.Marker(
                location=[user_lat, user_lng],
                popup="No terminals found",
                icon=folium.Icon(color='red')
            ).add_to(m)

    if user_action and user_action == 'show_stops':
        # Fetch stops from the API
        stops = fetch_data_url(BSTOPS_URL)
        for stop in stops:
            # Store stop data for JavaScript access
            stops_data.append({
                'name': stop['name'],
                'latitude': stop['latitude'],
                'longitude': stop['longitude']
            })
            
            folium.Marker(
                location=[stop['latitude'], stop['longitude']],
                popup=stop['name'],
                icon=folium.Icon(color='red')
            ).add_to(m)

    # Update the global data with collected information
    update_data_script = f"""
    <script>
        // Update the global data with terminals and stops
        if (window.mapData) {{
            window.mapData.terminals = {json.dumps(terminals_data)};
            window.mapData.stops = {json.dumps(stops_data)};
        }}
    </script>
    """
    
    m.get_root().html.add_child(Element(update_data_script))

    return {
        'map_html': m._repr_html_(),
        'user_lat': user_lat,
        'user_lng': user_lng,
        'user_action': user_action,
        'terminals': terminals_data,
        'stops': stops_data
    }


@app.route('/', strict_slashes=False)
def home():
    """
    Basic welcome endpoint
    """
    # # Create default map centered on Accra
    # accra_map = folium.Map(location=[5.6037, -0.1870], zoom_start=12)

    # # Resolve static/ path
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    os.makedirs(static_dir, exist_ok=True)

    # # Save default map
    # accra_map_path = os.path.join(static_dir, 'accra_map.html')
    # accra_map.save(accra_map_path)
    
    # # Fetch terminals for the map


    # # Render template with icon and default map
    # return render_template("index.html", icon='assets/logo.svg', accra_map='accra_map.html', terminals=terms)
    accra_coords = (5.6037, -0.1870)
    m = folium.Map(location=accra_coords, zoom_start=12)
    map_html = m._repr_html_()

    return render_template('home.html', map_html=map_html)

@app.route('/travel')
def travel():
    # Create base map centered on Accra
    accra_coords = (5.6037, -0.1870)
    m = folium.Map(location=accra_coords, zoom_start=12)
    map_html = m._repr_html_()
    return render_template('travel.html', map_html=map_html)

@app.route('/random_position')
def random_position():
    """Generates a random position within a small range around Accra"""
    import random

    data = request.args
    if 'lat' in data and 'lng' in data:
        base_lat = float(data['lat'])
        base_lng = float(data['lng'])
    else:
        # Base coordinates for Accra
        base_lat = 5.6037
        base_lng = -0.1870
    return (
        base_lat + random.uniform(-0.001, 0.001),
        base_lng + random.uniform(-0.001, 0.001)
    )

@app.route('/optimize')
def optimize():
    from datetime import datetime
    try:
        vehicles = requests.get(f'http://127.0.0.1:{PORT}{VEHICLES_URL}', timeout=5).json()
        routes = requests.get(f'http://127.0.0.1:{PORT}{ROUTES_URL}', timeout=5).json()
    except Exception as e:
        print(f"Error fetching vehicles: {str(e)}")
        vehicles = []
        routes = []
    day = datetime.now().strftime("%A").lower()
    data = {"vehicles": vehicles, "routes": routes, "day": day}
    
    return render_template('optimize.html', optimizationData=data, BASE_URL=BASE_URL, route_optimized=False)

@app.route('/optimize/route')
def optimized_route():
    
    # Create base map centered on Accra with a sample optimized route
    accra_coords = (5.6037, -0.1870)
    m = folium.Map(location=accra_coords, zoom_start=12)
    
    # Add a sample route (in a real app, this would come from your optimization algorithm)
    route_coords = [
        (5.6037 + random.uniform(-0.1, 0.1), -0.1870 + random.uniform(-0.1, 0.1)) 
        for _ in range(5)
    ]
    folium.PolyLine(route_coords, color="blue", weight=2.5, opacity=1).add_to(m)
    
    map_html = m._repr_html_()

    return render_template('optimize.html', icon='assets/logo.svg', map_html=map_html, route_optimized=True)


# Entry point
if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=True)
