#!/usr/bin/python3

import os
""" Agency Module for HBNB project """
from backend.models.base_model import BaseModel, Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer
from dotenv import load_dotenv
load_dotenv()

STORAGE_TYPE = os.getenv("UMPIRE_TYPE_STORAGE", "file")

class Agency(BaseModel, Base):
    """ The agency class, contains agency ID and name """
    if STORAGE_TYPE == "db":
        __tablename__ = 'agencies'
        agency_id = Column(String(20), nullable=True)
        name = Column(String(128), nullable=False)
        agency_url = Column(String(256), nullable=False)
        # Relationships
        terminals = relationship("Terminal", secondary='agency_terminals', back_populates="agencies")
        routes = relationship("Route", secondary='route_agencies', back_populates="agencies")

    else:
        agency_id = ""
        name = ""
        agency_url = ""
        terminals = []
        routes = []
