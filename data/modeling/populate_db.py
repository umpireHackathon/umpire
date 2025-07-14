import os
from turtle import right
import numpy as np
import pandas as pd
import re
from backend.dev_flask.views import suburb
from backend.models import storage
from backend.models.suburb import Suburb
from backend.models.bus_stop import BusStop
from backend.models.route import Route
from backend.models.agency import Agency
from backend.models.ml_model import MLModel
from backend.models.terminal import Terminal
from backend.models.association import routed_vehicles, route_terminals, agency_terminals, route_agencies


# Sources files
wrkdir = os.path.dirname(os.path.abspath(__file__))  # full absolute path to current script
src_agency = os.path.abspath(os.path.join(wrkdir, "../data_src/to_db/agencies.csv"))
src_suburb = os.path.abspath(os.path.join(wrkdir, "../data_src/to_db/suburbs.csv"))
src_bus_stop = os.path.abspath(os.path.join(wrkdir, "../data_src/to_db/bus_stops.csv"))
src_route = os.path.abspath(os.path.join(wrkdir, "../data_src/to_db/routes.csv"))
src_route_stops = os.path.abspath(os.path.join(wrkdir, "../data_src/to_db/route_stops.csv"))
src_ml_model = os.path.abspath(os.path.join(wrkdir, "../data_src/to_db/ml_model.csv"))
src_terminal = os.path.abspath(os.path.join(wrkdir, "../data_src/to_db/terminals.csv"))
src_association = os.path.abspath(os.path.join(wrkdir, "../data_src/to_db/route_terminals.csv"))

# Utility function
def get_list_from_string(s):
    """Extracts all wordandnumber from a string formatted like '[wordandnumber, wordandnumber, ...]'."""
    func = lambda x: x.strip().strip("'").strip('"')
    if isinstance(s, str):
        s = func(s)
        return re.findall(r'\b\w+\d*\b', s)
    return []


def check_columns(df, required_columns):
    """Check if the DataFrame contains all required columns."""
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"DataFrame is missing required columns: {', '.join(missing_columns)}")


def load_agency():
    """Load agency data from CSV and save to database.
    Expected CSV format:
        - id, name, agency_url
    Required columns:
        - [name, agency_url]
    Expected schema for db:
        name VARCHAR(128) NOT NULL,
        agency_url VARCHAR(256) NOT NULL,
    """
    if os.path.exists(src_agency):
        df_agency = pd.read_csv(src_agency)
        # Check if required columns are present
        required_columns = ['name', 'agency_url']
        check_columns(df_agency, required_columns)

        df_agency = df_agency[required_columns]  # Keep only required columns
        df_agency = df_agency.drop_duplicates(subset=['name', 'agency_url'])

        for _, row in df_agency.iterrows():
            print("-------------------------------------------")
            print(row.to_dict())
            print("-------------------------------------------")
            agency = Agency(**row.to_dict())
            try:
                agency.save()
            except Exception as e:
                print(f"Agency {row['name']} already exists, skipping.")
                print(f"Error: {e}")
        print(f"Agencies loaded: {len(df_agency)}")
    else:
        print(f"Agency source file not found: {src_agency}")

def load_suburb():
    """Load suburb data from CSV and save to database.
    Expected CSV format:
        - name, latitude, longitude, suburb_id
    Required columns for db:
        - [name, latitude, longitude]
    Expected schema for db:
        name VARCHAR(128) NOT NULL,
        latitude DOUBLE PRECISION NOT NULL,
        longitude DOUBLE PRECISION NOT NULL,
    """
    if os.path.exists(src_suburb):
        df_suburb = pd.read_csv(src_suburb)
        # Check if required columns are present
        required_columns = ['name', 'latitude', 'longitude']
        check_columns(df_suburb, required_columns)

        df_suburb = df_suburb[required_columns]  # Keep only required columns
        df_suburb = df_suburb.drop_duplicates(subset=required_columns)

        for _, row in df_suburb.iterrows():
            suburb = Suburb(**row.to_dict())
            suburb.save()
        print(f"Suburbs loaded: {len(df_suburb)}")
    else:
        print(f"Suburb source file not found: {src_suburb}")

def load_routes():
    """
    Expected CSV format:
     - route_id,name,distance_km
    Required columns for db:
     - [name, distance_km]
    Expected schema for db:
        name VARCHAR(128) NOT NULL,
        distance_km DOUBLE PRECISION NOT NULL,
    """
    if os.path.exists(src_route):
        df_route = pd.read_csv(src_route)
        # Check if required columns are present
        required_columns = ['name', 'distance_km']
        check_columns(df_route, required_columns)

        df_route = df_route[required_columns]  # Keep only required columns
        df_route = df_route.drop_duplicates(subset=required_columns)

        for _, row in df_route.iterrows():
            route = Route(**row.to_dict())
            route.save()
        print(f"Routes loaded: {len(df_route)}")
    else:
        print(f"Route source file not found: {src_route}")

