import asyncio
import logging
import os
import time
from datetime import datetime, timezone

import httpx
from config import Config
from data import add_result

logger = logging.getLogger(__name__)


async def check_urls(client: httpx.AsyncClient, config: Config, url: str):
    """Performs a single HTTP GET on a URL and stores the result.

    Uses streaming to avoid downloading the response body — only the status
    code is needed.

    Args:
        client: Shared httpx async client.
        config: Application configuration (timeout, etc.).
        url: The URL to check.
    """
    current_time = datetime.now(timezone.utc).isoformat()
    start = time.perf_counter()

    try:
        async with client.stream("GET", url, timeout=config.timeout) as r:
            status_code = str(r.status_code)
    except httpx.TimeoutException:
        status_code = "TIMEOUT"
    except httpx.RequestError:
        status_code = "CONNECTION_ERROR"
    except Exception as e:
        logger.error("Unexpected error checking %s: %s", url, e)
        status_code = "ERROR"

    elapsed_ms = (time.perf_counter() - start) * 1000
    add_result(url, current_time, elapsed_ms, status_code)


async def poll_urls(config: Config):
    """Polls all configured URLs concurrently on a fixed interval, indefinitely.

    The sleep duration accounts for the time spent polling to avoid temporal
    drift — the effective interval stays close to config.polling_interval.

    Args:
        config: Application configuration.
    """
    async with httpx.AsyncClient() as client:
        while True:
            cycle_start = asyncio.get_event_loop().time()
            await asyncio.gather(
                *[check_urls(client, config, url) for url in config.urls if url],
                return_exceptions=True,
            )
            elapsed = asyncio.get_event_loop().time() - cycle_start
            await asyncio.sleep(max(0, config.polling_interval - elapsed))


if __name__ == "__main__":
    config_path = os.getenv("CONFIG_PATH", "config.yaml")
    asyncio.run(poll_urls(Config(path=config_path)))
