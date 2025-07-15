#!/usr/bin/python3
""" BusStop Module for Umpire project """

import os
from dotenv import load_dotenv
from backend.models.base_model import STORAGE_TYPE, BaseModel, Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey
 
load_dotenv()

STORAGE_TYPE = os.getenv("UMPIRE_TYPE_STORAGE", "file")

class BusStop(BaseModel, Base):
    """ The bus stop class, contains city ID and name """
    if STORAGE_TYPE == "db":
        __tablename__ = 'bus_stops'
        name = Column(String(128), nullable=False)
        latitude = Column(Float, nullable=False)
        longitude = Column(Float, nullable=False)
        suburb_id = Column(Integer, ForeignKey('suburbs.id'), nullable=False)
        # Relationships
        suburb = relationship("Suburb", back_populates="bus_stops")
        routes = relationship("Route", secondary='route_stops', back_populates="bus_stops")
    else:
        id = ""
        name = ""
        latitude = 0.0
        longitude = 0.0
        suburb_id = ""
        suburb = None
        routes = []