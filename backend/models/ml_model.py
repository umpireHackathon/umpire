from os import getenv

from backend import models
from backend.models import storage_type
from backend.models.base_model import BaseModel, Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship


class DemandPrediction(BaseModel, Base):
    """ The DemandPrediction class, contains model ID and name """
    if storage_type == "db":
        __tablename__ = 'demand_predictions'
        name = Column(String, nullable=False)
        version = Column(String, nullable=False)
        task = Column(String, nullable=False)
        url = Column(String, nullable=False)
        inference_endpoint = Column(String, nullable=True)
        description = Column(String, nullable=True)
        target = Column(String, nullable=True) # Target variable for the model
        features = Column(String, nullable=True) # Comma-separated list of feature names
    else:
        name = ""
        version = ""
        task = ""
        url = ""
        inference_endpoint = ""
        description = ""
        target = ""
        features = ""

class TravelTimePrediction(BaseModel, Base):
    """ The TravelTimePrediction class, contains model ID and name """
    if storage_type == "db":
        __tablename__ = 'travel_time_predictions'
        name = Column(String, nullable=False)
        version = Column(String, nullable=False)
        task = Column(String, nullable=False)
        url = Column(String, nullable=False)
        inference_endpoint = Column(String, nullable=True)
        description = Column(String, nullable=True)
    else:
        name = ""
        version = ""
        task = ""
        url = ""
        inference_endpoint = ""
        description = ""


class StopsPrediction(BaseModel, Base):
    """ The StopsPrediction class, contains model ID and name """
    if storage_type == "db":
        __tablename__ = 'stops_predictions'
        name = Column(String, nullable=False)
        version = Column(String, nullable=False)
        task = Column(String, nullable=False)
        url = Column(String, nullable=False)
        inference_endpoint = Column(String, nullable=True)
        description = Column(String, nullable=True)
    else:
        name = ""
        version = ""
        task = ""
        url = ""
        inference_endpoint = ""
        description = ""