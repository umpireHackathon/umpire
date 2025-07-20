#!/usr/bin/python3
"""Renders amenities info"""

from backend.dev_flask.views import app_views
from backend.models import storage
from backend.models import Terminal
from flask import jsonify, request
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest
from .commons import (fetch_data, fetch_data_id, fetch_process,
                      reach_endpoint, allows)


def get_terminal(terminal_id=None):
    """Returns the terminal using the given id.
    """
    terminals = fetch_data(Terminal)
    if not terminals:
        return jsonify(
            {"error": "No terminals found"}), 404

    if terminal_id:
        results = [v.to_dict() for v in terminals if v.id == terminal_id]
    else:
        results = [v.to_dict() for v in terminals]

    return jsonify(results)

def add_terminal(terminal_id=None):
    """Add new terminal into the system.
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
            terminal = storage.get_or_create(Terminal, **sub)
            if terminal:
                terminal.save()
                j += 1
            i += 1
        return jsonify({"message": f"[{j}/{i} terminals added successfully"}), 201

    if type(data) is not dict:
        raise BadRequest(description='Not a JSON')
    if 'name' not in data:
        raise BadRequest(description='Missing name')
    terminal = Terminal(**data)

    terminal.save()
    return jsonify(terminal.to_dict()), 201

def delete_terminal(terminal_id=None):
    """Deletes terminal using given id.
    """
    results = fetch_process(Terminal, filter, terminal_id)
    if results:
        storage.delete(results[0])
        storage.save()
        return jsonify({}), 200
    raise NotFound()

def update_terminal(terminal_id=None):
    """"Updates terminal given id.
    """
    table_cols = ('id', 'created_at', 'updated_at')

    results = fetch_process(Terminal, filter, terminal_id)

    if results:
        data = request.get_json()
        if type(data) is not dict:
            raise BadRequest(description='Not a JSON')
        terminal_old = results[0]
        for key, value in data.items():
            if key not in table_cols:
                setattr(terminal_old, key, value)

        terminal_old.save()
        return jsonify(terminal_old.to_dict()), 200
    raise NotFound()

@app_views.route('/terminals', methods=allows)
@app_views.route('/terminals/<terminal_id>', methods=allows)
def handle_terminals(terminal_id=None):
    """Handles terminal endpoint.
    """
    terminal_handlers = reach_endpoint([get_terminal, add_terminal,
                                 delete_terminal, update_terminal])

    rm = request.method
    if rm in terminal_handlers:
        return terminal_handlers[rm](terminal_id)
    else:
        raise MethodNotAllowed(allows)