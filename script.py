import aiohttp
import json
import asyncio
from typing import List, Dict
import time
from aiohttp import ClientTimeout
from datetime import datetime
from tqdm.asyncio import tqdm_asyncio

class TTSBulkTranslator:
    def __init__(self,url , batch_size: int = 50, rate_limit: int = 10, total_requests: int = 10000):
        self.url = url
        self.batch_size = batch_size
        self.rate_limit = rate_limit
        self.total_requests = total_requests
        self.timeout = ClientTimeout(total=30)
        self.results: List[Dict] = []
        self.errors: List[Dict] = []
        
    async def translate_single(self, session: aiohttp.ClientSession, index: int) -> Dict:
        payload = json.dumps({
            "text": "bienvenu sur LAfricamobil",
            "to_lang": "wolof"
        })
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJyb2xlIjoic3VwZXJfYWRtaW4iLCJleHAiOjE3NDUzNDcwMTZ9.ZFBD-r4YW7BQC6yjIc6_34vt3de3G7F6wcmMSdSm27w'
        }

        try:
            async with session.post(self.url, headers=headers, data=payload, timeout=self.timeout) as response:
                response_data = await response.json()
                return {
                    "index": index,
                    "status": response.status,
                    "data": response_data,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "index": index,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def process_batch(self, session: aiohttp.ClientSession, start_idx: int, progress_bar) -> None:
        end_idx = min(start_idx + self.batch_size, self.total_requests)
        tasks = []
        
        for i in range(start_idx, end_idx):
            # Add delay to respect rate limit
            await asyncio.sleep(1 / self.rate_limit)
            task = asyncio.create_task(self.translate_single(session, i))
            tasks.append(task)
        
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in batch_results:
            if isinstance(result, Exception):
                self.errors.append({
                    "error": str(result),
                    "timestamp": datetime.now().isoformat()
                })
            elif result.get("status") == "error":
                self.errors.append(result)
            else:
                self.results.append(result)
            progress_bar.update(1)

    async def run_all_requests(self):
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            # Use tqdm for progress tracking
            with tqdm_asyncio(total=self.total_requests, desc="Translation Progress", unit="request") as progress_bar:
                batches = range(0, self.total_requests, self.batch_size)
                for start_idx in batches:
                    await self.process_batch(session, start_idx, progress_bar)
        
        end_time = time.time()
        return {
            "total_time": end_time - start_time,
            "successful_requests": len(self.results),
            "failed_requests": len(self.errors),
            "results": self.results,
            "errors": self.errors
        }

async def main():
    # Initialize with configurable parameters
    translator = TTSBulkTranslator(
        url= "https://devtts.lafricamobile.com/tts/translate", #url to test
        batch_size=10,  # Number of requests per batch
        rate_limit=5,    # Requests per second
        total_requests=100  # Total number of requests to make
    )
    
    print("Starting bulk translation...")
    results = await translator.run_all_requests()
    
    print("\nSummary:")
    print(f"Total time: {results['total_time']:.2f} seconds")
    print(f"Successful requests: {results['successful_requests']}")
    print(f"Failed requests: {results['failed_requests']}")
    
    # Save results to files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f'successful_requests_{timestamp}.json', 'w') as f:
        json.dump(results['results'], f, indent=2)
    
    if results['errors']:
        with open(f'failed_requests_{timestamp}.json', 'w') as f:
            json.dump(results['errors'], f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())