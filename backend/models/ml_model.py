from os import getenv

from backend import models
from backend.models.base_model import BaseModel, Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from backend.models.route_optimization import RouteOptimization


class DemandPrediction(BaseModel, Base):
    """ The DemandPrediction class, contains model ID and name """
    if getenv("UMPIRE_TYPE_STORAGE") == "db":
        __tablename__ = 'demand_predictions'
        name = Column(String, nullable=False)
        version = Column(String, nullable=False)
        task = Column(String, nullable=False)
        url = Column(String, nullable=False)
        inference_endpoint = Column(String, nullable=True)
        description = Column(String, nullable=True)
        target = Column(String, nullable=True) # Target variable for the model
        features = Column(String, nullable=True) # Comma-separated list of feature names
        
        # Relationship route allocation
        optimized_routes = relationship("OptimizedRoute", back_populates="demand_prediction")
    else:
        name = ""
        version = ""
        task = ""
        url = ""
        inference_endpoint = ""
        description = ""
        target = ""
        features = ""
        optimized_routes = []

        @property
        def optimized_routes(self):
            """Get the list of optimized routes for the model"""
            return models.storage.all(RouteOptimization).values()

        @optimized_routes.setter
        def optimized_routes(self, value):
            """Setter for optimized_routes"""

            if not isinstance(value, RouteOptimization):
                raise TypeError("Expected an OptimizedRoute instance")

            if value not in self.optimized_routes:
                self.optimized_routes.append(value)


class TravelTimePrediction(BaseModel, Base):
    """ The TravelTimePrediction class, contains model ID and name """
    if getenv("UMPIRE_TYPE_STORAGE") == "db":
        __tablename__ = 'travel_time_predictions'
        name = Column(String, nullable=False)
        version = Column(String, nullable=False)
        task = Column(String, nullable=False)
        url = Column(String, nullable=False)
        inference_endpoint = Column(String, nullable=True)
        description = Column(String, nullable=True)
        
        # Relationship route allocation
        optimized_routes = relationship("OptimizedRoute", back_populates="travel_time_prediction")
    else:
        name = ""
        version = ""
        task = ""
        url = ""
        inference_endpoint = ""
        description = ""
        optimized_routes = []

        @property
        def optimized_routes(self):
            """Get the list of optimized routes for the model"""
            return models.storage.all(RouteOptimization).values()

        @optimized_routes.setter
        def optimized_routes(self, value):
            """Setter for optimized_routes"""

            if not isinstance(value, RouteOptimization):
                raise TypeError("Expected an OptimizedRoute instance")

            if value not in self.optimized_routes:
                self.optimized_routes.append(value)


class StopsPrediction(BaseModel, Base):
    """ The StopsPrediction class, contains model ID and name """
    if getenv("UMPIRE_TYPE_STORAGE") == "db":
        __tablename__ = 'stops_predictions'
        name = Column(String, nullable=False)
        version = Column(String, nullable=False)
        task = Column(String, nullable=False)
        url = Column(String, nullable=False)
        inference_endpoint = Column(String, nullable=True)
        description = Column(String, nullable=True)
        
        # Relationship route allocation
        optimized_routes = relationship("OptimizedRoute", back_populates="ml_model")
    else:
        name = ""
        version = ""
        task = ""
        url = ""
        inference_endpoint = ""
        description = ""
        optimized_routes = []

        @property
        def optimized_routes(self):
            """Get the list of optimized routes for the model"""
            return models.storage.all(RouteOptimization).values()

        @optimized_routes.setter
        def optimized_routes(self, value):
            """Setter for optimized_routes"""

            if not isinstance(value, RouteOptimization):
                raise TypeError("Expected an OptimizedRoute instance")

            if value not in self.optimized_routes:
                self.optimized_routes.append(value)