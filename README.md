# Health Checker

A small service that periodically checks the health of a configurable list of URLs, stores the results in memory, and exposes them via a simple HTTP API.

## Architecture

```
.
├── .env
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── README.md
├── config.yaml
├── requirements.txt
└── python
    ├── app
    │   ├── api.py       # FastAPI app and /status endpoint
    │   ├── config.py    # YAML config loader
    │   ├── data.py      # In-memory result store
    │   └── worker.py    # Async polling worker
    └── tests
        ├── test_api.py
        ├── test_data.py
        └── test_worker.py
```

## Stack

| Component | Technology |
| -- | -- |
| Language | Python 3.13 |
| API | FastAPI + uvicorn |
| HTTP client | httpx (async) |
| Storage | `collections.deque` (own memory) |
| Tests | pytest + pytest-asyncio |

## Setup

### Local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env 
python python/app/api.py
```

### Docker Compose

```bash
cp .env.example .env
docker compose up
```

The `config.yaml` is mounted as a read-only volume, the URL list can be edited without rebuilding the image.


## Configuration
Edit `config.yaml` to set the URLs to monitor:

```yaml
urls:
  - https://example.com
  - https://httpbin.org/status/503

pollInterval: 60   # seconds between polls
timeout: 10        # seconds before a request is marked TIMEOUT
```

The config file path can be overridden via the `CONFIG_PATH` environment variable.

## API

### `GET /status`

Returns the latest check results for all monitored URLs.

```json
{
  "https://example.com": [
    {
      "timestamp": "2026-06-09T10:00:00.000000+00:00",
      "status_code": "200",
      "response_time_ms": 143.2
    }
  ]
}
```

`status_code` is the HTTP status code as a string, or `"TIMEOUT"` / `"CONNECTION_ERROR"` when the request fails.

## Tests

```bash
pytest python/tests -v
```

## Design Decisions

**asyncio + httpx** : All URLs are polled concurrently using `asyncio.gather`, so a slow or unresponsive URL does not delay the others. A single `httpx.AsyncClient` is shared across all checks for connection pooling.

**In-memory storage with `deque`** : Simple and dependency-free. The `deque(maxlen=100)` automatically evicts the oldest entries. Trade-off: results are lost on restart and do not scale across multiple instances. A persistent store (Redis, SQLite) would be the next step for production.

_NB: In a real case, I would use a TimeSeries DB like InfluxDB to store the info and read the data in a grafana or ELK dashboard._

**Worker as a background task** : The polling worker is launched as an `asyncio` task via FastAPI's `lifespan` hook. This avoids running a separate process and keeps the deployment as a single container.

**Config via YAML** : Human-readable, easy to edit, easy to add different links for differents module and best practise as I learnd. The path is overridable via `CONFIG_PATH` for container deployments where the file location may differ.

## Trade-offs

| Decision | Trade-off |
|---|---|
| In-memory store | No persistence across restarts |
| Single process | Cannot scale horizontally without shared state |
| No auth on `/status` | Acceptable for internal use, would need protection in prod (With APIKEY or a JWT Tokken)|
| Config loaded once at startup | URL list changes require a restart |
