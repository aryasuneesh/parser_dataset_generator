# to transform synthetic dataset from three columns to two columns (reasoning and parsed_output combined to one column)

import pandas as pd
import json
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

# First, define the Pydantic models as provided
class Attributes(BaseModel):
    node: str = Field(
        ...,
        description="Attributes mentioned in the query"
    )
    qualifier: Optional[str] = Field(
        None,
        description="Qualifier for attribute mentioned"
    )
    time: Optional[str] = Field(
        None,
        description="Time associated with the attribute mentioned"
    )
    quantifier: Optional[str] = Field(
        None,
        description="Quantifier for the attribute mentioned"
    )

class Exposures(BaseModel):
    node: Optional[str] = Field(
        None,
        description="Exposures mentioned in the query"
    )
    qualifier: Optional[str] = Field(
        default="high",
        description="Qualifier for exposure mentioned"
    )
    quantifier: Optional[str] = Field(
        None,
        description="Quantifier for the exposure mentioned"
    )

class Ticker(BaseModel):
    name: str = Field(
        ...,
        description="Name of a security mentioned"
    )

class AssetType(BaseModel):
    node: str = Field(
        ...,
        description="Asset type mentioned in the query"
    )

class Sebi(BaseModel):
    node: str = Field(
        ...,
        description="SEBI classification mentioned"
    )

class Vehicle(BaseModel):
    node: str = Field(
        ...,
        description="Vehicle mentioned in the query"
    )

class Objective(BaseModel):
    node: str = Field(
        ...,
        description="Objective mentioned in the query"
    )

class ParsedOutput(BaseModel):
    attributes: List[Attributes] = Field(default_factory=list)
    exposures: List[Exposures] = Field(default_factory=list)
    tickers: List[Ticker] = Field(default_factory=list)
    asset_types: List[AssetType] = Field(default_factory=list)
    sebi: List[Sebi] = Field(default_factory=list)
    vehicles: List[Vehicle] = Field(default_factory=list)
    objectives: List[Objective] = Field(default_factory=list)

    @field_validator('tickers', mode='before')
    def convert_tickers(cls, v):
        if not v:
            return []
        processed = []
        for item in v:
            if isinstance(item, Ticker):
                processed.append(item)
            elif isinstance(item, dict) and 'name' in item:
                processed.append(Ticker(name=item['name']))
            elif isinstance(item, str):
                processed.append(Ticker(name=item))
            else:
                raise ValueError(f"Invalid ticker format: {item}")
        return processed

    @field_validator('vehicles', mode='before')
    def convert_vehicles(cls, v):
        if not v:
            return []
        processed = []
        for item in v:
            if isinstance(item, Vehicle):
                processed.append(item)
            elif isinstance(item, dict) and 'node' in item:
                processed.append(Vehicle(node=item['node']))
            elif isinstance(item, str):
                processed.append(Vehicle(node=item))
            else:
                raise ValueError(f"Invalid vehicle format: {item}")
        return processed

    @field_validator('asset_types', mode='before')
    def convert_asset_types(cls, v):
        if not v:
            return []
        processed = []
        for item in v:
            if isinstance(item, AssetType):
                processed.append(item)
            elif isinstance(item, dict) and 'node' in item:
                processed.append(AssetType(node=item['node']))
            elif isinstance(item, str):
                processed.append(AssetType(node=item))
            else:
                raise ValueError(f"Invalid asset type format: {item}")
        return processed

class ParsedOutputReasoned(BaseModel):
    reasoning: str
    parsed_output: ParsedOutput

def transform_csv(input_file: str, output_file: str):
    """
    Transform CSV from old format to new format.
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file
    """
    try:
        # Read the CSV file
        df = pd.read_csv(input_file)
        
        # Create the new reasoned_parsed_output column
        def combine_reasoning_and_output(row):
            # Parse the parsed_output string to dict if it's a string
            if isinstance(row['parsed_output'], str):
                parsed_output = json.loads(row['parsed_output'])
            else:
                parsed_output = row['parsed_output']
            
            # Create the new format
            new_format = {
                'reasoning': row['reasoning'],
                'parsed_output': parsed_output
            }
            
            # Validate using Pydantic
            try:
                validated_output = ParsedOutputReasoned(**new_format)
                return json.dumps(validated_output.model_dump())
            except Exception as e:
                print(f"Validation error for row: {row}")
                print(f"Error: {str(e)}")
                return None
        
        # Apply the transformation
        df['reasoned_parsed_output'] = df.apply(combine_reasoning_and_output, axis=1)
        
        # Select only the required columns
        df_new = df[['query', 'reasoned_parsed_output']]
        
        # Write to new CSV file
        df_new.to_csv(output_file, index=False)
        print(f"Successfully transformed CSV and saved to {output_file}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    transform_csv("datasets/855/855_parser_dataset.csv", "datasets/855_parser_dataset_transformed.csv")