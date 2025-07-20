#!/usr/bin/python3
"""Renders bus_stops info"""

from api.v1.views import app_views
from backend.models import storage
from backend.models import BusStop
from flask import jsonify, request
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest
from .commons import (fetch_data, fetch_data_id, fetch_process,
                      reach_endpoint, allows)


def get_bus_stop(bus_stop_id=None):
    """Returns the bus stop using the given id.
    """
    bus_stops = fetch_data(BusStop)
    if not bus_stops:
        return jsonify(
            {"error": "No bus stops found"}), 404

    if bus_stop_id:
        results = [v.to_dict() for v in bus_stops if v.id == bus_stop_id]
    else:
        results = [v.to_dict() for v in bus_stops]

    return jsonify(results)

def add_bus_stop(bus_stop_id=None):
    """Add new bus stop into the system.
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
            bus_stop = storage.get_or_create(BusStop, **sub)
            if bus_stop:
                bus_stop.save()
                j += 1
            i += 1
        return jsonify({"message": f"[{j}/{i} bus stops added successfully"}), 201

    if type(data) is not dict:
        raise BadRequest(description='Not a JSON')
    if 'name' not in data:
        raise BadRequest(description='Missing name')
    bus_stop = BusStop(**data)

    bus_stop.save()
    return jsonify(bus_stop.to_dict()), 201

def delete_bus_stop(bus_stop_id=None):
    """Deletes bus stop using given id.
    """
    results = fetch_process(BusStop, filter, bus_stop_id)
    if results:
        storage.delete(results[0])
        storage.save()
        return jsonify({}), 200
    raise NotFound()

def update_bus_stop(bus_stop_id=None):
    """"Updates bus stop given id.
    """
    table_cols = ('id', 'created_at', 'updated_at')

    results = fetch_process(BusStop, filter, bus_stop_id)

    if results:
        data = request.get_json()
        if type(data) is not dict:
            raise BadRequest(description='Not a JSON')
        bus_stop_old = results[0]
        for key, value in data.items():
            if key not in table_cols:
                setattr(bus_stop_old, key, value)

        bus_stop_old.save()
        return jsonify(bus_stop_old.to_dict()), 200
    raise NotFound()

@app_views.route('/bstops', methods=allows)
@app_views.route('/bstops/<bus_stop_id>', methods=allows)
def handle_bus_stops(bus_stop_id=None):
    """Handles bus stops endpoint.
    """
    bus_stop_handlers = reach_endpoint([get_bus_stop, add_bus_stop,
                                 delete_bus_stop, update_bus_stop])

    rm = request.method
    if rm in bus_stop_handlers:
        return bus_stop_handlers[rm](bus_stop_id)
    else:
        raise MethodNotAllowed(allows)