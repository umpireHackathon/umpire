#!/usr/bin/python3
"""
Starting the Flask app for Umpire
<a target="_blank" href="https://icons8.com/icon/M8to8q11r1v5/bus-stop">Bus Stop</a> icon by <a target="_blank" href="https://icons8.com">Icons8</a>
"""

from datetime import datetime
import os
import random
import re
import folium
from folium.features import CustomIcon
from folium.features import DivIcon
from folium.elements import Element
import uuid
import numpy as np
from werkzeug.utils import secure_filename
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
UPLOAD_FOLDER = os.getenv("UMPIRE_UPLOAD_FOLDER", "data/uploads")
UPLOAD_FOLDER_LOC = os.getenv("UMPIRE_UPLOAD_FOLDER_LOC")

if UPLOAD_FOLDER_LOC == "local":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

# Set upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ------------------------Helper Functions-----------------
def get_list_from_string(s):
    """Extracts all wordandnumber from a string formatted like '[wordandnumber, wordandnumber, ...]'."""
    if isinstance(s, str):
     return re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', s, re.IGNORECASE)
    return []

def get_values_for_ids(s, db:list[dict]=None):
    """Converts a string of IDs to a list of IDs."""
    ids = get_list_from_string(s)
    func = lambda i, r: r['id'] == i
    if db is None:
        return ids
    return list(map(lambda i: next((r['name'] for r in db if func(i, r)), None), ids))

def choose_routes(number_of_routes=3):
    """Choose allowed routes for a vehicle."""
    import numpy as np
    from backend.models.route import Route
    from backend.models import storage
    
    routes_db = storage.all(Route)

    if not routes_db:
        return []
    routes = {}
    for route in routes_db.values():
        if routes.get(route.distance_km):
            continue
        routes[route.distance_km] = route.id
    # print(f"Available routes: {routes}")
    return [
        routes[k] for k in np.random.choice(list(routes.keys()), size=number_of_routes, replace=False)
    ]

def choose_data_for_optimization(vehicles=None, from_db=False, num_vehicles=10):
    """Export vehicles to CSV.
    required columns:['vehicle_number', 'capacity', 'average_sales', 'allowed_routes']
    """
    import numpy as np
    import pandas as pd
    from backend.models.vehicle import Vehicle
    from backend.models import storage

    day = datetime.now().strftime("%A").lower()
    if from_db:
        # If no vehicles provided, fetch all vehicles from storage
        # and add random data for optimization
        vehicles = storage.all(Vehicle)
        cols = ['vehicle_number', 'capacity']
        if vehicles:
            try:
                df = pd.DataFrame([v.to_dict() for v in vehicles.values()])
                df = df[cols][0:num_vehicles] if num_vehicles else df[cols]
                df = df.drop_duplicates(subset=cols)
                df["average_sales"] = np.random.randint(100, 600, size=len(df))
                df["allowed_routes"] = None
                df["allowed_routes"] = df["allowed_routes"].apply(lambda _: choose_routes(np.random.randint(1, 11)))
                filename = f"{day}_vehicles.csv"
                vehicles = {'data': df, 'filename': filename}
                safe_name = secure_filename(filename)
            except Exception as e:
                print(f"Error processing vehicles: {e}")
                return None
    else:
        # If vehicles provided, process them for optimization
        if not vehicles['data'].empty:
            try:
                filename = f"{day}_{vehicles.get('filename')}"
                safe_name = secure_filename(filename)
            except Exception as e:
                print(f"Error processing uploaded vehicles: {e}")
                return None
    
    unique_filename = f"{uuid.uuid4().hex}_{safe_name}"
    if UPLOAD_FOLDER_LOC == "local":
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        vehicles['data'].to_csv(file_path, index=False)
    else:
        from google.cloud import storage as gcs
        client = gcs.Client()
        bucket = client.bucket(os.getenv('BUCKET_NAME'))
        blob = bucket.blob(os.getenv('SOURCE_BLOB_NAME', unique_filename))
        blob.upload_from_string(vehicles['data'].to_csv(index=False), content_type='text/csv')

    return unique_filename




