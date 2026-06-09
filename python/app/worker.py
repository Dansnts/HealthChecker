import asyncio
import os
import time
from datetime import datetime, timezone

import httpx
from config import Config
from data import add_result


async def check_urls(client: httpx.AsyncClient, config: Config, url: str):
    """Performs a single HTTP GET on a URL and stores the result.

    Args:
        client: Shared httpx async client.
        config: Application configuration (timeout, etc.).
        url: The URL to check.
    """
    current_time = datetime.now(timezone.utc).isoformat()

    start = time.perf_counter()

    try:
        r = await client.get(url, timeout=config.timeout)  # Default timeout : 10s
        status_code = str(r.status_code)
    except httpx.TimeoutException:
        status_code = "TIMEOUT"
    except httpx.RequestError:
        status_code = "CONNECTION_ERROR"

    end = time.perf_counter()

    elapsed_ms = (end - start) * 1000  # in ms
    add_result(url, current_time, elapsed_ms, status_code)


async def poll_urls():
    """Polls all configured URLs concurrently on a fixed interval, indefinitely."""
    config_path = os.getenv("CONFIG_PATH", "config.yaml")
    config = Config(path=config_path)

    async with httpx.AsyncClient() as client:
        while True:
            await asyncio.gather(
                *[check_urls(client, config, url) for url in config.urls if url]
            )
            await asyncio.sleep(config.polling_interval)


if __name__ == "__main__":
    asyncio.run(poll_urls())
