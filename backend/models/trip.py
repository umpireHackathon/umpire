from backend.models import storage_type

from backend import models
from backend.models.base_model import BaseModel, Base
from sqlalchemy import Column, Integer, String, Boolean


class VehicleTrip(BaseModel, Base):
    """ The trip class"""
    if storage_type == "db":
        __tablename__ = 'trips'
        is_active = Column(Boolean, default=False, nullable=False)
        vehicle_id = Column(String(128), nullable=False)  # ID of the vehicle assigned to the trip
        route_id = Column(String(128), nullable=False)  # ID of the route for the trip
        number_of_stops = Column(Integer, nullable=False, default=0)  # Number of stops in the trip
        origin_terminal_id = Column(String(128), nullable=False)  # ID of the origin terminal
        destination_terminal_id = Column(String(128), nullable=False)  # ID of the destination terminal

    else:
        is_active = False
        vehicle_id = ""
        route_id = ""
        number_of_stops = 0
        origin_terminal_id = ""
        destination_terminal_id = ""
