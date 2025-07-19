"""
Data models for the Accra Bus Route Optimization Problem.

This module defines the data structures used to represent the optimization problem
parameters and results.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Any
import json
import uuid


@dataclass
class RouteOR:
    """Represents a bus route with all its characteristics."""
    route_id: str
    origin_terminal: str
    stops: List[str]
    distance_km: float
    time_min: float
    fare_ghs: float
    demand_per_day: int


@dataclass
class TerminalOR:
    """Represents a bus terminal with capacity constraints."""
    terminal_id: str
    max_buses: int


@dataclass
class VehicleType:
    """Represents a type of vehicle with its allowed routes."""
    type_name: str
    vehicle_ids: List[str]
    allowed_routes: List[str]


@dataclass
class GeneralParameters:
    """General system-wide parameters."""
    total_fleet_size: int
    max_route_length_km: float
    bus_capacity_passengers: int
    min_daily_sales_per_bus_ghs: float


@dataclass
class ProblemData:
    """Complete problem data structure."""
    id = uuid.uuid4()
    general: GeneralParameters
    terminals: List[str]
    buses: List[str]
    routes: List[RouteOR]
    terminal_capacity: List[TerminalOR]
    vehicle_types: Dict[str, VehicleType]
    created_at: str = datetime.now().isoformat()

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> 'ProblemData':
        """Create ProblemData instance from JSON dictionary."""
        # Parse general parameters
        general_data = json_data['parameters']['general']
        general = GeneralParameters(
            total_fleet_size=general_data['total_fleet_size'],
            max_route_length_km=general_data['max_route_length_km'],
            bus_capacity_passengers=general_data['bus_capacity_passengers'],
            min_daily_sales_per_bus_ghs=general_data['min_daily_sales_per_bus_ghs']
        )
        
        # Parse sets
        sets_data = json_data['parameters']['sets']
        terminals = sets_data['terminals']
        buses = sets_data['buses']
        
        # Parse routes
        routes = []
        for route_data in json_data['routes_definition']:
            route = RouteOR(
                route_id=route_data['route_id'],
                origin_terminal=route_data['origin_terminal'],
                stops=route_data['stops'],
                distance_km=route_data['distance_km'],
                time_min=route_data['time_min'],
                fare_ghs=route_data['fare_ghs'],
                demand_per_day=route_data['demand_per_day']
            )
            routes.append(route)
        
        # Parse terminal capacity
        terminal_capacity = []
        for terminal_data in json_data['terminal_capacity']:
            terminal = TerminalOR(
                terminal_id=terminal_data['terminal_id'],
                max_buses=terminal_data['max_buses']
            )
            terminal_capacity.append(terminal)
        
        # Parse vehicle types and permissions
        vehicle_types = {}
        vehicle_perms = json_data['vehicle_permissions']
        for type_name, type_data in vehicle_perms['vehicle_types'].items():
            vehicle_type = VehicleType(
                type_name=type_name,
                vehicle_ids=type_data['ids'],
                allowed_routes=vehicle_perms['route_allowances'][type_name]
            )
            vehicle_types[type_name] = vehicle_type
        
        return cls(
            general=general,
            terminals=terminals,
            buses=buses,
            routes=routes,
            terminal_capacity=terminal_capacity,
            vehicle_types=vehicle_types
        )
    
    @classmethod
    def from_json_file(cls, filepath: str) -> 'ProblemData':
        """Load problem data from JSON file."""
        with open(filepath, 'r') as f:
            json_data = json.load(f)
        return cls.from_json(json_data)
    @classmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert ProblemData instance to dictionary."""
        datetime_format = "%Y-%m-%dT%H:%M:%S.%f"
        tmp = {}
        for k, v in self.__dict__.items():
            if k == 'created_at':
                tmp[k] = v.strftime(datetime_format) if isinstance(v, datetime) else v
            if isinstance(v, list):
                tmp[k] = [item.to_dict() if hasattr(item, 'to_dict') else item for item in v]
            elif hasattr(v, 'to_dict'):
                tmp[k] = v.to_dict()
            else:
                tmp[k] = v
        return tmp



    def get_route_by_id(self, route_id: str) -> Optional[RouteOR]:
        """Get route by ID."""
        for route in self.routes:
            if route.route_id == route_id:
                return route
        return None
    
    def get_terminal_capacity(self, terminal_id: str) -> int:
        """Get capacity for a specific terminal."""
        for terminal in self.terminal_capacity:
            if terminal.terminal_id == terminal_id:
                return terminal.max_buses
        return 0
    
    def is_vehicle_allowed_on_route(self, vehicle_id: str, route_id: str) -> bool:
        """Check if a vehicle is allowed on a specific route."""
        for vehicle_type in self.vehicle_types.values():
            if vehicle_id in vehicle_type.vehicle_ids:
                return route_id in vehicle_type.allowed_routes
        return False


@dataclass
class OptimizationResult:
    """Results from the optimization."""
    objective_value: float
    selected_routes: List[str]
    vehicle_assignments: Dict[str, str]  # vehicle_id -> route_id
    total_revenue: float
    total_travel_time: float
    solver_status: str
    solve_time: float
    
    def get_buses_on_route(self, route_id: str) -> List[str]:
        """Get list of buses assigned to a specific route."""
        return [vehicle_id for vehicle_id, assigned_route in self.vehicle_assignments.items() 
                if assigned_route == route_id]
    
    def get_route_statistics(self, problem_data: ProblemData) -> Dict[str, Dict[str, Any]]:
        """Get statistics for each selected route."""
        stats = {}
        for route_id in self.selected_routes:
            route = problem_data.get_route_by_id(route_id)
            buses = self.get_buses_on_route(route_id)
            
            if route:
                stats[route_id] = {
                    'buses_assigned': len(buses),
                    'bus_ids': buses,
                    'distance_km': route.distance_km,
                    'time_min': route.time_min,
                    'fare_ghs': route.fare_ghs,
                    'demand_per_day': route.demand_per_day,
                    'daily_revenue': route.demand_per_day * route.fare_ghs,
                    'daily_travel_time': route.demand_per_day * route.time_min
                }
            return stats
