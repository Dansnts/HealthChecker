import yaml
from dotenv import load_dotenv

load_dotenv()


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
                data = yaml.safe_load(stream)
            except yaml.YAMLError as e:
                raise ValueError(f"Error while loading yaml file: {e}")

        self.urls = data.get("urls", [])
        self.polling_interval = data.get("pollInterval", 60)
        self.timeout = data.get("timeout", 10)
