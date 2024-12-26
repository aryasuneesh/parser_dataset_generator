import json
import csv
from constants.constants import (
    exposure,
    attribute,
    vehicle,
    asset_type,
    sebi_classification as sebi,
    objective
)

def analyze_node_coverage(dataset):
    # Initialize sets to track unique nodes found in dataset
    found_nodes = {
        'attributes': set(),
        'exposures': set(),
        'tickers': set(),
        'asset_types': set(),
        'sebi': set(),
        'vehicles': set(),
        'objectives': set()
    }
    
    # Process each row in dataset
    for i, row in enumerate(dataset):
        try:
            if len(row) < 2:
                print(f"Warning: Row {i} does not have enough columns: {row}")
                continue
                
            try:
                data = json.loads(row[4])
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON in row {i}: {row[4]}")
                continue
            
            # Collect unique nodes from each category
            for attr in data.get('attributes', []):
                node = attr.get('node')
                if node:
                    found_nodes['attributes'].add(node)
                
            for exp in data.get('exposures', []):
                node = exp.get('node')
                if node:
                    found_nodes['exposures'].add(node)

            for ticker in data.get('tickers', []):
                node = ticker.get('name')
                if node:
                    found_nodes['tickers'].add(node)

            for asset_type_item in data.get('asset_types', []):
                node = asset_type_item.get('node')
                if node:
                    found_nodes['asset_types'].add(node)

            for sebi_item in data.get('sebi', []):
                node = sebi_item.get('node')
                if node:
                    found_nodes['sebi'].add(node)

            for vehicle_item in data.get('vehicles', []):
                node = vehicle_item.get('node')
                if node:
                    found_nodes['vehicles'].add(node)

            for objective_item in data.get('objectives', []):
                node = objective_item.get('node')
                if node:
                    found_nodes['objectives'].add(node)
                    
        except Exception as e:
            print(f"Error processing row {i}: {str(e)}")
            continue

    # Compare with constants and print coverage
    print("\nNode Coverage Analysis")
    print("=" * 50)
    
    # Map of category names to their constant lists
    constant_maps = {
        'attributes': attribute,
        'exposures': exposure,
        'asset_types': asset_type,
        'sebi': sebi,
        'vehicles': vehicle,
        'objectives': objective
    }
    
    # Analyze coverage for each category
    for category, constant_list in constant_maps.items():
        found = found_nodes[category]
        total_nodes = len(constant_list)
        covered_nodes = len([node for node in constant_list if node in found])
        coverage_percent = (covered_nodes / total_nodes * 100) if total_nodes > 0 else 0
        
        print(f"\n{category.upper()}")
        print("-" * 30)
        print(f"Total nodes in constants: {total_nodes}")
        print(f"Nodes found in dataset: {covered_nodes}")
        print(f"Coverage: {coverage_percent:.1f}%")
        
        # Print missing nodes
        missing_nodes = set(constant_list) - found
        if missing_nodes:
            print("\nMissing nodes:")
            for node in sorted(missing_nodes):
                print(f"  - {node}")

    return found_nodes

def process_parser_dataset(input_file):
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        dataset = list(reader)
    
    found_nodes = analyze_node_coverage(dataset)
    return found_nodes

# Run analysis
process_parser_dataset('datasets/855_parser_dataset.csv')
