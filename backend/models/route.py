#!/usr/bin/python3
""" City Module for HBNB project """

from turtle import st
from backend import models
from backend.models import storage_type
from backend.models.base_model import BaseModel, Base
from backend.models.vehicle import Vehicle
from backend.models.terminal import Terminal
from backend.models.bus_stop import BusStop

from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, Table
from os import getenv

if storage_type == "db":
    from backend.models.association import route_terminals, routed_vehicles

class Route(BaseModel, Base):
    """ The route class, contains city ID and name """
    if storage_type == "db":
        __tablename__ = 'routes'
        name = Column(String(128), nullable=False)
        distance = Column(Float, nullable=False)
        # Relationships
        bus_stops = relationship("BusStop", back_populates="route")
        terminals = relationship("Terminal", secondary=route_terminals, back_populates="routes")
        vehicles = relationship("Vehicle", secondary=routed_vehicles, back_populates="routes")
    else:
        id = ""
        name = ""
        distance = 0.0
        travel_time = 0.0
        bus_stops = []
        vehicles = []
        terminals = []      

        @property
        def stops(self):
            """Get the list of bus stops for the route"""
            stop_lists = []
            for stop in models.storage.all(BusStop).values():
                if stop.route_id == self.id:
                    stop_lists.append(stop)
            return stop_lists
        @property
        def vehicles(self):
            """Get the list of vehicles for the route"""
            vehicle_lists = []
            for vehicle in models.storage.all(Vehicle).values():
                if self.id in [route.id for route in vehicle.routes]:
                    vehicle_lists.append(vehicle)
            return vehicle_lists
        @property
        def terminals(self):
            """Get the list of terminals for the route"""
            terminal_lists = []
            for terminal in models.storage.all(Terminal).values():
                if self.id in [route.id for route in terminal.routes]:
                    terminal_lists.append(terminal)
            return terminal_lists

        @stops.setter
        def stops(self, value):
            """Setter for stops"""

            if not isinstance(value, BusStop):
                raise TypeError("Expected a BusStop instance")

            if value not in self.stops:
                self.stops.append(value)
        @terminals.setter
        def terminals(self, value):
            """Setter for terminals"""

            if not isinstance(value, Terminal):
                raise TypeError("Expected a Terminal instance")

            if value not in self.terminals:
                self.terminals.append(value)
        @vehicles.setter
        def vehicles(self, value):
            """Setter for vehicles"""

            if not isinstance(value, Vehicle):
                raise TypeError("Expected a Vehicle instance")

            if value not in self.vehicles:
                self.vehicles.append(value)