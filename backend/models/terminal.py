# /usr/bin/python3
""" Terminal Module for Umpire project """

import os
from dotenv import load_dotenv
from backend import models
from backend.models.base_model import BaseModel, Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.models.route import Route

load_dotenv()

STORAGE_TYPE = os.getenv("UMPIRE_TYPE_STORAGE", "file")


class Terminal(BaseModel, Base):
    """ The terminal class, contains terminal ID and name """
    if STORAGE_TYPE == "db":
        __tablename__ = 'terminals'
        terminal_id = Column(String(20), nullable=True)
        name = Column(String(128), nullable=False)
        latitude = Column(Float, nullable=False)
        longitude = Column(Float, nullable=False)
        suburb_id = Column(Integer, ForeignKey('suburbs.id'), nullable=True)

        # Relationship to Suburb
        suburb = relationship("Suburb", back_populates="terminals")
        # Relationship to Route
        routes = relationship("Route", secondary='route_terminals', back_populates="terminals")
        # Relationship to Agency
        agencies = relationship("Agency", secondary='agency_terminals', back_populates="terminals")

    else:
        terminal_id = ""
        name = ""
        latitude = 0.0
        longitude = 0.0
        suburb_id = ""
        routes = []
        @property
        def routes(self):
            """Get the list of routes for the terminal"""
            route_lists = []
            for route in models.storage.all(Route).values():
                if self.id in [terminal.id for terminal in route.terminals]:
                    route_lists.append(route)
            return route_lists
