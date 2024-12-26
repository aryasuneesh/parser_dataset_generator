import pandas as pd
import os
import glob

def merge_segment_files():
    # Path to the datasets directory
    datasets_dir = 'datasets'
    
    # Pattern to match segment files
    pattern = os.path.join(datasets_dir, 'parser_dataset_segment_*.csv')
    
    # Get all segment files sorted numerically
    segment_files = sorted(
        glob.glob(pattern),
        key=lambda x: int(x.split('_')[-1].replace('.csv', ''))
    )
    
    print(f"Found {len(segment_files)} segment files")
    
    # Read and combine all segments
    dfs = []
    for file in segment_files:
        print(f"Reading {file}...")
        try:
            df = pd.read_csv(file)
            dfs.append(df)
            print(f"Added {len(df)} rows from {file}")
        except Exception as e:
            print(f"Error reading {file}: {str(e)}")
    
    if not dfs:
        print("No valid segment files found!")
        return
    
    # Combine all dataframes
    print("\nMerging segments...")
    final_df = pd.concat(dfs, ignore_index=True)
    
    # Save merged file
    output_file = os.path.join(datasets_dir, 'parser_dataset_final.csv')
    final_df.to_csv(output_file, index=False)
    
    print(f"\nMerge complete!")
    print(f"Total rows in final dataset: {len(final_df)}")
    print(f"Final file saved as: {output_file}")

if __name__ == "__main__":
    merge_segment_files()