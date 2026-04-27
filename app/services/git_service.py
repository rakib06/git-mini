"""Git repository operations service."""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from git import Repo, GitCommandError

from app.core.config import settings
from app.core.logger import logger
from app.utils.path_security import (
    sanitize_repo_name,
    validate_repo_path,
    validate_temp_local_path,
    ensure_temp_local_dir,
)
from app.utils.storage import RepositoryStorage


class GitService:
    """Handle all Git operations."""

    @staticmethod
    def is_bare_repo(path: Path) -> bool:
        """Check if path is a bare Git repository."""
        try:
            repo = Repo(str(path), odor_detect_unfinished_transaction=False)
            return repo.bare
        except Exception:
            return False

    @staticmethod
    def clone_or_fetch(remote_path: str, repo_name: str) -> Optional[Path]:
        """
        Clone repository from remote if not exists, or fetch+pull if exists.

        Args:
            remote_path: Path to bare repository on LAN share
            repo_name: Local repository name

        Returns:
            Path to local cloned repository, or None on error
        """
        # Validate paths
        validated_remote = validate_repo_path(remote_path)
        if not validated_remote:
            logger.error(f"Remote path validation failed: {remote_path}")
            return None

        temp_repo_path = validate_temp_local_path(repo_name)
        if not temp_repo_path:
            logger.error(f"Temp path validation failed: {repo_name}")
            return None

        ensure_temp_local_dir()

        try:
            if temp_repo_path.exists():
                # Fetch and pull
                logger.info(f"Fetching and pulling repo: {repo_name}")
                repo = Repo(str(temp_repo_path))

                # Fetch all remotes
                for remote in repo.remotes:
                    remote.fetch()

                # Pull on current branch
                if repo.head.is_detached:
                    logger.warning(f"Repository is in detached HEAD state: {repo_name}")
                else:
                    active_branch = repo.active_branch
                    active_branch.set_tracking_branch(f"origin/{active_branch.name}")
                    try:
                        active_branch.repo.remotes.origin.pull()
                    except GitCommandError as e:
                        logger.warning(f"Pull failed for {repo_name}: {e}")

                logger.info(f"Repository updated: {repo_name}")
            else:
                # Clone
                logger.info(f"Cloning repository: {remote_path} -> {temp_repo_path}")
                Repo.clone_from(str(validated_remote), str(temp_repo_path))
                logger.info(f"Repository cloned: {repo_name}")

            return temp_repo_path

        except Exception as e:
            logger.error(f"Clone/fetch error for {repo_name}: {e}")
            return None

    @staticmethod
    def get_branches(repo_path: Path) -> list[dict[str, str]]:
        """Get list of branches in repository."""
        try:
            repo = Repo(str(repo_path))
            branches = []

            for ref in repo.refs:
                if hasattr(ref, "name"):
                    is_current = (
                        ref == repo.active_branch
                        if not repo.head.is_detached
                        else False
                    )
                    branches.append(
                        {
                            "name": ref.name,
                            "commit": ref.commit.hexsha[:7],
                            "is_current": is_current,
                        }
                    )

            return branches
        except Exception as e:
            logger.error(f"Error getting branches: {e}")
            return []

    @staticmethod
    def get_commits(
        repo_path: Path, branch: Optional[str] = None, max_count: int = 50
    ) -> list[dict]:
        """Get commits from repository."""
        try:
            repo = Repo(str(repo_path))
            commits = []

            if branch:
                iter_source = repo.iter_commits(branch, max_count=max_count)
            else:
                iter_source = repo.iter_commits(max_count=max_count)

            for commit in iter_source:
                commits.append(
                    {
                        "sha": commit.hexsha[:7],
                        "full_sha": commit.hexsha,
                        "author": commit.author.name,
                        "email": commit.author.email,
                        "message": commit.message.strip(),
                        "timestamp": datetime.fromtimestamp(
                            commit.committed_date
                        ).isoformat(),
                        "parent_shas": [p.hexsha[:7] for p in commit.parents],
                    }
                )

            return commits
        except Exception as e:
            logger.error(f"Error getting commits: {e}")
            return []

    @staticmethod
    def get_status(repo_path: Path) -> dict:
        """Get repository status."""
        try:
            repo = Repo(str(repo_path))

            status_dict = {
                "branch": (
                    repo.active_branch.name if not repo.head.is_detached else "detached"
                ),
                "is_dirty": repo.is_dirty(),
                "untracked_files": repo.untracked_files,
                "staged": [],
                "unstaged": [],
            }

            # Get staged and unstaged changes
            for item in repo.index.diff("HEAD"):
                status_dict["staged"].append(item.a_path)

            for item in repo.index.diff(None):
                status_dict["unstaged"].append(item.a_path)

            return status_dict
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {}

    @staticmethod
    def get_diff(repo_path: Path, commit_sha: str, parent_index: int = 0) -> str:
        """Get diff for a commit."""
        try:
            repo = Repo(str(repo_path))
            commit = repo.commit(commit_sha)

            if not commit.parents:
                # First commit - diff against empty tree
                diffs = commit.tree.diff(None)
            else:
                parent = (
                    commit.parents[parent_index]
                    if parent_index < len(commit.parents)
                    else commit.parents[0]
                )
                diffs = parent.tree.diff(commit.tree)

            diff_text = ""
            for diff in diffs:
                diff_text += f"diff --git a/{diff.a_path} b/{diff.b_path}\n"
                if diff.change_type == "A":
                    diff_text += "new file mode 100644\n"
                elif diff.change_type == "D":
                    diff_text += "deleted file mode 100644\n"
                diff_text += f"index {diff.a_blob.hexsha[:7]}..{diff.b_blob.hexsha[:7] if diff.b_blob else '0000000'}\n"

                if diff.diff:
                    diff_text += diff.diff.decode("utf-8", errors="ignore")

            return diff_text
        except Exception as e:
            logger.error(f"Error getting diff: {e}")
            return ""

    @staticmethod
    def push_changes(repo_path: Path, branch: str = "main") -> bool:
        """Push changes to remote repository."""
        try:
            repo = Repo(str(repo_path))
            remote = repo.remote("origin")
            remote.push(branch)
            logger.info(f"Pushed changes to {branch}")
            return True
        except Exception as e:
            logger.error(f"Push error: {e}")
            return False

    @staticmethod
    def stage_all(repo_path: Path) -> bool:
        """Stage all changes."""
        try:
            repo = Repo(str(repo_path))
            repo.git.add(A=True)
            logger.info("All changes staged")
            return True
        except Exception as e:
            logger.error(f"Stage error: {e}")
            return False

    @staticmethod
    def commit(
        repo_path: Path,
        message: str,
        author_name: str = "User",
        author_email: str = "user@local",
    ) -> bool:
        """Create a commit."""
        try:
            repo = Repo(str(repo_path))
            repo.index.commit(
                message, author_name=author_name, author_email=author_email
            )
            logger.info(f"Committed with message: {message}")
            return True
        except Exception as e:
            logger.error(f"Commit error: {e}")
            return False

    @staticmethod
    def create_bare_repo(repo_name: str) -> dict:
        """Create a new bare repository on LAN share.

        1. Sanitize name
        2. Ensure .git suffix
        3. Build full LAN path from settings.allowed_paths[0]
        4. If exists -> error
        5. git init --bare full_path (no shell)
        6. Save repo metadata
        7. Return success message

        Args:
            repo_name: Repository name to create

        Returns:
            Dict with status, name, and remote_path
        """
        # 1. Sanitize name
        clean_name = sanitize_repo_name(repo_name)
        if not clean_name:
            return {"status": "error", "message": f"Invalid repository name: '{repo_name}'"}

        # 2. Ensure .git suffix
        if clean_name.endswith(".git"):
            bare_name = clean_name
        else:
            bare_name = f"{clean_name}.git"

        # 3. Build full LAN path from settings.allowed_paths[0]
        if not settings.allowed_paths:
            return {
                "status": "error",
                "message": "No allowed LAN paths configured in settings.json",
            }

        base_lan_path = Path(settings.allowed_paths[0])
        full_path = base_lan_path / bare_name

        # 4. If exists -> error
        if full_path.exists():
            return {
                "status": "error",
                "message": f"Repository already exists at {full_path}",
            }

        # Ensure parent directory exists (Windows UNC safe via pathlib)
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create parent directory: {e}")
            return {
                "status": "error",
                "message": f"Failed to create parent directory: {e}",
            }

        # 5. git init --bare full_path (no shell=True)
        try:
            logger.info(f"Creating bare repo at: {full_path}")
            subprocess.run(
                ["git", "init", "--bare", str(full_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            logger.info(f"Bare repo created: {full_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"git init --bare failed: {e.stderr}")
            return {"status": "error", "message": f"git init failed: {e.stderr}"}
        except FileNotFoundError:
            logger.error("git executable not found")
            return {"status": "error", "message": "Git executable not found"}

        # 6. Save repo metadata (use the name without .git as key)
        repo_key = clean_name.removesuffix(".git")
        remote_path_str = str(full_path)

        try:
            RepositoryStorage.add_repo(repo_key, remote_path_str)
            logger.info(f"Repo metadata saved: {repo_key} -> {remote_path_str}")
        except Exception as e:
            logger.error(f"Failed to save repo metadata: {e}")
            # Repo was created but metadata not saved — still report success but warn
            return {
                "status": "warning",
                "message": f"Bare repo created but metadata save failed",
                "name": repo_key,
                "remote_path": remote_path_str,
            }

        # 7. Return success message
        return {
            "status": "success",
            "message": f"Bare repository '{repo_key}' created on LAN",
            "name": repo_key,
            "remote_path": remote_path_str,
        }

    @staticmethod
    def list_repos() -> list[dict]:
        """List all registered repositories from storage.

        Returns:
            List of repository configurations
        """
        try:
            repos = RepositoryStorage.list_repos()
            result = []
            for name, config in repos.items():
                temp_path = validate_temp_local_path(name)
                is_cloned = temp_path and temp_path.exists()
                result.append(
                    {
                        "name": name,
                        "remote_path": config.get("remote_path"),
                        "is_cloned": is_cloned,
                        "last_opened": config.get("last_opened"),
                    }
                )
            return result
        except Exception as e:
            logger.error(f"Error listing repos: {e}")
            return []

    @staticmethod
    def ensure_local_clone(repo_name: str) -> Optional[Path]:
        """Ensure repository exists locally, clone if needed.

        Args:
            repo_name: Repository name

        Returns:
            Path to local clone, or None if failed
        """
        repo_config = RepositoryStorage.get_repo(repo_name)
        if not repo_config:
            logger.error(f"Repository not found: {repo_name}")
            return None

        return GitService.clone_or_fetch(repo_config["remote_path"], repo_name)

    @staticmethod
    def clone_from_lan(repo_name: str) -> Optional[Path]:
        """Clone a repository from LAN share to temp_local.

        Args:
            repo_name: Repository name to clone

        Returns:
            Path to cloned repository, or None on error
        """
        repo_config = RepositoryStorage.get_repo(repo_name)
        if not repo_config:
            logger.error(f"Repository config not found: {repo_name}")
            return None

        remote_path = repo_config["remote_path"]
        temp_repo_path = validate_temp_local_path(repo_name)

        if not temp_repo_path:
            logger.error(f"Invalid temp path for: {repo_name}")
            return None

        if temp_repo_path.exists():
            logger.info(f"Repository already cloned: {repo_name}")
            return temp_repo_path

        validated_remote = validate_repo_path(remote_path)
        if not validated_remote:
            logger.error(f"Remote path validation failed: {remote_path}")
            return None

        try:
            ensure_temp_local_dir()
            logger.info(f"Cloning: {remote_path} -> {temp_repo_path}")
            Repo.clone_from(str(validated_remote), str(temp_repo_path))
            logger.info(f"Clone successful: {repo_name}")
            return temp_repo_path
        except Exception as e:
            logger.error(f"Clone error: {e}")
            return None

    @staticmethod
    def sync_repo(repo_name: str) -> bool:
        """Sync repository (fetch + pull).

        Args:
            repo_name: Repository name

        Returns:
            True if successful, False otherwise
        """
        temp_repo_path = validate_temp_local_path(repo_name)
        if not temp_repo_path or not temp_repo_path.exists():
            logger.error(f"Repository not cloned: {repo_name}")
            return False

        try:
            logger.info(f"Syncing repository: {repo_name}")
            repo = Repo(str(temp_repo_path))

            # Fetch all remotes
            for remote in repo.remotes:
                logger.debug(f"Fetching from: {remote.name}")
                remote.fetch()

            # Pull on current branch
            if repo.head.is_detached:
                logger.warning(f"Repository in detached HEAD state: {repo_name}")
            else:
                active_branch = repo.active_branch
                active_branch.set_tracking_branch(f"origin/{active_branch.name}")
                try:
                    active_branch.repo.remotes.origin.pull()
                    logger.info(f"Pulled latest from {active_branch.name}")
                except GitCommandError as e:
                    logger.warning(f"Pull failed: {e}")
                    return False

            logger.info(f"Repository synced: {repo_name}")
            return True
        except Exception as e:
            logger.error(f"Sync error: {e}")
            return False

    @staticmethod
    def delete_local_clone(repo_name: str) -> bool:
        """Delete local clone from temp_local.

        Args:
            repo_name: Repository name

        Returns:
            True if successful, False otherwise
        """
        import shutil

        temp_repo_path = validate_temp_local_path(repo_name)
        if not temp_repo_path:
            logger.error(f"Invalid temp path: {repo_name}")
            return False

        if not temp_repo_path.exists():
            logger.info(f"Repository not found locally: {repo_name}")
            return True

        try:
            logger.info(f"Deleting local clone: {temp_repo_path}")
            shutil.rmtree(str(temp_repo_path))
            logger.info(f"Local clone deleted: {repo_name}")
            return True
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return False
