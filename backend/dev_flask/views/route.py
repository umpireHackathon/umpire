#!/usr/bin/python3
"""Renders amenities info"""
from backend.dev_flask.views import app_views

from backend.models import storage
from backend.models import Route

from flask import jsonify, request
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest

from .commons import (fetch_data, fetch_data_id, fetch_process,
                      reach_endpoint, allows)


def get_route(route_id=None):
    """Returns the route using the given id.
    """
    routes = fetch_data(Route)
    if not routes:
        return jsonify(
            {"error": "No routes found"}), 404

    if route_id:
        results = [v.to_dict() for v in routes if v.id == route_id]
    else:
        results = [v.to_dict() for v in routes]

    return jsonify(results)

def add_route(route_id=None):
    """Add new route into the system.
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
            route = storage.get_or_create(Route, **sub)
            if route:
                route.save()
                j += 1
            i += 1
        return jsonify({"message": f"[{j}/{i} routes added successfully"}), 201

    if type(data) is not dict:
        raise BadRequest(description='Not a JSON')
    if 'name' not in data:
        raise BadRequest(description='Missing name')
    route = Route(**data)

    route.save()
    return jsonify(route.to_dict()), 201

def delete_route(route_id=None):
    """Deletes route using given id.
    """
    results = fetch_process(Route, filter, route_id)
    if results:
        storage.delete(results[0])
        storage.save()
        return jsonify({}), 200
    raise NotFound()

def update_route(route_id=None):
    """"Updates route given id.
    """
    table_cols = ('id', 'created_at', 'updated_at')

    results = fetch_process(Route, filter, route_id)

    if results:
        data = request.get_json()
        if type(data) is not dict:
            raise BadRequest(description='Not a JSON')
        route_old = results[0]
        for key, value in data.items():
            if key not in table_cols:
                setattr(route_old, key, value)

        route_old.save()
        return jsonify(route_old.to_dict()), 200
    raise NotFound()

@app_views.route('/routes', methods=allows)
@app_views.route('/routes/<route_id>', methods=allows)
def handle_routes(route_id=None):
    """Handles route endpoint.
    """
    route_handlers = reach_endpoint([get_route, add_route,
                                 delete_route, update_route])

    rm = request.method
    if rm in route_handlers:
        return route_handlers[rm](route_id)
    else:
        raise MethodNotAllowed(allows)