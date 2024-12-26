import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import logging
from pydantic_models import (
    ParsedOutput,
    ParsedOutputReasoned,
    UserQuery,
    UserQueries,
    Reasoning,
    ParsedOutputCombinations,
    ReasoningCombinations
)
from structured_output import get_structured_openai_response
from prompt import (
    PARSED_OUTPUT_SYSTEM_PROMPT_1,
    PARSED_OUTPUT_SYSTEM_PROMPT_2,
    PARSED_OUTPUT_SYSTEM_PROMPT_3,
    ONTOLOGY_MATCHING_PROMPT,
    NATURAL_QUERY_GENERATION_PROMPT,
    REASONING_GENERATION_PROMPT
)
from few_shot_examples import (
    parsed_output_combination,
    query_combination,
    generated_ontology_nodes,
    generated_reasoning
)
import asyncio
from utils import rate_limiter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

async def get_matching_ontologies(path: str) -> ParsedOutputCombinations:
    logger.info(f"Getting matching ontologies for path: {path}")
    
    system_prompt = ONTOLOGY_MATCHING_PROMPT
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Generate THREE DIFFERENT matching ontology combinations for path: exposure/factor/growth"},
        {"role": "assistant", "content": json.dumps(parsed_output_combination.model_dump())},
        {"role": "user", "content": f"Generate THREE DIFFERENT matching ontology combinations for path: {path}"},
    ]
    
    return await get_structured_openai_response(
        client=client,
        messages=messages,
        response_model=ParsedOutputCombinations,
        max_tokens=1500,
        temperature=0.9
    )

async def generate_natural_query(ontology_paths: ParsedOutputCombinations) -> UserQueries:
    logger.info(f"Generating natural queries for paths")
    try:
        system_prompt = NATURAL_QUERY_GENERATION_PROMPT
        # print("\n\nFIRST ONTOLOGY PATH: ", ontology_paths.combinations[0])

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate a user query for each of the three ontology paths mentioned: {generated_ontology_nodes}"},
            {"role": "assistant", "content": f"{query_combination}"},
            {"role": "user", "content": f"Generate a user query for each of the three ontology paths mentioned: {ontology_paths}"},
        ]

        return await get_structured_openai_response(
            client=client,
            messages=messages,
            response_model=UserQueries,
            max_tokens=1500,
            temperature=0.7
        )
    except Exception as e:
        logger.error(f"Error generating natural queries: {str(e)}")
        raise

async def generate_reasoning(query: str) -> str:
    """Generate reasoning for a given natural language query"""
    system_prompt = REASONING_GENERATION_PROMPT

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Generate reasoning for this investment query: {query_combination.queries[0].query}"},
        {"role": "assistant", "content": f"{generated_reasoning.combinations[0]}"},
        {"role": "user", "content": f"Generate reasoning for this investment query: {query_combination.queries[1].query}"},
        {"role": "assistant", "content": f"{generated_reasoning.combinations[1]}"},
        {"role": "user", "content": f"Generate reasoning for this investment query: {query_combination.queries[2].query}"},
        {"role": "assistant", "content": f"{generated_reasoning.combinations[2]}"},
        {"role": "user", "content": f"Generate reasoning for this investment query: {query}"},
    ]

    reasoning_response = await get_structured_openai_response(
        client=client,
        messages=messages,
        response_model=Reasoning,
        max_tokens=1500,
        temperature=0.5
    )
    return reasoning_response.reasoning

async def generate_parsed_output_with_reasoning(query: str, reasoning: str) -> ParsedOutputReasoned:
    logger.info(f"Parsing query and reasoning into structured output")
    try:
        system_prompt = PARSED_OUTPUT_SYSTEM_PROMPT_3

        messages = [
            {"role": "system", "content": system_prompt},

            {"role": "user", "content": f"""
                Query: {query}
                Reasoning: {reasoning}                
            """}
        ]

        return await get_structured_openai_response(
            client=client,
            messages=messages,
            response_model=ParsedOutputReasoned,
            max_tokens=1500,
            temperature=0.6
        )
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON response: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error generating parsed output: {str(e)}")
        raise



# asyncio.run(get_matching_ontologies("exposure/region/international"))
# asyncio.run(generate_natural_query(parsed_output_combination))