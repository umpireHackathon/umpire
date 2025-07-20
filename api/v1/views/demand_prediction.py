#!/usr/bin/python3
"""Renders predicted demand info"""
from api.v1.views import app_views
from flask import jsonify, request
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest
import pandas as pd
import joblib
import os
import requests


# def data_input(input_dict, feature_s, feature_categories):
    
#     """Function to handle data input for demand prediction."""
#     # authenticate input_dict
#     if not isinstance(input_dict, dict):
#         return {"error": "Input must be a dictionary"}
#     # sample_data = {
#     #     "agency_id": 5,
#     #     "day_name": "monday",
#     # }
#     df_input = pd.DataFrame([input_dict])
#     df_input['day_name'] = pd.Categorical(df_input['day_name'], categories=feature_categories, ordered=True)
#     df_input = pd.get_dummies(df_input, columns=['day_name'])
#     for col in feature_s:
#         if col not in df_input.columns:
#             df_input[col] = 0
#     df_input = df_input[feature_s]
#     return df_input

# @app_views.route('/demand_prediction', methods=['GET'])
# def get_demand_prediction():
#     """Returns the demand prediction."""
    
#     # Load model and feature structure

#     # ur = f"https://ml-prediction-103109607498.europe-west1.run.app"

#     path = os.path.dirname(os.path.abspath(__file__))
#     loaded_model = joblib.load(os.path.join(path, "ml_model_demand_rf_demand_model.joblib"))
#     feature_columns_agency_id = joblib.load(os.path.join(path, "ml_model_demand_rf_demand_columns.joblib"))

#     feature_columns_categories = joblib.load(os.path.join(path, "ml_model_demand_day_categories.joblib"))

#     sample_data = {
#         "agency_id": 5,
#         "day_name": "monday",
#     }
#     sample_data = {}

#     request_json = request.get_json(silent=True)

#     if request.method != 'GET':
#         return jsonify({"error": "Method not allowed"}), 405

#     sample_data = {}

#     if request_json:
#         if 'agency_id' in request_json:
#             try:
#                 sample_data['agency_id'] = int(request_json['agency_id'])
#             except:
#                 return jsonify({"error": "agency_id is not int"}), 405
#         else:
#             return jsonify({"error": "agency_id is required"}), 400


#     df_input = data_input(sample_data, feature_columns_agency_id, feature_columns_categories)

#     prediction = loaded_model.predict(df_input)

#     return jsonify({"predicted_demand": prediction[0]}), 200



@app_views.route('/demand_prediction', methods=['GET'])
def get_demand_prediction():
    """Sends input to ML service and returns demand prediction."""

    try:
        prediction_url = "https://ml-prediction-103109607498.europe-west1.run.app/"
        
        if request.method != 'GET':
            return jsonify({"error": "Method not allowed"}), 405
        input_data = request.get_json(silent=True)
        if not input_data:
            return jsonify({"error": "No input data provided"}), 400
        if 'agency_id' not in input_data or not input_data['agency_id']:
            return jsonify({"error": "agency_id is required"}), 400
        if 'day_name' not in input_data or not input_data['day_name']:
            return jsonify({"error": "day_name is required"}), 400
        
        input_data['day_name'] = input_data['day_name'].lower()  # Ensure day_name is lowercase
        input_data['agency_id'] = int(input_data['agency_id'])  # Ensure agency_id is an integer
        
        response = requests.post(prediction_url, json=input_data)
        print(f"==========Response status code: {response.status_code}==========")
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch prediction"}), response.status_code

        prediction_data = response.json()
        return jsonify(prediction_data), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch prediction: {str(e)}"}), 500