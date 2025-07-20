#!/usr/bin/python3
"""Renders agencies info"""

from api.v1.views import app_views
from backend.models import storage
from backend.models import Agency
from flask import jsonify, request
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest
from .commons import (fetch_data, fetch_data_id, fetch_process,
                      reach_endpoint, allows)


def get_agency(agency_id=None):
    """Returns the agency using the given id.
    """
    agencies = fetch_data(Agency)
    if not agencies:
        return jsonify(
            {"error": "No agencies found"}), 404

    if agency_id:
        results = [v.to_dict() for v in agencies if v.id == agency_id]
    else:
        results = [v.to_dict() for v in agencies]

    return jsonify(results)

def add_agency(agency_id=None):
    """Add new agency into the system.
    """
    data = request.get_json()
    if not data:
        raise BadRequest(description='Not a JSON')

    if type(data) == list and len(data) > 0:
        i = 0
        j = 0
        for agency in data:
            if type(agency) is not dict:
                raise BadRequest(description='Not a JSON')
            if 'name' not in agency:
                raise BadRequest(description='Missing name')
            agency = storage.get_or_create(Agency, **agency)
            if agency:
                agency.save()
                j += 1
            i += 1
        return jsonify({"message": f"[{j}/{i} agencies added successfully"}), 201

    if type(data) is not dict:
        raise BadRequest(description='Not a JSON')
    if 'name' not in data:
        raise BadRequest(description='Missing name')
    agency = Agency(**data)

    agency.save()
    return jsonify(agency.to_dict()), 201

def delete_agency(agency_id=None):
    """Deletes agency using given id.
    """
    results = fetch_process(Agency, filter, agency_id)
    if results:
        storage.delete(results[0])
        storage.save()
        return jsonify({}), 200
    raise NotFound()

def update_agency(agency_id=None):
    """"Updates agency given id.
    """
    table_cols = ('id', 'created_at', 'updated_at')

    results = fetch_process(Agency, filter, agency_id)

    if results:
        data = request.get_json()
        if type(data) is not dict:
            raise BadRequest(description='Not a JSON')
        agency_old = results[0]
        for key, value in data.items():
            if key not in table_cols:
                setattr(agency_old, key, value)

        agency_old.save()
        return jsonify(agency_old.to_dict()), 200
    raise NotFound()

@app_views.route('/agencies', methods=allows)
@app_views.route('/agencies/<agency_id>', methods=allows)
def handle_agencies(agency_id=None):
    """Handles agencies endpoint.
    """
    agency_handlers = reach_endpoint([get_agency, add_agency,
                                 delete_agency, update_agency])

    rm = request.method
    if rm in agency_handlers:
        return agency_handlers[rm](agency_id)
    else:
        raise MethodNotAllowed(allows)