def load_terminals():
    """
    Load terminal data from CSV and save to database.
    Expected CSV format:
        - stop_id, name, latitude, longitude, suburb_id
    Required columns for db:
        - [name, latitude, longitude, suburb_id]
    Expected schema for db:
        name VARCHAR(128) NOT NULL,
        latitude DOUBLE PRECISION NOT NULL,
        longitude DOUBLE PRECISION NOT NULL,
        suburb_id VARCHAR(255) NULL REFERENCES suburbs(id) ON DELETE CASCADE,
    """
    if os.path.exists(src_terminal):
        df_terminal = pd.read_csv(src_terminal)
        # Check if required columns are present
        required_columns = ['name', 'latitude', 'longitude', 'suburb_id']
        check_columns(df_terminal, required_columns)

        df_terminal = df_terminal[required_columns]  # Keep only required columns
        df_terminal = df_terminal.drop_duplicates(subset=required_columns)
        df_suburb = pd.read_csv(src_suburb)

        for _, row in df_terminal.iterrows():
            # -----------get suburb_id-----------------
            suburb_id = row['suburb_id']
            if pd.isna(suburb_id):
                row['suburb_id'] = None
            else:
                suburb = df_suburb[df_suburb['suburb_id'] == suburb_id][['name', 'latitude', 'longitude']]
                suburb_obj = storage.get_or_create(Suburb, **suburb.iloc[0].to_dict())
                if suburb_obj:
                    row['suburb_id'] = suburb_obj.id
            # ---------------------------------------
            terminal = Terminal(**row.to_dict())
            terminal.save()
        print(f"Terminals loaded: {len(df_terminal)}")
    else:
        print(f"Terminal source file not found: {src_terminal}")


def load_bus_stops():
    """
    Load bus stop data from CSV and save to database.
    Expected CSV format:
        - [stop_id,name,latitude,longitude,suburb_id]
    Required columns for db:
        - [name, latitude, longitude]
    Expected schema for db:
        name VARCHAR(128) NOT NULL,
        latitude DOUBLE PRECISION NOT NULL,
        longitude DOUBLE PRECISION NOT NULL,
        suburb_id VARCHAR(255) NULL REFERENCES suburbs(id) ON DELETE CASCADE,
        route_id VARCHAR(255) REFERENCES routes(id) ON DELETE SET NULL,
    """
    if os.path.exists(src_bus_stop):
        df_bus_stop = pd.read_csv(src_bus_stop)
        df_route_stops = pd.read_csv(src_route_stops)
        df_route = pd.read_csv(src_route)

        # Check if required columns are present
        required_columns = ['stop_id', 'name', 'latitude', 'longitude']
        check_columns(df_bus_stop, required_columns)

        df_bus_stop = df_bus_stop[required_columns]  # Keep only required columns
        df_bus_stop = df_bus_stop.drop_duplicates(subset=required_columns)

        for _, row in df_bus_stop.iterrows():
            # -----------get route_id from df_route_stops-----------------
            pass

 

def load_route_terminals():
    """
    Load route terminals from CSV and save to database.
    Expected CSV format:
        - route_id, stop_ids
    Required columns for db:
        - [route_id, stop_ids]. NB: stop_ids is a list of terminal_ids in the Terminal model.
    Expected schema for db:
        route_id VARCHAR(255) NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
        terminal_id VARCHAR(255) NOT NULL REFERENCES terminals(id) ON DELETE CASCADE,
    """
    if os.path.exists(src_association):
        df_association = pd.read_csv(src_association)
        df_routes = pd.read_csv(src_route)
        df_terminals = pd.read_csv(src_terminal)

        required_columns = ['route_id', 'stop_ids']
        check_columns(df_association, required_columns)

        df_association = df_association[required_columns].drop_duplicates()

        for _, row in df_association.iterrows():
            # retrieve route and terminal objects
            if pd.isna(row['stop_ids']) or not row['stop_ids']:
                print(f"Skipping row with missing stop_ids: {row}")
                continue
            # Get the route object
            route_id = row['route_id']
            route_name = df_routes[df_routes['route_id'] == route_id]['name'].values[0]
            route_obj = storage.get_one_by(Route, name=route_name)
            if not route_obj:
                print(f"Route {route_name} not found, skipping.")
                continue
            # Convert stop_ids to a list of terminal IDs
            term_ids = get_list_from_string(row['stop_ids'])
            for t in term_ids:
                term_dict = df_terminals[df_terminals['stop_id'] == t]
                if not term_dict.empty:
                    term_name = term_dict['name'].values[0]
                    terminal = storage.get_one_by(Terminal, name=term_name)
                    if terminal and (terminal not in route_obj.terminals):
                        route_obj.terminals.append(terminal)
                        storage.new(route_obj)  # Mark as modified
        storage.save()
        print(f"Route-Terminal associations loaded: {len(df_association)}")
    else:
        print(f"Route-Terminal association file not found: {src_association}")

def populate_db():
    """Populate the database with initial data."""
    # load_agency()
    # load_suburb()
    # load_routes()
    # load_suburb()
    # load_terminals()
    # load_route_terminals()
    load_bus_stops()

    print("Database population completed. Note: Some sections are commented out for testing purposes.")
if __name__ == "__main__":
    populate_db()
    