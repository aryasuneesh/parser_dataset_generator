import json
import csv
from typing import Dict, List, Set

def extract_nodes_from_combinations(combinations: List[dict]) -> Dict[str, Set[str]]:
    """Extract all nodes from combinations structure in matched_paths"""
    nodes = {
        'attributes': set(),
        'exposures': set(),
        'tickers': set(),
        'asset_types': set(),
        'sebi': set(),
        'vehicles': set(),
        'objectives': set()
    }
    
    for combo in combinations:
        for category in nodes.keys():
            if category in combo:
                for item in combo[category]:
                    if category == 'tickers':
                        if 'name' in item:
                            nodes[category].add(item['name'])
                    else:
                        if 'node' in item:
                            nodes[category].add(item['node'])
    return nodes

def extract_nodes_from_parsed_output(parsed_output: dict) -> Dict[str, Set[str]]:
    """Extract all nodes from parsed output structure"""
    nodes = {
        'attributes': set(),
        'exposures': set(),
        'tickers': set(),
        'asset_types': set(),
        'sebi': set(),
        'vehicles': set(),
        'objectives': set()
    }
    
    for category in nodes.keys():
        if category in parsed_output:
            for item in parsed_output[category]:
                if category == 'tickers':
                    if 'name' in item:
                        nodes[category].add(item['name'])
                else:
                    if 'node' in item:
                        nodes[category].add(item['node'])
    return nodes

def extract_nodes_from_original_path(original_data: dict) -> Dict[str, Set[str]]:
    """Extract nodes from original path structure"""
    nodes = {
        'attributes': set(),
        'exposures': set(),
        'tickers': set(),
        'asset_types': set(),
        'sebi': set(),
        'vehicles': set(),
        'objectives': set()
    }
    
    # Map the original keys to our standardized categories
    category_mapping = {
        'exposure': 'exposures',
        'attribute': 'attributes',
        'ticker': 'tickers',
        'asset_type': 'asset_types',
        'sebi_classification': 'sebi',
        'vehicle': 'vehicles',
        'objective': 'objectives'
    }
    
    for orig_category, paths in original_data.items():
        if orig_category in category_mapping:
            category = category_mapping[orig_category]
            nodes[category].update(paths)
    
    return nodes

def format_coverage_analysis(row_idx: int, original_nodes: Dict[str, Set[str]], 
                           matched_nodes: Dict[str, Set[str]], 
                           parsed_nodes: Dict[str, Set[str]]) -> str:
    """Format the coverage analysis as readable text"""
    lines = [f"Analysis for Row {row_idx}:"]
    lines.append("=" * 50)
    
    # Analyze each category
    for category in original_nodes.keys():
        orig_paths = original_nodes[category]
        matched_paths = matched_nodes[category]
        parsed_paths = parsed_nodes[category]
        
        if orig_paths or matched_paths:  # Only analyze categories that have paths
            lines.append(f"\n{category.upper()}:")
            lines.append("-" * 30)
            
            # Check original paths coverage
            if orig_paths:
                missing_from_parsed = orig_paths - parsed_paths
                if missing_from_parsed:
                    lines.append("\nOriginal paths missing from parsed output:")
                    for path in sorted(missing_from_parsed):
                        lines.append(f"  - {path}")
            
            # Check matched paths coverage
            if matched_paths:
                missing_from_parsed = matched_paths - parsed_paths
                if missing_from_parsed:
                    lines.append("\nMatched paths missing from parsed output:")
                    for path in sorted(missing_from_parsed):
                        lines.append(f"  - {path}")
    
    return "\n".join(lines)

def analyze_path_coverage(input_file: str, output_file: str):
    with open(output_file, 'w', newline='', encoding='utf-8') as outf:
        writer = csv.writer(outf)
        writer.writerow(['row_number', 'original_path', 'matched_paths', 'parsed_output', 'analysis_results'])
        
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_idx, row in enumerate(reader, start=1):
                try:
                    # Parse JSON structures
                    original_data = json.loads(row['original_path'])
                    matched_data = json.loads(row['matched_paths'])
                    parsed_data = json.loads(row['parsed_output'])
                    
                    # Extract nodes from each structure
                    original_nodes = extract_nodes_from_original_path(original_data)
                    matched_nodes = extract_nodes_from_combinations(matched_data['combinations'])
                    parsed_nodes = extract_nodes_from_parsed_output(parsed_data)
                    
                    # Generate analysis
                    analysis = format_coverage_analysis(row_idx, original_nodes, 
                                                      matched_nodes, parsed_nodes)
                    
                    # Write to CSV
                    writer.writerow([
                        row_idx,
                        row['original_path'],
                        row['matched_paths'],
                        row['parsed_output'],
                        analysis
                    ])
                    
                except Exception as e:
                    print(f"Error processing row {row_idx}: {str(e)}")

def main():
    input_file = 'datasets/855_parser_dataset.csv'
    output_file = 'datasets/855_parser_dataset_path_coverage.csv'
    analyze_path_coverage(input_file, output_file)

if __name__ == "__main__":
    main() 