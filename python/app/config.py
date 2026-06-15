import logging
from urllib.parse import urlparse

import yaml
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Loads and exposes the application configuration from a YAML file."""

    def __init__(self, path: str = "config.yaml"):
        """Initializes Config by parsing a YAML file.

        Args:
            path: Path to the YAML configuration file.

        Raises:
            ValueError: If the YAML file cannot be parsed.
        """
        with open(path) as stream:
            try:
                data = yaml.safe_load(stream) or {}
            except yaml.YAMLError as e:
                raise ValueError(f"Error while loading yaml file: {e}")

        self.urls = self._validate_urls(data.get("urls") or [])
        self.polling_interval = data.get("pollInterval", 60)
        self.timeout = data.get("timeout", 10)

    @staticmethod
    def _validate_urls(urls: list) -> list[str]:
        """Filters out non-string and non-HTTP(S) entries from the URL list."""
        valid = []
        for url in urls:
            if not isinstance(url, str):
                logger.warning("Skipping non-string URL entry: %s", url)
                continue
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                logger.warning("Skipping invalid URL: %s", url)
                continue
            valid.append(url)
        return valid
