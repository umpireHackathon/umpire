"""
PuLP implementation of the bus route optimization problem.
"""

from typing import Dict, Any, List
from pulp import LpProblem, LpMaximize, LpVariable, LpBinary, lpSum, LpStatus
import time

from .data_models import ProblemData, OptimizationResult
from .solver_interface import SolverInterface, SolverFactory


class PuLPSolver(SolverInterface):
    """
    PuLP implementation for the bus route optimization problem.
    """
    
    def __init__(self, problem_data: ProblemData, weights: Dict[str, float]):
        super().__init__(problem_data, weights)
        self.model = LpProblem(self.get_solver_name(), LpMaximize)
        self.variables = {}

    def get_solver_name(self) -> str:
        return "pulp"

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
        self.variables["x"] = LpVariable.dicts(
            "x", [route.route_id for route in data.routes], 0, 1, LpBinary
        )

        # y_vk: 1 if bus v is assigned to route k, 0 otherwise
        self.variables["y"] = LpVariable.dicts(
            "y",
            [(v_id, r.route_id) for v_id in data.buses for r in data.routes],
            0, 1, LpBinary
        )

    def _create_objective(self) -> None:
        data = self.problem_data
        x = self.variables["x"]

        # Maximize Z = (w_revenue * Z_revenue) - (w_time * Z_time)
        # Z_revenue = sum(D_k * x_k * R_fare_k)
        # Z_time = sum(D_k * x_k * t_k)

        total_revenue = lpSum(
            route.demand_per_day * x[route.route_id] * route.fare_ghs
            for route in data.routes
        )
        total_travel_time = lpSum(
            route.demand_per_day * x[route.route_id] * route.time_min
            for route in data.routes
        )

        objective = (
            self.weights["revenue"] * total_revenue
            - self.weights["time"] * total_travel_time
        )
        self.model += objective, "Total_Objective"

    def _create_constraints(self) -> None:
        data = self.problem_data
        x = self.variables["x"]
        y = self.variables["y"]

        # 1. Fleet Size:
        self.model += (
            lpSum(y[v_id, r.route_id] for v_id in data.buses for r in data.routes)
            <= data.general.total_fleet_size,
            "Fleet_Size"
        )

        # 2. Route Distance Limits:
        for route in data.routes:
            self.model += (
                route.distance_km * x[route.route_id] <= data.general.max_route_length_km,
                f"Route_Distance_Limit_{route.route_id}"
            )

        # 3. Vehicle Average Daily Sales:
        for route in data.routes:
            # Only apply if route is selected (x[route.route_id] == 1)
            # If x[route.route_id] == 0, then LHS is 0, RHS is 0, so 0 >= 0
            # This implicitly handles the constraint only for selected routes.
            self.model += (
                route.demand_per_day * x[route.route_id] * route.fare_ghs
                >= lpSum(y[v_id, route.route_id] for v_id in data.buses)
                * data.general.min_daily_sales_per_bus_ghs,
                f"Vehicle_Daily_Sales_{route.route_id}"
            )

        # 4. Terminal Capacity:
        for terminal_obj in data.terminal_capacity:
            terminal_id = terminal_obj.terminal_id
            capacity = terminal_obj.max_buses
            
            # Sum of buses assigned to routes originating from this terminal
            self.model += (
                lpSum(
                    y[v_id, route.route_id]
                    for v_id in data.buses
                    for route in data.routes
                    if route.origin_terminal == terminal_id
                ) <= capacity,
                f"Terminal_Capacity_{terminal_id}"
            )

        # 5. Allowed Route Assignment:
        for v_id in data.buses:
            for route in data.routes:
                is_allowed = data.is_vehicle_allowed_on_route(v_id, route.route_id)
                self.model += (
                    y[v_id, route.route_id] <= (1 if is_allowed else 0),
                    f"Allowed_Route_Assignment_{v_id}_{route.route_id}"
                )

        # 6. Bus Assignment to Active Routes:
        for v_id in data.buses:
            for route in data.routes:
                self.model += (
                    y[v_id, route.route_id] <= x[route.route_id],
                    f"Bus_Assignment_Active_Route_{v_id}_{route.route_id}"
                )

        # 7. Single Assignment per Bus:
        for v_id in data.buses:
            self.model += (
                lpSum(y[v_id, r.route_id] for r in data.routes) <= 1,
                f"Single_Assignment_Per_Bus_{v_id}"
            )

        # 8. Passenger Capacity on Route:
        for route in data.routes:
            self.model += (
                route.demand_per_day * x[route.route_id]
                <= lpSum(y[v_id, route.route_id] for v_id in data.buses)
                * data.general.bus_capacity_passengers,
                f"Passenger_Capacity_{route.route_id}"
            )

    def solve(self, **solver_params) -> OptimizationResult:
        if not self.is_built:
            self.build_model()

        start_time = time.time()
        # PuLP's solve method can take various solver options
        # For example, solver=pulp.GUROBI(msg=0) or solver=pulp.CPLEX(msg=0)
        # By default, it uses CBC, which is usually installed with PuLP.
        self.model.solve(**solver_params)
        end_time = time.time()

        solve_time = end_time - start_time
        solver_status = LpStatus[self.model.status]

        selected_routes = [
            r.route_id for r in self.problem_data.routes
            if self.variables["x"][r.route_id].varValue > 0.5
        ]

        vehicle_assignments = {}
        for v_id in self.problem_data.buses:
            for r in self.problem_data.routes:
                if self.variables["y"][v_id, r.route_id].varValue > 0.5:
                    vehicle_assignments[v_id] = r.route_id

        # Calculate actual total revenue and travel time from selected routes and demand
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

        return OptimizationResult(
            objective_value=self.model.objective.value(),
            selected_routes=selected_routes,
            vehicle_assignments=vehicle_assignments,
            total_revenue=total_revenue,
            total_travel_time=total_travel_time,
            solver_status=solver_status,
            solve_time=solve_time
        )

# Register the PuLPSolver with the SolverFactory
SolverFactory.register_solver("pulp", PuLPSolver)


