import pandas as pd
import numpy as np

def shuffle_dataset(filename):
    # Read the CSV file
    df = pd.read_csv(filename)
    
    # Create a random permutation of indices
    shuffled_indices = np.random.permutation(len(df))
    
    # Shuffle the DataFrame using these indices
    shuffled_df = df.iloc[shuffled_indices].reset_index(drop=True)
    
    # Generate output filename
    output_filename = filename.rsplit('.', 1)[0] + '_shuffled.csv'
    
    # Save the shuffled DataFrame
    shuffled_df.to_csv(output_filename, index=False)
    
    print(f"Original dataset shape: {df.shape}")
    print(f"Shuffled dataset shape: {shuffled_df.shape}")
    print(f"Shuffled dataset saved to: {output_filename}")
    
    # Return the shuffled dataframe in case needed for further processing
    return shuffled_df

# Usage example:
shuffled_data = shuffle_dataset('855_parser_dataset_transformed.csv')