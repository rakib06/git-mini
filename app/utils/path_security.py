"""Path security and validation utilities."""

from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.logger import logger


def validate_repo_path(repo_path: str) -> Optional[Path]:
    """
    Validate that repo_path is within allowed_paths.

    Prevents directory traversal attacks.

    Args:
        repo_path: Path to validate (can be relative or absolute)

    Returns:
        Resolved Path if valid, None if invalid
    """
    try:
        # Resolve the path to absolute form
        requested = Path(repo_path).resolve()

        # Check against allowed paths
        for allowed in settings.allowed_paths:
            allowed_path = Path(allowed).resolve()
            try:
                # This will raise ValueError if requested is not relative to allowed_path
                requested.relative_to(allowed_path)
                logger.debug(f"Path validation passed: {requested}")
                return requested
            except ValueError:
                continue

        logger.warning(f"Path validation failed: {requested} not in allowed paths")
        return None

    except Exception as e:
        logger.error(f"Path validation error: {e}")
        return None


def validate_temp_local_path(repo_name: str) -> Optional[Path]:
    """
    Validate and get temp_local path for a repository.

    Args:
        repo_name: Repository name (must be a simple name without path separators)

    Returns:
        Path to temp_local repository if valid, None otherwise
    """
    # Prevent directory traversal in repo name
    if "/" in repo_name or "\\" in repo_name or repo_name.startswith("."):
        logger.warning(f"Invalid repo name: {repo_name}")
        return None

    temp_repo_path = settings.temp_local_path / repo_name

    try:
        # Ensure it's within temp_local_dir
        temp_repo_path.resolve().relative_to(settings.temp_local_path.resolve())
        logger.debug(f"Temp local path validation passed: {temp_repo_path}")
        return temp_repo_path
    except ValueError:
        logger.warning(f"Temp local path validation failed: {temp_repo_path}")
        return None


def ensure_temp_local_dir() -> Path:
    """Ensure temp_local directory exists."""
    settings.temp_local_path.mkdir(parents=True, exist_ok=True)
    return settings.temp_local_path


def sanitize_repo_name(name: str) -> Optional[str]:
    """
    Sanitize repository name to prevent traversal attacks.

    Args:
        name: Repository name to sanitize

    Returns:
        Sanitized name if valid, None if invalid
    """
    if not name or not isinstance(name, str):
        logger.warning("Invalid repo name type")
        return None

    # Remove/block dangerous patterns
    dangerous_patterns = ["/", "\\", "..", ":", "*", "?", '"', "<", ">", "|"]
    for pattern in dangerous_patterns:
        if pattern in name:
            logger.warning(f"Dangerous pattern in repo name: {name}")
            return None

    # Block names starting with dot
    if name.startswith("."):
        logger.warning(f"Repo name cannot start with dot: {name}")
        return None

    # Trim whitespace
    name = name.strip()

    if len(name) < 1 or len(name) > 255:
        logger.warning(f"Repo name length invalid: {len(name)}")
        return None

    logger.debug(f"Repo name sanitized: {name}")
    return name


def validate_branch_name(name: str) -> bool:
    """
    Validate branch name for safety.

    Args:
        name: Branch name to validate

    Returns:
        True if valid, False otherwise
    """
    if not name or not isinstance(name, str):
        logger.warning("Invalid branch name type")
        return False

    # Git branch names can contain most characters, but we restrict for safety
    dangerous_patterns = ["..", "~", "^", ":", "?", "*", "[", "@{", "//"]
    for pattern in dangerous_patterns:
        if pattern in name:
            logger.warning(f"Dangerous pattern in branch name: {name}")
            return False

    # Block control refs
    if name in ["HEAD", "FETCH_HEAD", "MERGE_HEAD", "CHERRY_PICK_HEAD"]:
        logger.warning(f"Cannot use reserved branch name: {name}")
        return False

    if len(name) < 1 or len(name) > 255:
        logger.warning(f"Branch name length invalid: {len(name)}")
        return False

    logger.debug(f"Branch name validated: {name}")
    return True
