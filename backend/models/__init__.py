#!/usr/bin/python3
"""create a unique FileStorage instance for your application"""

import os

from backend.models.agency import Agency
from backend.models.bus_stop import BusStop
from backend.models.route import Route
from backend.models.ml_model import MLModel
from backend.models.terminal import Terminal
from backend.models.suburb import Suburb
from backend.models.vehicle import Vehicle
from backend.models.trip import VehicleTrip
from backend.models.user import User
from backend.models.association import route_terminals, routed_vehicles, agency_terminals, route_agencies, route_stops

from dotenv import load_dotenv

load_dotenv()

storage_type = os.getenv("UMPIRE_TYPE_STORAGE", "file")

storage = None

if storage_type == "db":
    from backend.models.engine.db_storage import DBStorage
    storage = DBStorage()
else:
    from backend.models.engine.file_storage import FileStorage
    storage = FileStorage()
storage.reload()




