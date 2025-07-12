from backend.models import storage_type

from backend import models
from backend.models.base_model import BaseModel, Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.models.route import Route
from backend.models.association import routed_vehicles 

class Vehicle(BaseModel, Base):
    """ The vehicle class, contains vehicle ID and name """
    if storage_type == "db":
        __tablename__ = 'vehicles'
        name = Column(String(128), nullable=False)
        vehicle_number = Column(String(128), nullable=False)
        latitude = Column(Float, nullable=True)
        longitude = Column(Float, nullable=True)
        capacity = Column(Integer, nullable=False)
        assigned = Column(Boolean, default=False, nullable=False)
        # Relationship to Route
        routes = relationship("Route", secondary=routed_vehicles, back_populates="vehicles")

    else:
        name = ""
        vehicle_number = ""
        latitude = 0.0
        longitude = 0.0
        capacity = 0
        assigned = False
        routes = []

        @property
        def routes(self):
            """Get the list of routes for the vehicle"""
            route_lists = []
            for route in models.storage.all(Route).values():
                if self.id in [vehicle.id for vehicle in route.vehicles]:
                    route_lists.append(route)
            return route_lists