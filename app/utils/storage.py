"""Repository storage and configuration management."""

import json
from typing import Any, Optional

from app.core.config import settings
from app.core.logger import logger


class RepositoryStorage:
    """Manages repos.json configuration."""

    @staticmethod
    def load_repos() -> dict[str, Any]:
        """Load repositories from config/repos.json."""
        if not settings.config_repos_path.exists():
            logger.info("repos.json not found, returning empty dict")
            return {}

        try:
            with open(settings.config_repos_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading repos.json: {e}")
            return {}

    @staticmethod
    def save_repos(repos: dict[str, Any]) -> bool:
        """Save repositories to config/repos.json."""
        settings.config_repos_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(settings.config_repos_path, "w") as f:
                json.dump(repos, f, indent=2)
            logger.debug("repos.json saved")
            return True
        except Exception as e:
            logger.error(f"Error saving repos.json: {e}")
            return False

    @staticmethod
    def add_repo(name: str, remote_path: str) -> bool:
        """Add or update a repository in repos.json."""
        repos = RepositoryStorage.load_repos()
        repos[name] = {"remote_path": remote_path, "last_opened": None}
        return RepositoryStorage.save_repos(repos)

    @staticmethod
    def get_repo(name: str) -> Optional[dict[str, Any]]:
        """Get repository configuration."""
        repos = RepositoryStorage.load_repos()
        return repos.get(name)

    @staticmethod
    def list_repos() -> dict[str, Any]:
        """List all repositories."""
        return RepositoryStorage.load_repos()

    @staticmethod
    def delete_repo(name: str) -> bool:
        """Remove a repository from repos.json."""
        repos = RepositoryStorage.load_repos()
        if name in repos:
            del repos[name]
            return RepositoryStorage.save_repos(repos)
        return False
