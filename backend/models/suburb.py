#!/usr/bin/python3
""" Suburb Module for Umpire project """

import os
from dotenv import load_dotenv
from backend import models
from backend.models.base_model import BaseModel, Base
from sqlalchemy import Column, String, Float
from sqlalchemy.orm import relationship

load_dotenv()

STORAGE_TYPE = os.getenv("UMPIRE_TYPE_STORAGE", "file")


class Suburb(BaseModel, Base):
    """ The suburb class, contains suburb ID and name """
    if STORAGE_TYPE == "db":
        __tablename__ = 'suburbs'
        name = Column(String, nullable=False)
        latitude = Column(Float, nullable=False)
        longitude = Column(Float, nullable=False)
        
        # Relationship to BusStop
        bus_stops = relationship("BusStop", back_populates="suburb")
        # Relationship to Terminal
        terminals = relationship("Terminal", back_populates="suburb")

    else:
        id = ""
        name = ""
        latitude = 0.0
        longitude = 0.0
        bus_stops = []
        
        @property
        def bus_stops(self):
            
            """Get the list of bus stops in the suburb"""
            from backend.models.bus_stop import BusStop
            bus_stop_lists = []
            for bus_stop in models.storage.all(BusStop).values():
                if bus_stop.suburb_id == self.id:
                    bus_stop_lists.append(bus_stop)
            return bus_stop_lists
