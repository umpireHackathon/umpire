from os import getenv

from backend import models
from backend.models.base_model import BaseModel, Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from backend.models.bus_stop import BusStop
from backend.models.ml_model import DemandPrediction
from backend.models.ml_model import TravelTimePrediction
from backend.models.ml_model import StopsPrediction

if getenv("UMPIRE_TYPE_STORAGE") == "db":
    from backend.models.association import route_optimization


class Optimization(BaseModel, Base):
    """ The Optimization class, contains route ID and name """
    if getenv("UMPIRE_TYPE_STORAGE") == "db":
        __tablename__ = 'optimized_routes'
        travel_time = Column(Float, nullable=False)
        revenue = Column(Float, nullable=False)
        # Foreign keys
        demand_prediction_id = Column(Integer, ForeignKey('demand_predictions.id'), nullable=False)
        stops_prediction_id = Column(Integer, ForeignKey('stops_predictions.id'), nullable=False)
        travel_time_prediction_id = Column(Integer, ForeignKey('travel_time_predictions.id'), nullable=False)
        # Relationships
        demand_prediction = relationship("DemandPrediction", back_populates="optimized_routes")
        stops_prediction = relationship("StopsPrediction", back_populates="optimized_routes")
        routes = relationship("Route", secondary=route_optimization, back_populates="optimizations")