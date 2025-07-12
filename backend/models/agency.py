#!/usr/bin/python3

from backend.models import storage_type
from backend.models.base_model import BaseModel, Base

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from os import getenv


class Agency(BaseModel, Base):
    """ The agency class, contains agency ID and name """
    if storage_type == "db":
        __tablename__ = 'agencies'
        name = Column(String(128), nullable=False)
        agency_url = Column(String(256), nullable=False)
        # Relationships
        terminals = relationship("Terminal", back_populates="agency")

    else:
        name = ""
        agency_url = ""
        terminals = []
