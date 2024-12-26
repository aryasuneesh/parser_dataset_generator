from pydantic_models import (
    Attributes,
    Exposures,
    Ticker,
    AssetType,
    Sebi,
    Vehicle,
    Objective,
    ParsedOutput,
    ParsedOutputCombinations,
    Reasoning,
    UserQuery,
    UserQueries,
    ReasoningCombinations
)

# EXAMPLES - GENERATED ONTOLOGY | CONSTANTS FOR FEW SHOTS

parsed_output_1 = ParsedOutput(
    attributes=[
        Attributes(
            node="attribute/style/size/mid_cap",
            qualifier="high",
            time=None,
            quantifier=None,
        ),
        Attributes(
            node="attribute/risk/volatility/medium",
            qualifier="high",
            time=None,
            quantifier=None,
        ),
    ],
    exposures=[
        Exposures(node="exposure/factor/growth", qualifier="high", quantifier=">30%"),
        Exposures(
            node="exposure/sector/healthcare",
            qualifier="high",
            time=None,
            quantifier=None,
        ),
    ],
    tickers=[Ticker(name="SUNPHARMA")],
    asset_types=[AssetType(node="asset_type/equity")],
    sebi=[Sebi(node="sebi_classification/equity_schemes/mid_cap_fund")],
    vehicles=[Vehicle(node="vehicle/etf")],
    objectives=[Objective(node="objective/growth")],
)

parsed_output_2 = ParsedOutput(
    attributes=[
        Attributes(
            node="attribute/style/size/large_cap",
            qualifier="high",
            time=None,
            quantifier=None,
        ),
        Attributes(
            node="attribute/returns/alpha",
            qualifier="high",
            time="last_year",
            quantifier=None,
        ),
    ],
    exposures=[
        Exposures(node="exposure/factor/growth", qualifier="high", quantifier=">30%")
    ],
    tickers=[Ticker(name="INFY"), Ticker(name="TCS")],
    asset_types=[AssetType(node="asset_type/equity")],
    sebi=[Sebi(node="sebi_classification/equity_schemes/sectoral_thematic_fund")],
    vehicles=[Vehicle(node="vehicle/mutual_fund")],
    objectives=[Objective(node="objective/growth")],
)

parsed_output_3 = ParsedOutput(
    attributes=[
        Attributes(
            node="attribute/returns/risk_adjusted_returns/high",
            qualifier="high",
            time=None,
            quantifier=None,
        )
    ],
    exposures=[
        Exposures(node="exposure/factor/growth", qualifier="high", quantifier=">30%"),
        Exposures(
            node="exposure/factor/value", qualifier="high", time=None, quantifier=None
        ),
    ],
    tickers=[],
    asset_types=[
        AssetType(node="asset_type/equity"),
        AssetType(node="asset_type/bonds"),
    ],
    sebi=[Sebi(node="sebi_classification/hybrid_schemes/balanced_hybrid_fund")],
    vehicles=[Vehicle(node="vehicle/mutual_fund")],
    objectives=[Objective(node="objective/growth"), Objective(node="objective/income")],
)

parsed_output_combination = ParsedOutputCombinations(
    combinations=[parsed_output_1, parsed_output_2, parsed_output_3]
)

#access just the first query
# print(parsed_output_combination.combinations[0])

# EXAMPLES - GENERATED QUERY | CONSTANTS FOR FEW SHOTS

query_1 = UserQuery(query="What's the cumulative return of Pidilite Inds. over the last year?")
query_2 = UserQuery(query="Show me mutual funds with high risk-adjusted returns.")
query_3 = UserQuery(query="What are the benefits of diversification in an investment portfolio?")

query_combination = UserQueries(queries=[query_1, query_2, query_3])


# EXAMPLES - GENERATED ONTOLOGY NODES | CONSTANTS FOR FEW SHOTS

#generated_node_1 for query_1
generated_node_1 = ParsedOutput(
    attributes=[
        Attributes(
            node="attribute/returns/cumulative_returns",
            qualifier=None,
            time="last year",
            quantifier=None,
        ),
    ],
    exposures=[],
    tickers=[Ticker(name="Pidilite Inds.")],
    asset_types=[],
    sebi=[],
    vehicles=[Vehicle(node="vehicle/stock")],
    objectives=[],
)

generated_node_2 = ParsedOutput(
    attributes=[
        Attributes(
            node="attribute/returns/risk_adjusted_returns",
            qualifier="high",
            time=None,
            quantifier=None,
        ),
    ],
    exposures=[],
    tickers=[],
    asset_types=[],
    sebi=[],
    vehicles=[
        Vehicle(node="vehicle/mutual_fund"),
    ],
    objectives=[],
)

generated_node_3 = ParsedOutput(
    attributes=[],
    exposures=[],
    tickers=[],
    asset_types=[],
    sebi=[],
    vehicles=[
        Vehicle(node="vehicle/portfolio"),
    ],
    objectives=[],
)

generated_ontology_nodes = ParsedOutputCombinations(
    combinations=[generated_node_1, generated_node_2, generated_node_3]
)

# GENERATED REASONING | CONSTANTS FOR FEW SHOTS

reasoning_1 = Reasoning(reasoning="This query is looking for the cumulative return of a specific ticker (Pidilite Inds.) over the last year. The key elements are the attribute (cumulative return), the qualifying time period (1 year), and the specific ticker (Pidilite Inds.).")
reasoning_2 = Reasoning(reasoning="This query is looking for mutual funds with high risk-adjusted returns. The key elements are the attribute (risk-adjusted returns), the qualifying criterion (high), and the absence of specific tickers or asset types.")
reasoning_3 = Reasoning(reasoning="This query is looking for benefits of diversification in an investment portfolio. The key elements are the attribute (diversification), and the absence of specific tickers, asset types, or vehicles.")

generated_reasoning = ReasoningCombinations(
    combinations=[reasoning_1, reasoning_2, reasoning_3]
)