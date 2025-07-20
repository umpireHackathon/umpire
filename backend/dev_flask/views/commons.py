#!/usr/bin/bash
"""Has functions and other items common to all views"""
from flask import current_app, jsonify
from backend.models import storage


# Variables
err_msg = ['Not a JSON', 'Missing name']
allows = ['GET', 'POST', 'DELETE', 'PUT']


# helpers
def manipulate(fn, id_, data):
    """A helper func that applies a given function on data using id_"""
    if fn is filter:
        return list(filter(lambda x: x.id == id_, data))
    elif fn is map:
        return list(map(lambda x: x.to_dict(), data))

def fetch_data(obj):
    """Retrieves data from data base"""
    try:
        return storage.all(obj).values()
    except Exception as e:
        print(f"----------------Error fetching data: {e}----------------")
        return []


def fetch_data_id(obj, id_):
    """Retrieves data from data base"""
    try:
        return storage.get(obj, id_)
    except Exception as e:
        return {"error": str(e)}


def fetch_process(obj, fn, id_):
    """Retrieve and process data"""
    data = fetch_data(obj)
    return manipulate(fn, id_, data)


def reach_endpoint(endpoints):
    """Creates a dictionary of methods and their endpoint functions"""
    if not endpoints:
        return {}
    return {allows[n]: i for n, i in enumerate(endpoints)}


def clean_field(props, obj):
    """deletes object's property"""
    obj = obj.to_dict()
    for i in props:
        if i in obj:
            del obj[i]
    return obj


def delete_obj(obj):
    """removes objects from db"""
    if obj:
        storage.delete(obj)
        storage.save()

def fetch_data_url(url):
    """Fetches data from a given internal URL and returns it as JSON"""
    with current_app.test_client() as client:
        response = client.get(url)
    if response.status_code == 200:
        return response.get_json()
    else:
        print(f"Error fetching data: {response.status_code} - {response.text}")
        return {"error": "Failed to fetch data"}, response.status_code
