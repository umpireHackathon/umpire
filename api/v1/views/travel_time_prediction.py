#!/usr/bin/python3
"""Renders predicted demand info"""
from api.v1.views import app_views
from flask import jsonify, request
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest
import pandas as pd
import joblib
import os
from backend.models import storage
from backend.models import Route
import datetime

@app_views.route('/travel_time_prediction', methods=['GET'])
def get_travel_time_prediction():
    """Returns the travel time prediction.
    Args:
        route_id (str): The ID of the route for which to predict travel time.
        day_name (str): The day of the week for which to predict travel time.
        origin (str): The origin location for the travel time prediction.
        destination (str): The destination location for the travel time prediction.
    """
    print("Fetching travel time prediction...")

    route_id = request.args.get("route_id")
    day_name = request.args.get("day_name")   
    if not route_id or not day_name:
        return jsonify({"error": "Route ID and day_name are required"}), 400
    
    # fetch the route details
    route = storage.get_one_by(Route, id=route_id)
    if not route:
        return jsonify({"error": "Route not found"}), 404
    route_stops = route.bus_stops if route.bus_stops else []
    if not route_stops:
        return jsonify({"error": "Route has no stops"}), 404
    
    route_type = "bus"
    origin = route.name.split(" to ")[0] if " to " in route.name else route.name
    destination = route.name.split(" to ")[-1] if " to " in route.name else route.name

    hour_of_day = datetime.datetime.now().hour
    trip_distance_km = route.distance_km if hasattr(route, 'distance_km') else 5.0


    sample_input = {
        "route_type": route_type,
        "hour_of_day": hour_of_day,
        "trip_distance_km": trip_distance_km,
        "day_name": day_name,
        "origin": origin,
        "destination": destination
    }

    # Load model and feature structure

    # ur = f"https://ml-prediction-103109607498.europe-west1.run.app"
    categories={'day_name': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']}
    print("Loading travel time prediction model...")
    path = os.path.dirname(os.path.abspath(__file__))
    loaded_model = joblib.load(os.path.join(path, "ml_model_travel_time_rf_travel_time_model.joblib"))
    feature_columns = joblib.load(os.path.join(path, "ml_model_travel_time_travel_time_features.joblib"))
    preprocessor = joblib.load(os.path.join(path, "ml_model_travel_time_travel_time_preprocessor.joblib"))
    print("Model loaded successfully.")

    # Convert sample_input to a pandas DataFrame
    sample_input_df = pd.DataFrame([sample_input], columns=list(sample_input))
    # Ensure the DataFrame has the correct feature order as expected by the preprocessor
    sample_input_df = sample_input_df[feature_columns]  # Reorder columns to match feature_columns
    # Apply the preprocessor to transform the input data
    try:
        processed_input = preprocessor.transform(sample_input_df)
    except Exception as e:
        print(f"Error during preprocessing: {e}")
        return jsonify({"error_preprocessor": "Preprocessing failed"}), 500
    
    # Make predictions using the loaded model
    try:
        prediction = loaded_model.predict(processed_input)
        print("Predicted travel time:", prediction[0])  # Assuming regression output (single value)
    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({"error_prediction": "Prediction failed"}), 500
    return jsonify({
        "message": "Travel time prediction model loaded successfully.",
        "feature_columns": [i for i in feature_columns],
        "prediction": prediction[0]
    }), 200