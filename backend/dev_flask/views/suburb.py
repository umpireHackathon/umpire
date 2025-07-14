#!/usr/bin/python3
"""Renders amenities info"""
from backend.dev_flask.views import app_views

from backend.models import storage
from backend.models import Suburb

from flask import jsonify, request
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest
from .commons import (manipulate, fetch_data, fetch_data_id, fetch_process,
                      reach_endpoint, allows, err_msg)

def get_suburb(suburb_id=None):
    """Returns the suburb using the given id.
    """
    sub_all = fetch_data(Suburb)
    if not sub_all:
        return jsonify(
            {"error": "No suburbs found"}), 404
    
    if suburb_id:
        results = [v.to_dict() for v in sub_all if v.id == suburb_id]
    else:
        results = [v.to_dict() for v in sub_all]

    return jsonify(results)

def add_suburb(suburb_id=None):
    """Add new suburb into the system.
    """
    
    req_d = request.get_json()
    print("=============", type(req_d), "================")

    if len(req_d) == 0:
        raise BadRequest(description='Not a JSON')

    if type(req_d) == list and len(req_d) > 0:
        i = 0
        for sub in req_d:
            if type(sub) is not dict:
                raise BadRequest(description='Not a JSON')
            if 'name' not in sub:
                raise BadRequest(description='Missing name')
            sub_obj = Suburb(**sub)
            sub_obj.save()
            i += 1
        return jsonify({"message": f"{i} suburbs added successfully"}), 201
    
    if type(req_d) is not dict:
        raise BadRequest(description='Not a JSON')
    if 'name' not in req_d:
        raise BadRequest(description='Missing name')
    sub_obj = Suburb(**req_d)

    sub_obj.save()
    return jsonify(sub_obj.to_dict()), 201


def delete_suburb(suburb_id=None):
    """Deletes suburb using given id.
    """
    results = fetch_process(Suburb, filter, suburb_id)
    if results:
        storage.delete(results[0])
        storage.save()
        return jsonify({}), 200
    raise NotFound()


def update_suburb(suburb_id=None):
    """"Updates suburb given id.
    """
    table_cols = ('id', 'created_at', 'updated_at')

    results = fetch_process(Suburb, filter, suburb_id)

    if results:
        data = request.get_json()
        if type(data) is not dict:
            raise BadRequest(description='Not a JSON')
        sub_old = results[0]
        for key, value in data.items():
            if key not in table_cols:
                setattr(sub_old, key, value)

        sub_old.save()
        return jsonify(sub_old.to_dict()), 200
    raise NotFound()


@app_views.route('/suburbs', methods=allows)
@app_views.route('/suburbs/<suburb_id>', methods=allows)
def handle_suburbs(suburb_id=None):
    """Handles suburbs endpoint.
    """
    sub_handlers = reach_endpoint([get_suburb, add_suburb,
                                 delete_suburb, update_suburb])

    rm = request.method
    if rm in sub_handlers:
        return sub_handlers[rm](suburb_id)
    else:
        raise MethodNotAllowed(allows)