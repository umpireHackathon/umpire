#!/usr/bin/python3
""" City Module for HBNB project """

import os
from dotenv import load_dotenv
from backend.models.base_model import BaseModel, Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Float

load_dotenv()

STORAGE_TYPE = os.getenv("UMPIRE_TYPE_STORAGE", "file")


class Route(BaseModel, Base):
    """ The route class, contains city ID and name """
    if STORAGE_TYPE == "db":
        __tablename__ = 'routes'
        name = Column(String(128), nullable=False)
        distance_km = Column(Float, nullable=False)
        # Relationships
        bus_stops = relationship("BusStop", secondary='route_stops', back_populates="routes")
        terminals = relationship("Terminal", secondary='route_terminals', back_populates="routes")
        vehicles = relationship("Vehicle", secondary='routed_vehicles', back_populates="routes")
        agencies = relationship("Agency", secondary='route_agencies', back_populates="routes")
    else:
        id = ""
        name = ""
        distance = 0.0
        travel_time = 0.0
        bus_stops = []
        vehicles = []
        terminals = []
        agencies = []

        @property
        def stops(self):
            """Get the list of bus stops for the route"""
            from backend.models.bus_stop import BusStop
            from backend import models
            stop_lists = []
            for stop in models.storage.all(BusStop).values():
                if stop.route_id == self.id:
                    stop_lists.append(stop)
            return stop_lists
        @property
        def vehicles(self):
            """Get the list of vehicles for the route"""
            from backend.models.vehicle import Vehicle
            from backend import models
            vehicle_lists = []
            for vehicle in models.storage.all(Vehicle).values():
                if self.id in [route.id for route in vehicle.routes]:
                    vehicle_lists.append(vehicle)
            return vehicle_lists
        @property
        def terminals(self):
            """Get the list of terminals for the route"""
            from backend.models.terminal import Terminal
            from backend import models
            terminal_lists = []
            for terminal in models.storage.all(Terminal).values():
                if self.id in [route.id for route in terminal.routes]:
                    terminal_lists.append(terminal)
            return terminal_lists