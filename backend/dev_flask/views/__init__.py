#!/usr/bin/python3
"""Houses the blueprint for the flask API"""
from flask import Blueprint

app_views = Blueprint('app_views', __name__, url_prefix='/api')

# Importing all views to register their routes
# 
from backend.dev_flask.views.suburb import *
from backend.dev_flask.views.bus_stop import *
from backend.dev_flask.views.terminal import *
from backend.dev_flask.views.route import *
from backend.dev_flask.views.vehicle import *


# Prediction views
from backend.dev_flask.views.demand_prediction import *
from backend.dev_flask.views.travel_time_prediction import *
from backend.dev_flask.views.terminal_prediction import *