# -----------------------------Flask App Routes-----------------

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
        terminals = fetch_data_url('/api/terminals')
        
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

    if user_action and user_action == 'show_stops':
        # Fetch stops from the API
        stops = fetch_data_url('/api/bstops')
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

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Handles file upload and returns a confirmation message"""
    import pandas as pd

    if request.method == 'POST':

        numVehicles = int(request.form.get('numVehicles', 0))
        if not request.form.get('loadFromDB'):
            uploaded_file = request.files.get('file')
            print(f"Received POST request for file upload: {request.form.get('loadFromDB')}")
            unique_filename = None
            # converted the uploaded csv file to df
            if uploaded_file:
                try:
                    vehicles = pd.read_csv(uploaded_file)
                    unique_filename = choose_data_for_optimization({'data': vehicles, 'filename': uploaded_file.filename})
                except pd.errors.EmptyDataError as e:
                    return jsonify({"error": f"Invalid CSV data: {str(e)}"}), 400
            else:
                return jsonify({"error": "No file uploaded"}), 400
        
        else:
            # If the request is from the database upload button
            unique_filename = choose_data_for_optimization(from_db=True, num_vehicles=numVehicles)
        return jsonify({"filename": unique_filename, "numVehicles": numVehicles}), 200

@app.route('/optimize')
def optimize():
    from datetime import datetime
    import pandas as pd
    from backend.models import storage
    from backend.models.vehicle import Vehicle

    numVehicles = int(request.args.get('numVehicles', 0))
    print(f"Number of vehicles for optimization: {numVehicles}")
    vehicles = requests.get(f'http://127.0.0.1:{PORT}/api/vehicles', timeout=5).json()
    routes = requests.get(f'http://127.0.0.1:{PORT}/api/routes', timeout=5).json()
    
    # Get uploaded file name from query parameters, process it for optimization
    stats_desc = None
    vehicle_data = None
    predicted_demand = None
    predicted_stops = None

    filename = request.args.get('filename')
    # Read the uploaded file if provided
    if filename:
        if UPLOAD_FOLDER_LOC == "local":
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
            if not os.path.isfile(filepath):
                return f"File not found: {filename}", 404
            try:
                if numVehicles:
                    predicted_demand = np.random.randint(100, 600, size=numVehicles)
                    predicted_stops = np.random.randint(1, 5, size=numVehicles)
                df = pd.read_csv(filepath)
                df['allowed_routes'] = df['allowed_routes'].apply(lambda x: get_values_for_ids(x, routes))
                df['predicted_demand'] = predicted_demand
                df['predicted_stops'] = predicted_stops
                stats_desc = df.describe(include='all').fillna("").to_html(classes='stats-table')
                vehicle_data = df.to_html(classes='stats-table')
                filename = filename.split('_')[1:]  # Remove file extension for display
                filename = ' '.join(filename)  # Join the parts back into a string
            except Exception as e:
                return f"Error reading file: {e}", 500
        else:
            # For cloud storage, fetch the file content
            from google.cloud import storage as gcs
            client = gcs.Client()
            bucket = client.bucket(os.getenv('BUCKET_NAME'))
            blob = bucket.blob(os.getenv('SOURCE_BLOB_NAME', filename))
            try:
                content = blob.download_as_text()
                df = pd.read_csv(pd.compat.StringIO(content))
                df['allowed_routes'] = df['allowed_routes'].apply(lambda x: get_values_for_ids(x, routes))
                df['predicted_demand'] = np.random.randint(100, 600, size=len(df))
                df['predicted_stops'] = np.random.randint(1, 5, size=len(df))
                stats_desc = df.describe(include='all').fillna("").to_html(classes='stats-table')
                vehicle_data = df.to_html(classes='stats-table')
            except Exception as e:
                return f"Error reading file from cloud: {e}", 500
    day = datetime.now().strftime("%A").lower()
    data = {"vehicles": vehicles, "routes": routes, "day": day, "stats": [stats_desc, vehicle_data]}

    return render_template('optimize.html', optimizationData=data, filename=filename)


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