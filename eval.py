import json
import pandas as pd
from typing import Dict, List, Set

def extract_nodes_from_json(json_str: str) -> Set[str]:
    """
    Extract all unique nodes from the parsed JSON output.
    Returns a set of node strings using just the node value
    """
    try:
        # Clean up the input string if it's a string
        if isinstance(json_str, str):
            # Remove '###\n' if present at the start
            if json_str.startswith('###'):
                json_str = json_str.split('###\n', 1)[1]
            data = json.loads(json_str)
        else:
            data = json_str
            
        # If the data has parsed_output field, use that
        if isinstance(data, dict) and 'parsed_output' in data:
            parsed_output = data['parsed_output']
        else:
            parsed_output = data
        
        nodes = set()
        # Categories to check
        categories = ['attributes', 'exposures', 'tickers', 'asset_types', 'sebi', 'vehicles', 'objectives']
        
        for category in categories:
            items = parsed_output.get(category, [])
            if not isinstance(items, list):
                continue
                
            for item in items:
                if not isinstance(item, dict):
                    continue
                    
                # For tickers, use 'name' field
                if category == 'tickers':
                    if 'name' in item:
                        nodes.add(item['name'])
                # For all other categories, use 'node' field
                elif 'node' in item:
                    nodes.add(item['node'])
        
        return nodes
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Problematic string: {json_str}")
        return set()
    except Exception as e:
        print(f"Error processing JSON: {e}")
        print(f"Problematic data: {json_str}")
        return set()

def compare_nodes(generated: Set[str], original: Set[str]) -> Dict[str, Set[str]]:
    """
    Compare two sets of nodes and return matching, missing, and mismatched nodes
    """
    return {
        'matching': generated & original,
        'missing': original - generated,
        'mismatched': generated - original
    }

def process_csv(input_file: str, output_file: str):
    """
    Process the CSV file and create an evaluation report with scoring
    """
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Create lists to store results
    matching_nodes = []
    missing_nodes = []
    mismatched_nodes = []
    generated_counts = []
    original_counts = []
    matching_counts = []
    missing_counts = []
    mismatched_counts = []
    
    # Tracking overall statistics
    total_correct = 0
    total_incorrect = 0
    
    # Process each row
    for idx, row in df.iterrows():
        print(f"\n=== Row {idx} ===")
        print("Generated Response (raw):", repr(row['generated_response']))
        print("Original Output (raw):", repr(row['original_parsed_output']))
        
        # Extract nodes from both outputs
        generated_nodes = extract_nodes_from_json(row['generated_response'])
        original_nodes = extract_nodes_from_json(row['original_parsed_output'])
        
        print("Generated nodes:", generated_nodes)
        print("Original nodes:", original_nodes)
        
        # Compare nodes
        comparison = compare_nodes(generated_nodes, original_nodes)
        print("Comparison results:", comparison)
        
        # Store results
        matching_nodes.append(', '.join(sorted(comparison['matching'])))
        missing_nodes.append(', '.join(sorted(comparison['missing'])))
        mismatched_nodes.append(', '.join(sorted(comparison['mismatched'])))
        
        # Store counts
        generated_counts.append(len(generated_nodes))
        original_counts.append(len(original_nodes))
        matching_counts.append(len(comparison['matching']))
        missing_counts.append(len(comparison['missing']))
        mismatched_counts.append(len(comparison['mismatched']))
        
        # Update overall statistics
        if len(comparison['missing']) == 0 and len(comparison['mismatched']) == 0:
            total_correct += 1
        else:
            total_incorrect += 1
    
    # Print overall statistics
    print("\n=== Overall Statistics ===")
    print(f"Total correctly matched queries: {total_correct}")
    print(f"Total incorrectly matched queries: {total_incorrect}")
    print(f"Accuracy: {total_correct/(total_correct + total_incorrect):.2%}")
    
    # Add new columns to the dataframe
    df['generated_node_count'] = generated_counts
    df['original_node_count'] = original_counts
    df['matching_nodes'] = matching_nodes
    df['matching_node_count'] = matching_counts
    df['missing_nodes'] = missing_nodes
    df['missing_node_count'] = missing_counts
    df['mismatched_nodes'] = mismatched_nodes
    df['mismatched_node_count'] = mismatched_counts
    
    # Save the results
    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    input_file = "42_llama_val_results.csv"
    output_file = "42_llama_evaluation_results.csv"
    process_csv(input_file, output_file)