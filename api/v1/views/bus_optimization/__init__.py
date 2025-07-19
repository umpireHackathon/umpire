"""
Accra Bus Route Optimization Package

A production-ready Python implementation for optimizing bus routes in Accra,
supporting multiple solvers (PuLP, Google OR-Tools, Gurobi).
"""

from .data_models import ProblemData, OptimizationResult, Route, Terminal, VehicleType, GeneralParameters
from .solver_interface import SolverInterface, SolverFactory, solve_bus_optimization

# Import solver implementations to register them
try:
    from .pulp_solver import PuLPSolver
    _PULP_AVAILABLE = True
except ImportError:
    _PULP_AVAILABLE = False

try:
    from .ortools_solver import ORToolsSolver
    _ORTOOLS_AVAILABLE = True
except ImportError:
    _ORTOOLS_AVAILABLE = False

try:
    from .gurobi_solver import GurobiSolver
    _GUROBI_AVAILABLE = True
except ImportError:
    _GUROBI_AVAILABLE = False

__version__ = "1.0.0"
__author__ = "Bus Optimization Team"

def get_available_solvers():
    """Return a list of available solvers based on installed packages."""
    available = []
    if _PULP_AVAILABLE:
        available.append("pulp")
    if _ORTOOLS_AVAILABLE:
        available.append("ortools")
    if _GUROBI_AVAILABLE:
        available.append("gurobi")
    return available

def check_solver_availability():
    """Print information about solver availability."""
    print("Solver Availability:")
    print(f"  PuLP: {'✓' if _PULP_AVAILABLE else '✗'}")
    print(f"  OR-Tools: {'✓' if _ORTOOLS_AVAILABLE else '✗'}")
    print(f"  Gurobi: {'✓' if _GUROBI_AVAILABLE else '✗'}")
    print(f"\nAvailable solvers: {get_available_solvers()}")

__all__ = [
    'ProblemData',
    'OptimizationResult', 
    'Route',
    'Terminal',
    'VehicleType',
    'GeneralParameters',
    'SolverInterface',
    'SolverFactory',
    'solve_bus_optimization',
    'get_available_solvers',
    'check_solver_availability'
]

