import os
import sys
import asyncio
import subprocess
from typing import List
import logging
from constants.constants import count_paths_with_depth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_segment(start: int, size: int) -> None:
    """Run a single segment asynchronously"""
    segment_num = start // size + 1
    logger.info(f"Starting segment {segment_num} (paths {start} to {start + size})")
    
    env = os.environ.copy()
    env['SEGMENT_START'] = str(start)
    env['SEGMENT_SIZE'] = str(size)
    
    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            'main.py',
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Handle both stdout and stderr concurrently
        async def read_stream(stream, prefix):
            while True:
                line = await stream.readline()
                if not line:
                    break
                logger.info(f"Segment {segment_num} {prefix}: {line.decode().strip()}")
                
        # Create tasks for both streams
        stdout_task = asyncio.create_task(read_stream(process.stdout, "OUT"))
        stderr_task = asyncio.create_task(read_stream(process.stderr, "ERR"))
        
        # Wait for both streams and process to complete
        await asyncio.gather(stdout_task, stderr_task)
        await process.wait()
        
        if process.returncode == 0:
            logger.info(f"Segment {segment_num} completed successfully")
        else:
            logger.error(f"Segment {segment_num} failed with return code {process.returncode}")
                
    except Exception as e:
        logger.error(f"Error running segment {segment_num}: {str(e)}")
 
async def run_segments_concurrently():
    total_paths, _ = count_paths_with_depth()  # Get actual number of valid paths
    segment_size = 30  # Adjusted for more paths
    max_concurrent = 5  # Keep concurrent segments manageable
    
    # Create segments
    start_markers = list(range(0, total_paths, segment_size))
    
    logger.info(f"Total valid paths: {total_paths}")
    logger.info(f"Number of segments: {len(start_markers)}")
    
    # Process segments in chunks to control concurrency
    for i in range(0, len(start_markers), max_concurrent):
        chunk = start_markers[i:i + max_concurrent]
        tasks = [run_segment(start, segment_size) for start in chunk]
        
        logger.info(f"Starting concurrent execution of segments {i//max_concurrent + 1}")
        await asyncio.gather(*tasks)
        logger.info(f"Completed batch of segments {i//max_concurrent + 1}")
        
        # Optional: Add delay between batches
        if i + max_concurrent < len(start_markers):
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        # Create datasets directory if it doesn't exist
        os.makedirs('datasets', exist_ok=True)
        
        logger.info("Starting concurrent segment processing")
        asyncio.run(run_segments_concurrently())
        logger.info("All segments completed")
        
    except KeyboardInterrupt:
        logger.info("\nProcess interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")