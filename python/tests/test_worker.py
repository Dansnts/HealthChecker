import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock

from worker import check_urls
from data import store


def make_config(timeout=10):
    config = MagicMock()
    config.timeout = timeout
    return config


def make_stream_client(status_code=200):
    """Creates a mock httpx client that mimics client.stream() context manager."""
    mock_response = MagicMock()
    mock_response.status_code = status_code

    mock_stream = AsyncMock()
    mock_stream.__aenter__ = AsyncMock(return_value=mock_response)
    mock_stream.__aexit__ = AsyncMock(return_value=False)

    mock_client = MagicMock()
    mock_client.stream = MagicMock(return_value=mock_stream)
    return mock_client


@pytest.mark.asyncio
async def test_check_urls_records_status_code():
    await check_urls(make_stream_client(200), make_config(), "https://example.com")

    assert store["https://example.com"][-1]["status_code"] == "200"


@pytest.mark.asyncio
async def test_check_urls_handles_timeout():
    mock_client = MagicMock()
    mock_stream = AsyncMock()
    mock_stream.__aenter__ = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
    mock_stream.__aexit__ = AsyncMock(return_value=False)
    mock_client.stream = MagicMock(return_value=mock_stream)

    await check_urls(mock_client, make_config(), "https://example.com")

    assert store["https://example.com"][-1]["status_code"] == "TIMEOUT"


@pytest.mark.asyncio
async def test_check_urls_handles_connection_error():
    mock_client = MagicMock()
    mock_stream = AsyncMock()
    mock_stream.__aenter__ = AsyncMock(side_effect=httpx.RequestError("error"))
    mock_stream.__aexit__ = AsyncMock(return_value=False)
    mock_client.stream = MagicMock(return_value=mock_stream)

    await check_urls(mock_client, make_config(), "https://example.com")

    assert store["https://example.com"][-1]["status_code"] == "CONNECTION_ERROR"
