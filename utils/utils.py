# To rate limit the requests to the API

import asyncio
import time

class RateLimiter:
    def __init__(self, max_requests_per_minute: int = 30000):
        self.max_requests_per_minute = max_requests_per_minute
        self.requests = []
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            current_time = time.time()
            # Remove requests older than 1 minute
            self.requests = [req_time for req_time in self.requests 
                           if current_time - req_time < 60]
            
            if len(self.requests) >= self.max_requests_per_minute:
                # Wait until we can make another request
                await asyncio.sleep(0.1)
                return await self.acquire()
            
            self.requests.append(current_time)

rate_limiter = RateLimiter()