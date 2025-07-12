
from backend.models import storage_type
from backend import models
from backend.models.base_model import BaseModel, Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from backend.models.route import Route

if storage_type == "db":
    from backend.models.association import route_terminals, agency_terminals

class Terminal(BaseModel, Base):
    """ The terminal class, contains terminal ID and name """
    if storage_type == "db":
        __tablename__ = 'terminals'
        name = Column(String(128), nullable=False)
        latitude = Column(Float, nullable=False)
        longitude = Column(Float, nullable=False)
        suburb_id = Column(Integer, ForeignKey('suburbs.id'), nullable=False)

        # Relationship to Suburb
        suburb = relationship("Suburb", back_populates="terminals")
        # Relationship to Route
        routes = relationship("Route", secondary=route_terminals, back_populates="terminals")
        # Relationship to Agency
        agencies = relationship("Agency", secondary=agency_terminals, back_populates="terminals")

    else:
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
