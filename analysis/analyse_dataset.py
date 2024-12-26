import json
import random
import csv

def analyze_distribution(dataset):
    distributions = {
        'attributes': {},
        'exposures': {},
        'tickers': {},
        'asset_types': {},
        'sebi': {},
        'vehicles': {},
        'objectives': {}
    }
    
    for i, row in enumerate(dataset):
        try:
            # Check if row has at least 2 columns
            if len(row) < 2:
                print(f"Warning: Row {i} does not have enough columns: {row}")
                continue
                
            try:
                data = json.loads(row[4])  # Parse the JSON string in fifth column
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON in row {i}: {row[4]}")
                print(f"Error details: {str(e)}")
                continue
            
            # Count occurrences of each category
            for attr in data.get('attributes', []):
                node = attr.get('node')
                if node:
                    distributions['attributes'][node] = distributions['attributes'].get(node, 0) + 1
                
            for exp in data.get('exposures', []):
                node = exp.get('node')
                if node:
                    distributions['exposures'][node] = distributions['exposures'].get(node, 0) + 1

            for ticker in data.get('tickers', []):
                node = ticker.get('name')
                if node:
                    distributions['tickers'][node] = distributions['tickers'].get(node, 0) + 1

            for asset_type in data.get('asset_types', []):
                node = asset_type.get('node')
                if node:
                    distributions['asset_types'][node] = distributions['asset_types'].get(node, 0) + 1

            for sebi in data.get('sebi', []):
                node = sebi.get('node')
                if node:
                    distributions['sebi'][node] = distributions['sebi'].get(node, 0) + 1

            for vehicle in data.get('vehicles', []):
                node = vehicle.get('node')
                if node:
                    distributions['vehicles'][node] = distributions['vehicles'].get(node, 0) + 1

            for objective in data.get('objectives', []):
                node = objective.get('node')
                if node:
                    distributions['objectives'][node] = distributions['objectives'].get(node, 0) + 1
                    
        except Exception as e:
            print(f"Error processing row {i}: {str(e)}")
            continue

    return distributions

def process_parser_dataset(input_file):
    # Read original dataset
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        dataset = list(reader)
    
    # Analyze distribution
    distributions = analyze_distribution(dataset)
    
    # Calculate total samples
    total_samples = len(dataset)
    
    # Print analysis results
    print(f"\nDataset Analysis (Total samples: {total_samples})")
    print("=" * 50)
    
    # For each category, print sorted frequencies and percentages
    for category, nodes in distributions.items():
        if nodes:  # Only print if there are nodes in this category
            print(f"\n{category.upper()}")
            print("-" * 30)
            
            # Sort nodes by frequency in descending order
            sorted_nodes = sorted(nodes.items(), key=lambda x: x[1], reverse=True)
            
            # Calculate percentages and print
            for node, count in sorted_nodes:
                percentage = (count / total_samples) * 100
                print(f"{node}: {count} ({percentage:.1f}%)")

# Run analysis
process_parser_dataset('datasets/855_parser_dataset.csv')