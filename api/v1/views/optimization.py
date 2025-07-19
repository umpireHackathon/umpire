#!/usr/bin/python3
"""
Main script to run the Accra Bus Route Optimization.
"""

import datetime
import os
from dotenv import load_dotenv
from flask import jsonify
from api.v1.views import app_views
from api.v1.views.bus_optimization import solve_bus_optimization, get_available_solvers, check_solver_availability
from backend.models.data_models import ProblemData

load_dotenv()

def main():
    """ Main function to run the route optimization.
    This function loads the problem data, checks solver availability
    and runs the optimization using available solvers.
    """
    
    from dotenv import load_dotenv
    load_dotenv()

    check_solver_availability()

    base_path = os.path.dirname(os.path.abspath(__file__))
    # move 3 step up folder
    base_path = os.path.abspath(os.path.join(base_path, os.pardir, os.pardir, os.pardir))
    OPTIMIZATION_DATA_URL = os.getenv('OPTIMIZATION_DATA_URL')

    SAMPLE_JSON_DATA = os.path.join(base_path, OPTIMIZATION_DATA_URL)

    # Load problem data from the sample JSON
    try:
        problem_data = ProblemData.from_json_file(SAMPLE_JSON_DATA)
        print("\nProblem data loaded successfully.")
    except Exception as e:
        print("\nProblem data loaded successfully.")
        print(f"Error loading problem optimization sample data: {e}")
        return {"error": str(e)}

    # Define objective weights (e.g., prioritize revenue more than time)
    # Adjust these weights to reflect business priorities
    weights = {"revenue": 1.0, "time": 0.01} # Example: 1 GHS revenue is 100x more important than 1 min travel time

    available_solvers = get_available_solvers()

    if not available_solvers:
        print("\nNo optimization solvers found. Please install PuLP, OR-Tools, or Gurobi.")
        return {"error": "No optimization solvers found."}

    solutions = {}
    for solver_name in available_solvers:
        print(f"\n--- Solving with {solver_name.upper()} --- ")

        sol = {}
        try:
            result = solve_bus_optimization(
                problem_data=problem_data,
                solver_name=solver_name,
                weights=weights,
                # Add solver-specific parameters here if needed
                # For Gurobi: TimeLimit=60, MIPGap=0.01
                # For OR-Tools: time_limit=60
            )

            print(f"Solver Status: {result.solver_status}")
            print(f"Solve Time: {result.solve_time:.4f} seconds")
            print(f"Objective Value: {result.objective_value:.2f}")
            print(f"Total Revenue: {result.total_revenue:.2f} GHS")
            print(f"Total Travel Time (Demand-Weighted): {result.total_travel_time:.2f} minutes")

            if result.selected_routes:
                print("\nSelected Routes:")
                for route_id in result.selected_routes:
                    route_info = problem_data.get_route_by_id(route_id)
                    buses_on_route = result.get_buses_on_route(route_id)
                    print(f"  - {route_id}: {len(buses_on_route)} buses assigned ({', '.join(buses_on_route)}) ")
                    if route_info:
                        print(f"    (Distance: {route_info.distance_km}km, Time: {route_info.time_min}min, Fare: {route_info.fare_ghs}GHS, Demand: {route_info.demand_per_day})")
                sol["selected_routes"] = result.selected_routes
                sol["vehicle_assignments"] = result.vehicle_assignments

                print("\nVehicle Assignments (Vehicle -> Route):")
                for vehicle_id, assigned_route in result.vehicle_assignments.items():
                    print(f"  {vehicle_id} -> {assigned_route}")
                    sol["vehicle_assignments"][vehicle_id] = assigned_route

            else:
                print("\nNo routes selected or no feasible solution found.")
            sol["solver_status"] = result.solver_status
            sol["solve_time"] = result.solve_time
            sol["objective_value"] = result.objective_value
            sol["total_revenue"] = result.total_revenue
            sol["total_travel_time"] = result.total_travel_time
            solutions[solver_name] = {"data": sol, "status": "success"}

        except Exception as e:
            print(f"Error solving with {solver_name}: {e}")
            solutions[solver_name] = {"error": str(e), "status": "failed", "data": {}}
        finally:
            solutions["Info"] = {
                "problem_data": problem_data.id,
                "weights": weights,
                "available_solvers": available_solvers,
                "date": datetime.datetime.now().isoformat(),
            }

    return solutions


@app_views.route('/optimize_sample', methods=['GET'])
def optimize_routes():
    solutions = main()
    return jsonify(solutions)

if __name__ == "__main__":
    main()


