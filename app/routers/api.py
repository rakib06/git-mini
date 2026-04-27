"""API routes for JSON endpoints."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.core.logger import logger
from app.services.git_service import GitService
from app.utils.path_security import validate_repo_path, validate_temp_local_path
from app.utils.storage import RepositoryStorage

router = APIRouter(tags=["api"])


# Request/Response Models
class RepoAddRequest(BaseModel):
    """Request to add a repository."""

    name: str
    remote_path: str


class CommitRequest(BaseModel):
    """Request to create a commit."""

    message: str
    author_name: str = "User"
    author_email: str = "user@local"


class PushRequest(BaseModel):
    """Request to push changes."""

    branch: str = "main"


class CreateBareRepoRequest(BaseModel):
    """Request to create a bare repository."""

    name: str
    initialize_with_readme: bool = False


class LinkLocalRepoRequest(BaseModel):
    """Request to link an existing local repository to LAN."""

    repo_name: str
    local_path: str


@router.get("/repositories")
async def list_repositories() -> dict:
    """List all registered repositories."""
    try:
        repos = RepositoryStorage.list_repos()
        return {"repositories": repos, "count": len(repos)}
    except Exception as e:
        logger.error(f"Error listing repos: {e}")
        raise HTTPException(status_code=500, detail="Failed to list repositories")


@router.post("/repositories")
async def add_repository(req: RepoAddRequest) -> dict:
    """Register a new repository."""
    if not req.name or not req.remote_path:
        raise HTTPException(status_code=400, detail="name and remote_path are required")

    # Validate remote path
    validated = validate_repo_path(req.remote_path)
    if not validated:
        raise HTTPException(status_code=400, detail="Invalid remote_path")

    try:
        if RepositoryStorage.add_repo(req.name, str(validated)):
            return {"status": "success", "message": f"Repository '{req.name}' added"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save repository")
    except Exception as e:
        logger.error(f"Error adding repo: {e}")
        raise HTTPException(status_code=500, detail="Failed to add repository")


@router.post("/repositories/create-bare")
async def create_bare_repository(req: CreateBareRepoRequest) -> dict:
    """Create a new bare repository on LAN share."""
    if not req.name:
        raise HTTPException(status_code=400, detail="name is required")

    result = GitService.create_bare_repo(req.name, req.initialize_with_readme)

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    elif result["status"] == "warning":
        return result
    else:
        return result


@router.post("/repositories/link-local")
async def link_local_repository(req: LinkLocalRepoRequest) -> dict:
    """Link an existing local repository to a LAN bare remote."""
    if not req.repo_name or not req.local_path:
        raise HTTPException(status_code=400, detail="repo_name and local_path are required")

    repo_config = RepositoryStorage.get_repo(req.repo_name)
    if not repo_config:
        raise HTTPException(status_code=404, detail="Repository not found")

    result = GitService.link_local_repo(req.local_path, repo_config["remote_path"])

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.delete("/repositories/{repo_name}")
async def delete_repository(repo_name: str) -> dict:
    """Delete a registered repository."""
    try:
        if RepositoryStorage.delete_repo(repo_name):
            return {"status": "success", "message": f"Repository '{repo_name}' deleted"}
        else:
            raise HTTPException(status_code=404, detail="Repository not found")
    except Exception as e:
        logger.error(f"Error deleting repo: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete repository")


@router.post("/repositories/{repo_name}/clone-or-fetch")
async def clone_or_fetch_repository(repo_name: str) -> dict:
    """Clone repository from remote or fetch+pull if exists."""
    repo_config = RepositoryStorage.get_repo(repo_name)
    if not repo_config:
        raise HTTPException(status_code=404, detail="Repository not found")

    try:
        repo_path = GitService.clone_or_fetch(repo_config["remote_path"], repo_name)
        if repo_path:
            return {"status": "success", "path": str(repo_path)}
        else:
            raise HTTPException(status_code=500, detail="Clone/fetch failed")
    except Exception as e:
        logger.error(f"Error cloning/fetching repo: {e}")
        raise HTTPException(status_code=500, detail="Failed to clone/fetch repository")


@router.get("/repositories/{repo_name}/branches")
async def get_branches(repo_name: str) -> dict:
    """Get branches for a repository."""
    temp_repo_path = validate_temp_local_path(repo_name)
    if not temp_repo_path or not temp_repo_path.exists():
        raise HTTPException(status_code=404, detail="Repository not cloned locally")

    try:
        branches = GitService.get_branches(temp_repo_path)
        return {"branches": branches, "count": len(branches)}
    except Exception as e:
        logger.error(f"Error getting branches: {e}")
        raise HTTPException(status_code=500, detail="Failed to get branches")


@router.get("/repositories/{repo_name}/commits")
async def get_commits(
    repo_name: str, branch: str = Query(None), max_count: int = Query(50)
) -> dict:
    """Get commits from a repository."""
    temp_repo_path = validate_temp_local_path(repo_name)
    if not temp_repo_path or not temp_repo_path.exists():
        raise HTTPException(status_code=404, detail="Repository not cloned locally")

    try:
        commits = GitService.get_commits(temp_repo_path, branch, max_count)
        return {"commits": commits, "count": len(commits)}
    except Exception as e:
        logger.error(f"Error getting commits: {e}")
        raise HTTPException(status_code=500, detail="Failed to get commits")


@router.get("/repositories/{repo_name}/status")
async def get_status(repo_name: str) -> dict:
    """Get repository status."""
    temp_repo_path = validate_temp_local_path(repo_name)
    if not temp_repo_path or not temp_repo_path.exists():
        raise HTTPException(status_code=404, detail="Repository not cloned locally")

    try:
        status = GitService.get_status(temp_repo_path)
        return {"status": status}
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get status")


@router.get("/repositories/{repo_name}/diff/{commit_sha}")
async def get_diff(
    repo_name: str, commit_sha: str, parent_index: int = Query(0)
) -> dict:
    """Get diff for a specific commit."""
    temp_repo_path = validate_temp_local_path(repo_name)
    if not temp_repo_path or not temp_repo_path.exists():
        raise HTTPException(status_code=404, detail="Repository not cloned locally")

    try:
        diff = GitService.get_diff(temp_repo_path, commit_sha, parent_index)
        return {"commit": commit_sha, "diff": diff}
    except Exception as e:
        logger.error(f"Error getting diff: {e}")
        raise HTTPException(status_code=500, detail="Failed to get diff")


@router.post("/repositories/{repo_name}/stage-all")
async def stage_all_changes(repo_name: str) -> dict:
    """Stage all changes in repository."""
    temp_repo_path = validate_temp_local_path(repo_name)
    if not temp_repo_path or not temp_repo_path.exists():
        raise HTTPException(status_code=404, detail="Repository not cloned locally")

    try:
        if GitService.stage_all(temp_repo_path):
            return {"status": "success", "message": "All changes staged"}
        else:
            raise HTTPException(status_code=500, detail="Staging failed")
    except Exception as e:
        logger.error(f"Error staging changes: {e}")
        raise HTTPException(status_code=500, detail="Failed to stage changes")


@router.post("/repositories/{repo_name}/commit")
async def create_commit(repo_name: str, req: CommitRequest) -> dict:
    """Create a commit."""
    temp_repo_path = validate_temp_local_path(repo_name)
    if not temp_repo_path or not temp_repo_path.exists():
        raise HTTPException(status_code=404, detail="Repository not cloned locally")

    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Commit message is required")

    try:
        if GitService.commit(
            temp_repo_path, req.message, req.author_name, req.author_email
        ):
            return {"status": "success", "message": "Commit created"}
        else:
            raise HTTPException(status_code=500, detail="Commit failed")
    except Exception as e:
        logger.error(f"Error creating commit: {e}")
        raise HTTPException(status_code=500, detail="Failed to create commit")


@router.post("/repositories/{repo_name}/push")
async def push_repository(repo_name: str, req: PushRequest) -> dict:
    """Push changes to remote repository."""
    temp_repo_path = validate_temp_local_path(repo_name)
    if not temp_repo_path or not temp_repo_path.exists():
        raise HTTPException(status_code=404, detail="Repository not cloned locally")

    try:
        if GitService.push_changes(temp_repo_path, req.branch):
            return {"status": "success", "message": f"Pushed to {req.branch}"}
        else:
            raise HTTPException(status_code=500, detail="Push failed")
    except Exception as e:
        logger.error(f"Error pushing: {e}")
        raise HTTPException(status_code=500, detail="Failed to push changes")
