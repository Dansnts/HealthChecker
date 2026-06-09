import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock

from worker import check_urls
from data import store


def make_config(timeout=10):
    config = MagicMock()
    config.timeout = timeout
    return config


@pytest.mark.asyncio
async def test_check_urls_records_status_code():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    await check_urls(mock_client, make_config(), "https://example.com")

    assert store["https://example.com"][-1]["status_code"] == "200"


@pytest.mark.asyncio
async def test_check_urls_handles_timeout():
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("timeout"))

    await check_urls(mock_client, make_config(), "https://example.com")

    assert store["https://example.com"][-1]["status_code"] == "TIMEOUT"


@pytest.mark.asyncio
async def test_check_urls_handles_connection_error():
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=httpx.RequestError("error"))

    await check_urls(mock_client, make_config(), "https://example.com")

    assert store["https://example.com"][-1]["status_code"] == "CONNECTION_ERROR"
