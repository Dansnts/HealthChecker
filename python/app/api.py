import asyncio
import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from config import Config
from data import get_result
from fastapi import FastAPI
from worker import poll_urls

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Loads config and starts the polling worker on startup, cancels it on shutdown."""
    config_path = os.getenv("CONFIG_PATH", "config.yaml")
    config = Config(path=config_path)

    task = asyncio.create_task(poll_urls(config))
    task.add_done_callback(
        lambda t: logger.error("Worker stopped unexpectedly: %s", t.exception())
        if not t.cancelled() and t.exception()
        else None
    )
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)


@app.get("/status")
async def get_status():
    """Returns the latest health check results for all monitored URLs.

    Returns:
        A dict mapping each URL to a list of its recent check results.
    """
    return get_result()


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.getenv("V4_ADDRESS", "0.0.0.0"),
        port=int(os.getenv("PORT", 8080)),
    )
