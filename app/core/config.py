"""Application configuration management."""

import json
from pathlib import Path


class Settings:
    """Application settings from config/settings.json."""

    def __init__(self) -> None:
        """Load settings from config file."""
        config_path = Path(__file__).parent.parent.parent / "config" / "settings.json"

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path) as f:
            config = json.load(f)

        self.host: str = config.get("host", "127.0.0.1")
        self.port: int = config.get("port", 8000)
        self.allowed_paths: list[str] = config.get("allowed_paths", [])
        self.temp_local_dir: str = config.get("temp_local_dir", "temp_local")

        # Set up full paths
        self.base_dir = Path(__file__).parent.parent.parent
        self.temp_local_path = self.base_dir / self.temp_local_dir
        self.logs_dir = self.base_dir / "logs"
        self.config_repos_path = self.base_dir / "config" / "repos.json"

    def validate(self) -> bool:
        """Validate configuration."""
        if not self.host:
            raise ValueError("host is required in settings.json")
        if self.port <= 0 or self.port > 65535:
            raise ValueError(f"port must be between 1 and 65535, got {self.port}")
        if not self.allowed_paths:
            raise ValueError("allowed_paths must not be empty in settings.json")
        return True


# Global settings instance
settings = Settings()
