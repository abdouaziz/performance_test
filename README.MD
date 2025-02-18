# TTS Bulk Translator

## Overview
The `TTSBulkTranslator` is an asynchronous Python script that sends bulk requests to a Text-to-Speech (TTS) API for translation. It allows configuring batch sizes, rate limits, and the total number of requests to process efficiently while handling errors gracefully.

## Features
- Sends multiple translation requests in batches.
- Implements a rate limit to prevent excessive API calls.
- Uses `asyncio` and `aiohttp` for efficient asynchronous requests.
- Tracks progress using `tqdm.asyncio`.
- Logs successful and failed requests to JSON files.

## Installation

Ensure you have Python 3.7 or higher installed. Then, install the required dependencies:

```bash
pip install aiohttp tqdm
```

## Usage

Run the script using:

```bash
python script.py
```

## Configuration

The script allows customization of the following parameters:

- **`url`**: API endpoint for TTS translation.
- **`batch_size`**: Number of concurrent requests sent per batch.
- **`rate_limit`**: Maximum number of requests per second.
- **`total_requests`**: Total number of requests to be sent.

Modify the `main()` function to adjust these settings:

```python
translator = TTSBulkTranslator(
    url="https://devtts.lafricamobile.com/tts/translate",
    batch_size=10,  # Number of requests per batch
    rate_limit=5,    # Requests per second
    total_requests=100  # Total number of requests to make
)
```

## Expected Output
The script will display a progress bar while processing requests. Once completed, a summary report is printed:

```
Starting bulk translation...
Translation Progress: 100%|█████████| 100/100 [00:20<00:00, 5.00 requests/s]

Summary:
Total time: 20.00 seconds
Successful requests: 95
Failed requests: 5
```

## Output Files
The script saves results as JSON files:

- `successful_requests_<timestamp>.json`: Contains successful translations.
- `failed_requests_<timestamp>.json`: Logs failed requests with error details.

## Error Handling
Errors are captured and logged in the `errors` list. The script retries within the batch execution, but persistent failures are recorded separately.
