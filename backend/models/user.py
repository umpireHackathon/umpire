#!/usr/bin/python3
""" User Module for Umpire project """
import os
from dotenv import load_dotenv
from backend import models
from backend.models.base_model import BaseModel, Base
from sqlalchemy import Column, String, Boolean

load_dotenv()

STORAGE_TYPE = os.getenv("UMPIRE_TYPE_STORAGE", "file")

class User(BaseModel, Base):
    """ The user class, contains user ID and name """
    if STORAGE_TYPE == "db":
        __tablename__ = 'users'
        email = Column(String(128), nullable=False)
        password = Column(String(128), nullable=False)
        first_name = Column(String(128), nullable=False)
        last_name = Column(String(128), nullable=False)
        is_active = Column(Boolean, default=True, nullable=False)
    else:
        email = ""
        password = ""
        first_name = ""
        last_name = ""
        is_active = True