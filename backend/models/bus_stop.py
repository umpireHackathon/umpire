#!/usr/bin/python3

from backend.models import storage_type
from backend.models.base_model import BaseModel, Base

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from os import getenv


class BusStop(BaseModel, Base):
    """ The bus stop class, contains city ID and name """
    if storage_type == "db":
        __tablename__ = 'bus_stops'
        name = Column(String(128), nullable=False)
        latitude = Column(Float, nullable=False)
        longitude = Column(Float, nullable=False)
        suburb_id = Column(Integer, ForeignKey('suburbs.id'), nullable=False)
        route_id = Column(Integer, ForeignKey('routes.id'), nullable=True)
        # Relationships
        suburb = relationship("Suburb", back_populates="bus_stops")
    else:
        id = ""
        name = ""
        latitude = 0.0
        longitude = 0.0
        suburb_id = ""
        route_id = ""