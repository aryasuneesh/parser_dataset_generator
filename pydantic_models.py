from typing import List, Optional, Any, Literal, Dict

from pydantic import BaseModel, Field, field_validator

from constants.constants import (
    exposure,
    attribute,
    vehicle,
    asset_type,
    sebi_classification,
    objective,
)


class Attributes(BaseModel):
    node: str = Field(
        ...,
        description=f"Attributes mentioned in the query. Acceptable values are {attribute}",
    )
    qualifier: Optional[str] = Field(
        None,
        description="Qualifier for attribute mentioned. Acceptable values are low & high",
    )
    time: Optional[str] = Field(
        None,
        description="Time associated with the attribute mentioned. Can be specific date, relative date or units with duration",
    )
    quantifier: Optional[str] = Field(
        None,
        description="Quantifier for the attribute mentioned. Acceptable values follow the format - <arithmetic_operator><value><unit> . Eg. >4% , <5% in case of returns , volatility , expense ratio etc. >500cr , <20000cr in case of AUM , Market Cap. & >50 , =100 in case of NAV , VWAP etc.",
    )


class Exposures(BaseModel):
    node: Optional[str] = Field(
        None,
        description=f"Exposures mentioned in the query. Acceptable values fall under - sector exposures. sectors follow the GICS classification - {exposure}.",
    )
    qualifier: Optional[str] = Field(
        default="high",
        description="Qualifier for exposure mentioned. Acceptable values are low, high, or None.",
    )
    quantifier: Optional[str] = Field(
        None,
        description="Quantifier for the exposure mentioned. Acceptable values follow the format - <arithmetic_operator><value><unit>. For sector exposures, use formats like >4%, <5%.",
    )


class Ticker(BaseModel):
    name: str = Field(
        ...,
        description="Name of a security mentioned in the user query. Could be referring to a mutual fund , stock , etf or debt instrument.",
    )


class AssetType(BaseModel):
    node: str = Field(
        ...,
        description=f"Asset type mentioned in the query. Acceptable values are {asset_type}",
    )


class Sebi(BaseModel):
    node: str = Field(
        ...,
        description=f"SEBI classification mentioned in the query. Acceptable values are {sebi_classification}",
    )


class Vehicle(BaseModel):
    node: str = Field(
        ...,
        description=f"Vehicle mentioned in the query. Acceptable values are {vehicle}",
    )


class Objective(BaseModel):
    node: str = Field(
        ...,
        description=f"Objective mentioned in the query. Acceptable values are {objective}",
    )


class ParsedOutput(BaseModel):
    attributes: list[Attributes] = Field(
        default_factory=list, description="Attributes mentioned in the query "
    )
    exposures: list[Exposures] = Field(
        default_factory=list, description="Exposures mentioned in the query"
    )
    tickers: list[Ticker] = Field(
        default_factory=list, description="Securities identified in the query"
    )
    asset_types: list[AssetType] = Field(
        default_factory=list, description="Asset types mentioned in the query"
    )
    sebi: list[Sebi] = Field(
        default_factory=list, description="SEBI classifications mentioned in the query"
    )
    vehicles: list[Vehicle] = Field(
        default_factory=list, description="Investment Vehicles mentioned in the query"
    )
    objectives: list[Objective] = Field(
        default_factory=list, description="Objectives mentioned in the query"
    )

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

    @field_validator(
        "attributes",
        "exposures",
        "sebi",
        "objectives",
        mode="before"
    )
    def set_default_lists(cls, v):
        return v or []
    
# print(ParsedOutput.model_json_schema())

class ParsedOutputReasoned(BaseModel):
    reasoning: str = Field(..., description="Reasoning for the parsed output")
    parsed_output: ParsedOutput = Field(..., description="Parsed output")

class ParsedOutputCombinations(BaseModel):
    combinations: list[ParsedOutput] = Field(..., description="List of parsed outputs")


class UserQuery(BaseModel):
    query: str = Field(..., description="Natural language investment query")


class UserQueries(BaseModel):
    queries: list[UserQuery] = Field(
        ..., description="List of natural language queries"
    )


class Reasoning(BaseModel):
    reasoning: str = Field(..., description="Reasoning for the parsed output")


class ReasoningCombinations(BaseModel):
    combinations: list[Reasoning] = Field(..., description="List of reasoning outputs")


