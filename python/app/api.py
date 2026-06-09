import asyncio
import os
from contextlib import asynccontextmanager

import uvicorn
from data import get_result
from fastapi import FastAPI
from worker import poll_urls


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Starts the polling worker on startup and cancels it on shutdown."""
    task = asyncio.create_task(poll_urls())
    task.add_done_callback(
        lambda t: (
            print("WORKER ERROR:", t.exception())
            if not t.cancelled() and t.exception()
            else None
        )
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
        host=str(os.getenv("V4_ADDRESS", "0.0.0.0")),
        port=int(os.getenv("PORT", 8080)),
    )
