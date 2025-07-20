#!/usr/bin/python3
"""Renders amenities info"""
from backend.dev_flask.views import app_views

from backend.models import storage
from backend.models import Vehicle

from flask import jsonify, request
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest

from .commons import (fetch_data, fetch_data_id, fetch_process,
                      reach_endpoint, allows)


def get_vehicle(vehicle_id=None):
    """Returns the vehicle using the given id.
    """
    vehicles = fetch_data(Vehicle)
    if not vehicles:
        return jsonify(
            {"error": "No vehicles found"}), 404

    if vehicle_id:
        results = [v.to_dict() for v in vehicles if v.id == vehicle_id]
    else:
        results = [v.to_dict() for v in vehicles]

    return jsonify(results)

@app_views.route('/vehicle/<vehicle_Number>/capacity', methods=['GET'])
def get_vehicle_capacity(vehicle_Number=None):
    """Returns the capacity of the vehicle using the given id.
    """
    print(f"Fetching capacity for vehicle: {vehicle_Number}...")
    if vehicle_Number:
        vehicle = storage.get_one_by(Vehicle, vehicle_number=vehicle_Number)
        if vehicle:
            return jsonify({"capacity": vehicle.capacity}), 200
    return jsonify({"error": "Vehicle not found"}), 404

def add_vehicle(vehicle_id=None):
    """Add new vehicle into the system.
    """
    data = request.get_json()
    if not data:
        raise BadRequest(description='Not a JSON')

    if type(data) == list and len(data) > 0:
        i = 0
        j = 0
        for sub in data:
            if type(sub) is not dict:
                raise BadRequest(description='Not a JSON')
            if 'name' not in sub:
                raise BadRequest(description='Missing name')
            vehicle = storage.get_or_create(Vehicle, **sub)
            if vehicle:
                vehicle.save()
                j += 1
            i += 1
        return jsonify({"message": f"[{j}/{i} vehicles added successfully"}), 201

    if type(data) is not dict:
        raise BadRequest(description='Not a JSON')
    if 'name' not in data:
        raise BadRequest(description='Missing name')
    vehicle = Vehicle(**data)

    vehicle.save()
    return jsonify(vehicle.to_dict()), 201

def delete_vehicle(vehicle_id=None):
    """Deletes vehicle using given id.
    """
    results = fetch_process(Vehicle, filter, vehicle_id)
    if results:
        storage.delete(results[0])
        storage.save()
        return jsonify({}), 200
    raise NotFound()

def update_vehicle(vehicle_id=None):
    """"Updates vehicle given id.
    """
    table_cols = ('id', 'created_at', 'updated_at')

    results = fetch_process(Vehicle, filter, vehicle_id)

    if results:
        data = request.get_json()
        if type(data) is not dict:
            raise BadRequest(description='Not a JSON')
        vehicle_old = results[0]
        for key, value in data.items():
            if key not in table_cols:
                setattr(vehicle_old, key, value)

        vehicle_old.save()
        return jsonify(vehicle_old.to_dict()), 200
    raise NotFound()

@app_views.route('/vehicles', methods=allows)
@app_views.route('/vehicles/<vehicle_id>', methods=allows)
def handle_vehicles(vehicle_id=None):
    """Handles vehicle endpoint.
    """
    vehicle_handlers = reach_endpoint([get_vehicle, add_vehicle,
                                 delete_vehicle, update_vehicle])

    rm = request.method
    if rm in vehicle_handlers:
        return vehicle_handlers[rm](vehicle_id)
    else:
        raise MethodNotAllowed(allows)