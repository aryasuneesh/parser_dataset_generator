import json
import pandas as pd
import ast
from typing import List, Dict, Set, Tuple
from pydantic import BaseModel
from pydantic_models import ParsedOutput, Exposures, Vehicle, Attributes, Ticker, AssetType, Sebi, Objective

def parse_generated_response(response: str) -> ParsedOutput:
    """Parse the generated response JSON and extract parsed_output"""
    try:
        response_dict = json.loads(response)
        return ParsedOutput(**response_dict['parsed_output'])
    except Exception as e:
        print(f"Error parsing generated response: {e}")
        return ParsedOutput()

def parse_original_output(output: str) -> ParsedOutput:
    """Convert original_parsed_output string to ParsedOutput"""
    try:
        # Remove class names from the string to make it valid Python literal
        output = output.replace('Attributes(', 'dict(')
        output = output.replace('Exposures(', 'dict(')
        output = output.replace('Ticker(', 'dict(')
        output = output.replace('Vehicle(', 'dict(')
        output = output.replace('AssetType(', 'dict(')
        output = output.replace('Sebi(', 'dict(')
        output = output.replace('Objective(', 'dict(')
        
        # Convert string representation to tuple
        parsed_tuple = ast.literal_eval(output)
        
        # Convert dictionaries back to proper objects
        def convert_dicts(lst, cls):
            return [cls(**item) if isinstance(item, dict) else item for item in lst]
        
        # Create ParsedOutput with the corresponding lists
        return ParsedOutput(
            attributes=convert_dicts(parsed_tuple[0], Attributes),
            exposures=convert_dicts(parsed_tuple[1], Exposures),
            tickers=convert_dicts(parsed_tuple[2], Ticker),
            asset_types=convert_dicts(parsed_tuple[3], AssetType),
            sebi=convert_dicts(parsed_tuple[4], Sebi),
            vehicles=convert_dicts(parsed_tuple[5], Vehicle) if len(parsed_tuple) > 5 else [],
            objectives=convert_dicts(parsed_tuple[6], Objective) if len(parsed_tuple) > 6 else []
        )
    except Exception as e:
        print(f"Error parsing original output: {e}")
        return ParsedOutput()

def extract_nodes(parsed_output: ParsedOutput) -> Dict[str, Set[str]]:
    """Extract all nodes from a ParsedOutput object"""
    nodes = {
        'attributes': {attr.node for attr in parsed_output.attributes},
        'exposures': {exp.node for exp in parsed_output.exposures if exp.node},
        'tickers': {ticker.name for ticker in parsed_output.tickers},
        'asset_types': {asset.node for asset in parsed_output.asset_types},
        'sebi': {s.node for s in parsed_output.sebi},
        'vehicles': {v.node for v in parsed_output.vehicles},
        'objectives': {obj.node for obj in parsed_output.objectives}
    }
    return nodes

def compare_outputs(generated: ParsedOutput, original: ParsedOutput) -> Tuple[bool, Dict[str, List[str]], Dict[str, List[str]]]:
    """Compare generated and original outputs"""
    generated_nodes = extract_nodes(generated)
    original_nodes = extract_nodes(original)
    
    # Check matches
    all_matched = all(
        generated_nodes[category] == original_nodes[category]
        for category in generated_nodes.keys()
    )
    
    # Find missing nodes
    missing_nodes = {
        category: list(original_nodes[category] - generated_nodes[category])
        for category in original_nodes.keys()
        if original_nodes[category] - generated_nodes[category]
    }
    
    # Find wrong nodes
    wrong_nodes = {
        category: list(generated_nodes[category] - original_nodes[category])
        for category in generated_nodes.keys()
        if generated_nodes[category] - original_nodes[category]
    }
    
    return all_matched, missing_nodes, wrong_nodes

def evaluate_results(df: pd.DataFrame) -> pd.DataFrame:
    """Evaluate the results and create output DataFrame"""
    results = []
    
    for _, row in df.iterrows():
        try:
            # Parse outputs
            generated = parse_generated_response(row['generated_response'])
            original = parse_original_output(row['original_parsed_output'])
            
            # Compare outputs
            all_matched, missing_nodes, wrong_nodes = compare_outputs(generated, original)
            
            results.append({
                'query': row['query'],
                'all_nodes_matched': all_matched,
                'missing_nodes': json.dumps(missing_nodes) if missing_nodes else '',
                'wrong_nodes': json.dumps(wrong_nodes) if wrong_nodes else ''
            })
        except Exception as e:
            print(f"Error processing row: {e}")
            results.append({
                'query': row['query'],
                'all_nodes_matched': False,
                'missing_nodes': 'Error processing',
                'wrong_nodes': str(e)
            })
    
    return pd.DataFrame(results)

def main():
    # Read input CSV
    df = pd.read_csv('val_results.csv')
    
    # Evaluate results
    results_df = evaluate_results(df)
    
    # Save to CSV
    results_df.to_csv('evaluation_results.csv', index=False)
    print("Evaluation completed and saved to evaluation_results.csv")

if __name__ == "__main__":
    main()