# !/usr/bin/python3
""" MLModel Module for HBNB project """

import os
from dotenv import load_dotenv
from backend.models.base_model import BaseModel, Base
from sqlalchemy import Column, String

load_dotenv()

STORAGE_TYPE = os.getenv("UMPIRE_TYPE_STORAGE", "file")


class MLModel(BaseModel, Base):
    """ The MLModel class, contains model ID and name """
    if STORAGE_TYPE == "db":
        __tablename__ = 'ml_model'
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
        created_at = ""
        updated_at = ""