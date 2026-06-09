from collections import deque

store: dict[str, deque] = {}


def add_result(url: str, timestamp: str, response_time: float, status_code: str):
    """Appends a check result to the in-memory store for a given URL.

    Args:
        url: The URL that was checked.
        timestamp: ISO 8601 UTC timestamp of the check.
        response_time: Response time in milliseconds.
        status_code: HTTP status code, or "TIMEOUT" / "CONNECTION_ERROR" on failure.
    """
    if url not in store:
        store[url] = deque(maxlen=100)

    store[url].append(
        {
            "timestamp": timestamp,
            "status_code": status_code,
            "response_time_ms": response_time,
        }
    )


def get_result() -> dict:
    """Returns all stored check results grouped by URL.

    Returns:
        A dict mapping each URL to a list of its check results.
    """
    return {url: list(results) for url, results in store.items()}
