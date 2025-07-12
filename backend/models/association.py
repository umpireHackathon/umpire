from sqlalchemy import Column, Integer, ForeignKey, Table
from backend.models.base_model import Base

from os import getenv


route_optimization = Table(
    'optimized_routes', Base.metadata,
    Column('route_id', Integer, ForeignKey('routes.id'), primary_key=True),
    Column('optimized_route_id', Integer, ForeignKey('optimized_routes.id'), primary_key=True)
)

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
