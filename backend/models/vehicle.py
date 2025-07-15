#!/usr/bin/python3
""" Vehicle Module for Umpire project """

import os
from dotenv import load_dotenv
from backend.models.base_model import BaseModel, Base
from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship

load_dotenv()

STORAGE_TYPE = os.getenv("UMPIRE_TYPE_STORAGE", "file")
# Sources files
wrkdir = os.path.dirname(os.path.abspath(__file__))  # full absolute path to current script
src_vehicle_icon = os.path.abspath(os.path.join(wrkdir, "../../assets/bus3.png"))

class Vehicle(BaseModel, Base):
    """ The vehicle class, contains vehicle ID and name """
    if STORAGE_TYPE == "db":
        __tablename__ = 'vehicles'
        vehicle_number = Column(String(128), nullable=False)
        latitude = Column(Float, nullable=True)
        longitude = Column(Float, nullable=True)
        capacity = Column(Integer, nullable=False)
        assigned = Column(Boolean, default=False, nullable=False)
        icon = Column(String(255), nullable=False, default=src_vehicle_icon)
        # Relationship to Route
        routes = relationship("Route", secondary='routed_vehicles', back_populates="vehicles")

    else:
        name = ""
        vehicle_number = ""
        latitude = 0.0
        longitude = 0.0
        capacity = 0
        assigned = False
        routes = []

        @property
        def routes(self):
            """Get the list of routes for the vehicle"""
            from backend.models.route import Route
            from backend import models
            route_lists = []
            for route in models.storage.all(Route).values():
                if self.id in [vehicle.id for vehicle in route.vehicles]:
                    route_lists.append(route)
            return route_lists