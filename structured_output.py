import asyncio
import logging
import instructor
from typing import Literal
from pydantic_models import (
    ParsedOutput,
    ParsedOutputReasoned,
    ParsedOutputCombinations,
    Reasoning,
    UserQueries
)
from pydantic import BaseModel, Field
from utils import rate_limiter
from concurrent.futures import ThreadPoolExecutor


# Configure logger
logger = logging.getLogger(__name__)

import sys
sys.setrecursionlimit(3000)

class NaturalQuery(BaseModel):
    query: str = Field(..., description="Natural language investment query")

class NaturalQueries(BaseModel):
    queries: list[NaturalQuery] = Field(..., description="List of natural language queries")

class OntologyMatch(BaseModel):
    original_path: dict = Field(..., description="Original ontology path")
    matched_paths: dict = Field(..., description="Matched ontology paths")
    

async def get_structured_openai_response(
    client,
    messages: list,
    response_model: Literal[ParsedOutput, ParsedOutputReasoned, ParsedOutputCombinations, Reasoning, UserQueries],
    max_tokens: int = 1500,
    model_name: str = "gpt-4o",
    temperature: float = 1.0,
    timeout: int = 30
):
    max_retries = 3
    retry_count = 0
    backoff = 1
    
    while retry_count < max_retries:
        try:
            await rate_limiter.acquire()
            patched_client = instructor.patch(client)
            
            def make_request():
                try:
                    return patched_client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        max_tokens=max_tokens,
                        seed=123,
                        temperature=temperature,
                        response_model=response_model,
                        validation_context={"strict": True},
                    )
                except Exception as e:
                    return e

            async with asyncio.timeout(timeout):
                # Use ThreadPoolExecutor explicitly
                with ThreadPoolExecutor() as executor:
                    response = await asyncio.get_event_loop().run_in_executor(
                        executor, 
                        make_request
                    )
                    
                    if isinstance(response, Exception):
                        raise response
                        
                    return response
                
        except asyncio.TimeoutError:
            logger.error(f"Request timed out (attempt {retry_count + 1}/{max_retries})")
            retry_count += 1
            if retry_count == max_retries:
                raise
            await asyncio.sleep(backoff)
            backoff *= 2
        except Exception as e:
            logger.error(f"Error (attempt {retry_count + 1}/{max_retries}): {str(e)}")
            retry_count += 1
            if retry_count == max_retries:
                raise
            await asyncio.sleep(backoff)
            backoff *= 2