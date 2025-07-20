# backend/models/association.py
""" Association module for HBNB project """

import os
from dotenv import load_dotenv 
from backend import models
from sqlalchemy import Column, Integer, ForeignKey, Table

load_dotenv()

STORAGE_TYPE = os.getenv("UMPIRE_TYPE_STORAGE", "file")

if STORAGE_TYPE == "db":
    from backend.models.base_model import Base

    routed_vehicles = Table(
        'routed_vehicles', Base.metadata,
        Column('route_id', Integer, ForeignKey('routes.id'), primary_key=True),
        Column('vehicle_id', Integer, ForeignKey('vehicles.id'), primary_key=True)
    )
    route_terminals = Table(
        'route_terminals', Base.metadata,
        Column('route_id', Integer, ForeignKey('routes.id'), primary_key=True),
        Column('terminal_id', Integer, ForeignKey('terminals.id'), primary_key=True)
    )

    agency_terminals = Table(
        'agency_terminals', Base.metadata,
        Column('agency_id', Integer, ForeignKey('agencies.id'), primary_key=True),
        Column('terminal_id', Integer, ForeignKey('terminals.id'), primary_key=True)
    )

    route_agencies = Table(
        'route_agencies', Base.metadata,
        Column('route_id', Integer, ForeignKey('routes.id'), primary_key=True),
        Column('agency_id', Integer, ForeignKey('agencies.id'), primary_key=True)

    )

    route_stops = Table(
        'route_stops', Base.metadata,
        Column('route_id', Integer, ForeignKey('routes.id'), primary_key=True),
        Column('bus_stop_id', Integer, ForeignKey('bus_stops.id'), primary_key=True)
    )
    

else:
    routed_vehicles = None
    route_terminals = None
    agency_terminals = None
    route_agencies = None
    route_stops = None