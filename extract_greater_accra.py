#!/usr/bin/env python3
"""
Script to extract only the Greater Accra polygons from the Ghana administrative boundaries GeoJSON file.
"""

import json
import sys
import os

def extract_greater_accra_polygons(input_file, output_file):
    """
    Extract Greater Accra features from the input GeoJSON file and save to output file.
    
    Args:
        input_file (str): Path to the input GeoJSON file
        output_file (str): Path to the output GeoJSON file for Greater Accra only
    """
    try:
        # Read the input GeoJSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Filter features for Greater Accra only
        greater_accra_features = []
        
        for feature in data.get('features', []):
            properties = feature.get('properties', {})
            # Check if this feature is for Greater Accra
            if properties.get('NAME_1') == 'GreaterAccra':
                greater_accra_features.append(feature)
        
        # Create new GeoJSON structure with only Greater Accra features
        greater_accra_geojson = {
            "type": "FeatureCollection",
            "name": "gadm41_GHA_1_GreaterAccra",
            "crs": data.get('crs', {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
                }
            }),
            "features": greater_accra_features
        }
        
        # Write the filtered data to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(greater_accra_geojson, f, indent=2)
        
        print(f"Successfully extracted {len(greater_accra_features)} Greater Accra feature(s)")
        print(f"Output saved to: {output_file}")
        
        # Print summary information
        for i, feature in enumerate(greater_accra_features):
            props = feature.get('properties', {})
            print(f"Feature {i+1}:")
            print(f"  GID_1: {props.get('GID_1', 'N/A')}")
            print(f"  NAME_1: {props.get('NAME_1', 'N/A')}")
            print(f"  ISO_1: {props.get('ISO_1', 'N/A')}")
            print(f"  Geometry Type: {feature.get('geometry', {}).get('type', 'N/A')}")
        
        return True
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return False
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file. {e}")
        return False
    except Exception as e:
        print(f"Error: An unexpected error occurred. {e}")
        return False

def main():
    # Default file paths
    input_file = r"e:\amihere\Hackathon\umpire\data\data_src\gadm41_GHA_1.json"
    output_file = r"e:\amihere\Hackathon\umpire\data\data_src\greater_accra_polygons.json"
    
    # Allow command line arguments to override defaults
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print("-" * 50)
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        return
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Extract Greater Accra polygons
    success = extract_greater_accra_polygons(input_file, output_file)
    
    if success:
        print("\n✅ Extraction completed successfully!")
    else:
        print("\n❌ Extraction failed!")

if __name__ == "__main__":
    main()
