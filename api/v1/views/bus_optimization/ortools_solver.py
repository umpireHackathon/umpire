"""
Google OR-Tools implementation of the bus route optimization problem.
"""

from typing import Dict, Any
from ortools.linear_solver import pywraplp
import time

from .data_models import ProblemData, OptimizationResult
from .solver_interface import SolverInterface, SolverFactory


class ORToolsSolver(SolverInterface):
    """
    Google OR-Tools implementation for the bus route optimization problem.
    """
    
    def __init__(self, problem_data: ProblemData, weights: Dict[str, float]):
        super().__init__(problem_data, weights)
        # Use SCIP as the default solver (CBC is also available)
        self.model = pywraplp.Solver.CreateSolver('SCIP')
        if not self.model:
            raise RuntimeError("SCIP solver not available")
        self.variables = {}

    def get_solver_name(self) -> str:
        return "ortools"

    def build_model(self) -> None:
        if self.is_built:
            return

        self._create_variables()
        self._create_objective()
        self._create_constraints()
        self.is_built = True

    def _create_variables(self) -> None:
        data = self.problem_data

        # x_k: 1 if route k is selected, 0 otherwise
        self.variables["x"] = {}
        for route in data.routes:
            self.variables["x"][route.route_id] = self.model.BoolVar(f"x_{route.route_id}")

        # y_vk: 1 if bus v is assigned to route k, 0 otherwise
        self.variables["y"] = {}
        for v_id in data.buses:
            for route in data.routes:
                self.variables["y"][(v_id, route.route_id)] = self.model.BoolVar(
                    f"y_{v_id}_{route.route_id}"
                )

    def _create_objective(self) -> None:
        data = self.problem_data
        x = self.variables["x"]

        # Maximize Z = (w_revenue * Z_revenue) - (w_time * Z_time)
        total_revenue = sum(
            route.demand_per_day * x[route.route_id] * route.fare_ghs
            for route in data.routes
        )
        total_travel_time = sum(
            route.demand_per_day * x[route.route_id] * route.time_min
            for route in data.routes
        )

        objective = (
            self.weights["revenue"] * total_revenue
            - self.weights["time"] * total_travel_time
        )
        self.model.Maximize(objective)

    def _create_constraints(self) -> None:
        data = self.problem_data
        x = self.variables["x"]
        y = self.variables["y"]

        # 1. Fleet Size:
        self.model.Add(
            sum(y[(v_id, r.route_id)] for v_id in data.buses for r in data.routes)
            <= data.general.total_fleet_size
        )

        # 2. Route Distance Limits:
        for route in data.routes:
            self.model.Add(
                route.distance_km * x[route.route_id] <= data.general.max_route_length_km
            )

        # 3. Vehicle Average Daily Sales:
        for route in data.routes:
            self.model.Add(
                route.demand_per_day * x[route.route_id] * route.fare_ghs
                >= sum(y[(v_id, route.route_id)] for v_id in data.buses)
                * data.general.min_daily_sales_per_bus_ghs
            )

        # 4. Terminal Capacity:
        for terminal_obj in data.terminal_capacity:
            terminal_id = terminal_obj.terminal_id
            capacity = terminal_obj.max_buses
            
            self.model.Add(
                sum(
                    y[(v_id, route.route_id)]
                    for v_id in data.buses
                    for route in data.routes
                    if route.origin_terminal == terminal_id
                ) <= capacity
            )

        # 5. Allowed Route Assignment:
        for v_id in data.buses:
            for route in data.routes:
                is_allowed = data.is_vehicle_allowed_on_route(v_id, route.route_id)
                if not is_allowed:
                    self.model.Add(y[(v_id, route.route_id)] == 0)

        # 6. Bus Assignment to Active Routes:
        for v_id in data.buses:
            for route in data.routes:
                self.model.Add(y[(v_id, route.route_id)] <= x[route.route_id])

        # 7. Single Assignment per Bus:
        for v_id in data.buses:
            self.model.Add(
                sum(y[(v_id, r.route_id)] for r in data.routes) <= 1
            )

        # 8. Passenger Capacity on Route:
        for route in data.routes:
            self.model.Add(
                route.demand_per_day * x[route.route_id]
                <= sum(y[(v_id, route.route_id)] for v_id in data.buses)
                * data.general.bus_capacity_passengers
            )

    def solve(self, **solver_params) -> OptimizationResult:
        if not self.is_built:
            self.build_model()

        # Set solver parameters
        if 'time_limit' in solver_params:
            self.model.SetTimeLimit(solver_params['time_limit'] * 1000)  # OR-Tools uses milliseconds

        start_time = time.time()
        status = self.model.Solve()
        end_time = time.time()

        solve_time = end_time - start_time

        # Map OR-Tools status to string
        status_map = {
            pywraplp.Solver.OPTIMAL: "Optimal",
            pywraplp.Solver.FEASIBLE: "Feasible",
            pywraplp.Solver.INFEASIBLE: "Infeasible",
            pywraplp.Solver.UNBOUNDED: "Unbounded",
            pywraplp.Solver.ABNORMAL: "Abnormal",
            pywraplp.Solver.NOT_SOLVED: "Not Solved"
        }
        solver_status = status_map.get(status, "Unknown")

        if status in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE]:
            selected_routes = [
                r.route_id for r in self.problem_data.routes
                if self.variables["x"][r.route_id].solution_value() > 0.5
            ]

            vehicle_assignments = {}
            for v_id in self.problem_data.buses:
                for r in self.problem_data.routes:
                    if self.variables["y"][(v_id, r.route_id)].solution_value() > 0.5:
                        vehicle_assignments[v_id] = r.route_id

            # Calculate actual total revenue and travel time
            total_revenue = sum(
                route.demand_per_day * route.fare_ghs
                for route in self.problem_data.routes
                if route.route_id in selected_routes
            )
            total_travel_time = sum(
                route.demand_per_day * route.time_min
                for route in self.problem_data.routes
                if route.route_id in selected_routes
            )

            objective_value = self.model.Objective().Value()
        else:
            selected_routes = []
            vehicle_assignments = {}
            total_revenue = 0
            total_travel_time = 0
            objective_value = 0

        return OptimizationResult(
            objective_value=objective_value,
            selected_routes=selected_routes,
            vehicle_assignments=vehicle_assignments,
            total_revenue=total_revenue,
            total_travel_time=total_travel_time,
            solver_status=solver_status,
            solve_time=solve_time
        )


# Register the ORToolsSolver with the SolverFactory
SolverFactory.register_solver("ortools", ORToolsSolver)

