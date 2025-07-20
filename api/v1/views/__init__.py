#!/usr/bin/python3
"""Houses the blueprint for the flask API"""
from flask import Blueprint

app_views = Blueprint('app_views', __name__, url_prefix='/api/v1/')

# Importing all views to register their routes
# 
from api.v1.views.suburb import *
from api.v1.views.bus_stop import *
from api.v1.views.terminal import *
from api.v1.views.route import *
from api.v1.views.vehicle import *
from api.v1.views.agencies import *

# Prediction views
from api.v1.views.demand_prediction import *
from api.v1.views.travel_time_prediction import *
from api.v1.views.terminal_prediction import *

# Optimization views
from api.v1.views.optimization import *
