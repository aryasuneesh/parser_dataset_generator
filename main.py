from generator import (
    generate_natural_query,
    generate_reasoning,
    get_matching_ontologies,
    generate_parsed_output_with_reasoning
)
from utils import rate_limiter

from constants.constants import (
    exposure,
    attribute,
    vehicle,
    asset_type,
    sebi_classification,
    objective
)

import json
import csv
import os
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple
import time
import gc

logger = logging.getLogger(__name__)

def append_to_csv(file_path: str, data: dict):
    """Append a row of data to CSV file"""
    file_exists = os.path.isfile(file_path)
    
    # Clean the data and ensure proper JSON formatting
    cleaned_data = {}
    for k, v in data.items():
        if isinstance(v, (dict, list)):
            # First ensure all keys in nested structures are properly quoted
            json_str = json.dumps(v, ensure_ascii=False)
            # Parse and re-dump to ensure proper formatting
            parsed_json = json.loads(json_str)
            cleaned_data[k] = json.dumps(parsed_json, ensure_ascii=False)
        else:
            cleaned_data[k] = v
    
    with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['original_path', 'matched_paths', 'query', 'reasoning', 'parsed_output']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(cleaned_data)

async def process_single_path(category: str, path: str, file_path: str):
    """Process a single ontology path through the entire pipeline"""
    error_count = 0
    max_errors = 3  # Circuit breaker threshold
    
    logger.info(f"Starting to process path: {category}/{path}")
    
    try:
        base_dict = {category: [path]}
        logger.info(f"Getting matching ontologies for: {path}")
        matched_ontology = await get_matching_ontologies(path)
        
        if not matched_ontology:
            logger.warning(f"No matching ontologies found for path: {path}")
            return
            
        queries = await generate_natural_query(matched_ontology)
        
        for query in queries.queries:
            try:
                if error_count >= max_errors:
                    logger.error(f"Circuit breaker triggered for path {path} after {max_errors} errors")
                    return None
                    
                reasoning = await generate_reasoning(query.query)
                parsed_output = await generate_parsed_output_with_reasoning(
                    query=query.query,
                    reasoning=reasoning
                )
                
                row_data = {
                    'original_path': json.dumps(base_dict),
                    'matched_paths': matched_ontology.model_dump(),
                    'query': query.query,
                    'reasoning': reasoning,
                    'parsed_output': parsed_output.parsed_output.model_dump()
                }
                append_to_csv(file_path, row_data)
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing query '{query.query}': {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error processing path '{path}': {str(e)}")
        return None

async def process_paths_batch(paths_batch: List[Tuple[str, str]], file_path: str):
    """Process a batch of paths with controlled concurrency"""
    results = []
    
    # Process in chunks
    chunk_size = 4  # Process 4 paths concurrently
    for i in range(0, len(paths_batch), chunk_size):
        chunk = paths_batch[i:i + chunk_size]
        chunk_tasks = []
        
        # Create tasks for each path in the chunk
        for var_name, path in chunk:
            task = asyncio.create_task(
                process_single_path(var_name, path, file_path)
            )
            chunk_tasks.append(task)
        
        try:
            # Process chunk concurrently with longer timeout
            chunk_results = await asyncio.wait_for(
                asyncio.gather(*chunk_tasks, return_exceptions=True),
                timeout=180  # 3 minutes timeout
            )
            
            # Clear completed tasks
            for task in chunk_tasks:
                task.cancel()
            
            # Handle each result individually
            for result in chunk_results:
                if isinstance(result, Exception):
                    logger.error(f"Error in chunk result: {str(result)}")
                    results.append(None)
                else:
                    results.append(result)
            
            # Clear memory
            del chunk_tasks
            del chunk_results
            gc.collect()
            
            # Delay between chunks
            await asyncio.sleep(0.5)
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout processing chunk")
            results.extend([None] * len(chunk_tasks))
            await asyncio.sleep(1.0)
            
        except Exception as e:
            logger.error(f"Error processing chunk: {str(e)}")
            results.extend([None] * len(chunk_tasks))
            await asyncio.sleep(1.0)
        
        finally:
            gc.collect()
    
    return results

async def main():
    # Get segment information from environment
    segment_start = int(os.getenv('SEGMENT_START', '0'))
    segment_size = int(os.getenv('SEGMENT_SIZE', '50'))
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Variables from constants.py
    variables = [
        ('exposure', exposure),
        ('attribute', attribute),
        ('vehicle', vehicle),
        ('asset_type', asset_type),
        ('sebi_classification', sebi_classification),
        ('objective', objective)
    ]
    
    # Prepare all paths
    all_paths = []
    for var_name, var_list in variables:
        valid_paths = [(var_name, path) for path in var_list if not path.startswith('#')]  # Only skip commented paths
        paths_count = len(valid_paths)
        all_paths.extend(valid_paths)
        logger.info(f"Added {paths_count} valid paths from {var_name}")
    
    logger.info(f"Total valid paths collected: {len(all_paths)}")
    logger.info(f"Segment range: {segment_start} to {segment_start + segment_size}")

    # Get paths for this segment only
    segment_paths = all_paths[segment_start:segment_start + segment_size]
    file_path = f"datasets/parser_dataset_segment_{segment_start}.csv"

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Process in optimized batch sizes
    batch_size = 20
    total_paths = len(segment_paths)
    processed = 0
    
    try:
        for i in range(0, total_paths, batch_size):
            batch = segment_paths[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}, paths {i+1} to {min(i+batch_size, total_paths)}")
            
            try:
                results = await process_paths_batch(batch, file_path)
                
                processed += len(batch)
                logger.info(f"Processed {processed}/{total_paths} paths in segment {segment_start}")
                
                # Clean up after each batch
                del results
                gc.collect()
                
                # Delay between batches
                if i + batch_size < total_paths:
                    await asyncio.sleep(0.5)
                    
            except Exception as e:
                logger.error(f"Error processing batch {i//batch_size + 1}: {str(e)}")
                gc.collect()
                continue
                
    except KeyboardInterrupt:
        logger.info("\nProcess interrupted by user")
        logger.info(f"Progress: Processed {processed}/{total_paths} paths in segment {segment_start}")
        
    except Exception as e:
        logger.error(f"Fatal error in main process: {str(e)}")
        
    finally:
        gc.collect()
        logger.info(f"Segment {segment_start} completed")
        logger.info(f"Final progress: Processed {processed}/{total_paths} paths in segment {segment_start}")

    current_dir = os.getcwd()
    logger.info(f"Current working directory: {current_dir}")
    logger.info(f"Full file path: {os.path.abspath(file_path)}")

if __name__ == "__main__":
    # Debug info
    logger.info("Starting main.py execution")
    logger.info(f"Environment variables: SEGMENT_START={os.getenv('SEGMENT_START')}, SEGMENT_SIZE={os.getenv('SEGMENT_SIZE')}")
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the async main function
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Fatal error in main(): {str(e)}")
        sys.exit(1)