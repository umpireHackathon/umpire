"""
Abstract solver interface for the bus route optimization problem.

This module defines the interface that all solver implementations must follow,
enabling dynamic solver selection at runtime.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from .data_models import ProblemData, OptimizationResult


class SolverInterface(ABC):
    """Abstract base class for optimization solvers."""
    
    def __init__(self, problem_data: ProblemData, weights: Optional[Dict[str, float]] = None):
        """
        Initialize the solver with problem data.
        
        Args:
            problem_data: The complete problem data
            weights: Objective function weights {'revenue': w_revenue, 'time': w_time}
        """
        self.problem_data = problem_data
        self.weights = weights or {'revenue': 1.0, 'time': 0.1}
        self.model = None
        self.variables = {}
        self.is_built = False
    
    @abstractmethod
    def build_model(self) -> None:
        """Build the optimization model with variables, objective, and constraints."""
        pass
    
    @abstractmethod
    def solve(self, **solver_params) -> OptimizationResult:
        """
        Solve the optimization problem.
        
        Args:
            **solver_params: Solver-specific parameters
            
        Returns:
            OptimizationResult containing the solution
        """
        pass
    
    @abstractmethod
    def get_solver_name(self) -> str:
        """Return the name of the solver."""
        pass
    
    def set_weights(self, revenue_weight: float, time_weight: float) -> None:
        """Update objective function weights."""
        self.weights = {'revenue': revenue_weight, 'time': time_weight}
        if self.is_built:
            # If model is already built, need to rebuild with new weights
            self.is_built = False
    
    def _create_variables(self) -> None:
        """Create decision variables. To be implemented by subclasses."""
        pass
    
    def _create_objective(self) -> None:
        """Create objective function. To be implemented by subclasses."""
        pass
    
    def _create_constraints(self) -> None:
        """Create constraints. To be implemented by subclasses."""
        pass
    
    def _extract_solution(self) -> OptimizationResult:
        """Extract solution from solved model. To be implemented by subclasses."""
        pass


class SolverFactory:
    """Factory class for creating solver instances."""
    
    _solvers = {}
    
    @classmethod
    def register_solver(cls, name: str, solver_class: type) -> None:
        """Register a solver class."""
        cls._solvers[name] = solver_class
    
    @classmethod
    def create_solver(cls, name: str, problem_data: ProblemData, 
                     weights: Optional[Dict[str, float]] = None) -> SolverInterface:
        """
        Create a solver instance.
        
        Args:
            name: Name of the solver ('pulp', 'ortools', 'gurobi')
            problem_data: Problem data
            weights: Objective function weights
            
        Returns:
            Solver instance
        """
        if name not in cls._solvers:
            raise ValueError(f"Unknown solver: {name}. Available solvers: {list(cls._solvers.keys())}")
        
        return cls._solvers[name](problem_data, weights)
    
    @classmethod
    def available_solvers(cls) -> list:
        """Return list of available solver names."""
        return list(cls._solvers.keys())


def solve_bus_optimization(problem_data: ProblemData, 
                          solver_name: str = 'pulp',
                          weights: Optional[Dict[str, float]] = None,
                          **solver_params) -> OptimizationResult:
    """
    Convenience function to solve the bus optimization problem.
    
    Args:
        problem_data: Problem data
        solver_name: Name of solver to use
        weights: Objective function weights
        **solver_params: Additional solver parameters
        
    Returns:
        OptimizationResult
    """
    solver = SolverFactory.create_solver(solver_name, problem_data, weights)
    solver.build_model()
    return solver.solve(**solver_params)

