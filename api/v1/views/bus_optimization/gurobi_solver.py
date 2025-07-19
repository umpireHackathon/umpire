"""
Gurobi implementation of the bus route optimization problem.
"""

from typing import Dict, Any
import gurobipy as gp
from gurobipy import GRB
import time

from .data_models import ProblemData, OptimizationResult
from .solver_interface import SolverInterface, SolverFactory


class GurobiSolver(SolverInterface):
    """
    Gurobi implementation for the bus route optimization problem.
    """
    
    def __init__(self, problem_data: ProblemData, weights: Dict[str, float]):
        super().__init__(problem_data, weights)
        self.env = gp.Env(empty=True)
        self.env.setParam("OutputFlag", 0) # Suppress Gurobi output
        self.env.start()
        self.model = gp.Model(self.get_solver_name(), env=self.env)
        self.variables = {}

    def get_solver_name(self) -> str:
        return "gurobi"

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
        self.variables["x"] = self.model.addVars(
            [route.route_id for route in data.routes], vtype=GRB.BINARY, name="x"
        )

        # y_vk: 1 if bus v is assigned to route k, 0 otherwise
        self.variables["y"] = self.model.addVars(
            [(v_id, r.route_id) for v_id in data.buses for r in data.routes],
            vtype=GRB.BINARY, name="y"
        )

    def _create_objective(self) -> None:
        data = self.problem_data
        x = self.variables["x"]

        # Maximize Z = (w_revenue * Z_revenue) - (w_time * Z_time)
        total_revenue = gp.quicksum(
            route.demand_per_day * x[route.route_id] * route.fare_ghs
            for route in data.routes
        )
        total_travel_time = gp.quicksum(
            route.demand_per_day * x[route.route_id] * route.time_min
            for route in data.routes
        )

        objective = (
            self.weights["revenue"] * total_revenue
            - self.weights["time"] * total_travel_time
        )
        self.model.setObjective(objective, GRB.MAXIMIZE)

    def _create_constraints(self) -> None:
        data = self.problem_data
        x = self.variables["x"]
        y = self.variables["y"]

        # 1. Fleet Size:
        self.model.addConstr(
            gp.quicksum(y[v_id, r.route_id] for v_id in data.buses for r in data.routes)
            <= data.general.total_fleet_size,
            "Fleet_Size"
        )

        # 2. Route Distance Limits:
        for route in data.routes:
            self.model.addConstr(
                route.distance_km * x[route.route_id] <= data.general.max_route_length_km,
                f"Route_Distance_Limit_{route.route_id}"
            )

        # 3. Vehicle Average Daily Sales:
        for route in data.routes:
            self.model.addConstr(
                route.demand_per_day * x[route.route_id] * route.fare_ghs
                >= gp.quicksum(y[v_id, route.route_id] for v_id in data.buses)
                * data.general.min_daily_sales_per_bus_ghs,
                f"Vehicle_Daily_Sales_{route.route_id}"
            )

        # 4. Terminal Capacity:
        for terminal_obj in data.terminal_capacity:
            terminal_id = terminal_obj.terminal_id
            capacity = terminal_obj.max_buses
            
            self.model.addConstr(
                gp.quicksum(
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
                self.model.addConstr(
                    y[v_id, route.route_id] <= (1 if is_allowed else 0),
                    f"Allowed_Route_Assignment_{v_id}_{route.route_id}"
                )

        # 6. Bus Assignment to Active Routes:
        for v_id in data.buses:
            for route in data.routes:
                self.model.addConstr(
                    y[v_id, route.route_id] <= x[route.route_id],
                    f"Bus_Assignment_Active_Route_{v_id}_{route.route_id}"
                )

        # 7. Single Assignment per Bus:
        for v_id in data.buses:
            self.model.addConstr(
                gp.quicksum(y[v_id, r.route_id] for r in data.routes) <= 1,
                f"Single_Assignment_Per_Bus_{v_id}"
            )

        # 8. Passenger Capacity on Route:
        for route in data.routes:
            self.model.addConstr(
                route.demand_per_day * x[route.route_id]
                <= gp.quicksum(y[v_id, route.route_id] for v_id in data.buses)
                * data.general.bus_capacity_passengers,
                f"Passenger_Capacity_{route.route_id}"
            )

    def solve(self, **solver_params) -> OptimizationResult:
        if not self.is_built:
            self.build_model()

        # Set Gurobi parameters
        for param, value in solver_params.items():
            try:
                self.model.setParam(param, value)
            except gp.GurobiError as e:
                print(f"Warning: Could not set Gurobi parameter {param}: {e}")

        start_time = time.time()
        self.model.optimize()
        end_time = time.time()

        solve_time = end_time - start_time
        
        solver_status = "Unknown"
        if self.model.status == GRB.OPTIMAL:
            solver_status = "Optimal"
        elif self.model.status == GRB.INFEASIBLE:
            solver_status = "Infeasible"
        elif self.model.status == GRB.UNBOUNDED:
            solver_status = "Unbounded"
        elif self.model.status == GRB.TIME_LIMIT:
            solver_status = "Time Limit"
        elif self.model.status == GRB.INTERRUPTED:
            solver_status = "Interrupted"
        elif self.model.status == GRB.SOLUTION_LIMIT:
            solver_status = "Solution Limit"
        elif self.model.status == GRB.NODE_LIMIT:
            solver_status = "Node Limit"
        elif self.model.status == GRB.ITERATION_LIMIT:
            solver_status = "Iteration Limit"
        elif self.model.status == GRB.NUMERIC:
            solver_status = "Numeric"
        elif self.model.status == GRB.SUBOPTIMAL:
            solver_status = "Suboptimal"
        elif self.model.status == GRB.USER_OBJ_LIMIT:
            solver_status = "User Objective Limit"
        elif self.model.status == GRB.LOADED:
            solver_status = "Loaded"
        elif self.model.status == GRB.NOT_STARTED:
            solver_status = "Not Started"
        elif self.model.status == GRB.NO_SOLUTION_FOUND:
            solver_status = "No Solution Found"

        if self.model.status == GRB.OPTIMAL or self.model.status == GRB.SUBOPTIMAL:
            selected_routes = [
                r.route_id for r in self.problem_data.routes
                if self.variables["x"][r.route_id].X > 0.5
            ]

            vehicle_assignments = {}
            for v_id in self.problem_data.buses:
                for r in self.problem_data.routes:
                    if self.variables["y"][v_id, r.route_id].X > 0.5:
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

            objective_value = self.model.ObjVal
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

# Register the GurobiSolver with the SolverFactory
SolverFactory.register_solver("gurobi", GurobiSolver)


