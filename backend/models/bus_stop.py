#!/usr/bin/python3
""" City Module for HBNB project """

from backend.models.base_model import BaseModel, Base

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from os import getenv


class BusStop(BaseModel, Base):
    """ The bus stop class, contains city ID and name """
    if getenv("UMPIRE_TYPE_STORAGE") == "db":
        __tablename__ = 'bus_stops'
        id = Column(Integer, primary_key=True)
        name = Column(String(128), nullable=False)
        latitude = Column(Float, nullable=False)
        longitude = Column(Float, nullable=False)
        suburb_id = Column(Integer, ForeignKey('suburbs.id'), nullable=False)

        # Relationship to Suburb
        suburb = relationship("Suburb", back_populates="bus_stops")
    else:
        id = ""
        name = ""
        latitude = 0.0
        longitude = 0.0
        suburb_id = ""