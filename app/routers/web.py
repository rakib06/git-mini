"""Web routes for HTML UI."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.core.logger import logger
from app.utils.path_security import validate_repo_file_path
from app.utils.storage import RepositoryStorage
from app.services.git_service import GitService

router = APIRouter(tags=["web"])

# Set up Jinja2
templates_path = settings.base_dir / "templates"
templates = Jinja2Templates(directory=str(templates_path))


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """Home page - list repositories."""
    repos = RepositoryStorage.list_repos()
    from app.utils.path_security import validate_temp_local_path

    enriched_repos = {}
    for name, config in repos.items():
        temp_path = validate_temp_local_path(name)
        is_cloned = temp_path and temp_path.exists()
        if isinstance(config, dict):
            enriched_repos[name] = dict(config)
        else:
            # Handle malformed/corrupted entries gracefully
            enriched_repos[name] = {"remote_path": str(config) if config else "", "last_opened": None}
        enriched_repos[name]["is_cloned"] = is_cloned

    return templates.TemplateResponse(
        request,
        "index.html",
        {"repositories": enriched_repos},
    )


@router.get("/repo/{repo_name}", response_class=HTMLResponse)
async def repo_page(request: Request, repo_name: str) -> HTMLResponse:
    """Repository overview page - ensures clone exists, syncs, shows details."""
    try:
        repo_config = RepositoryStorage.get_repo(repo_name)
        if not repo_config:
            return HTMLResponse(content="<h1>404</h1><p>Repository not found</p>", status_code=404)

        # Phase 3: Ensure local clone exists
        temp_repo_path = GitService.ensure_local_clone(repo_name)
        if not temp_repo_path:
            return HTMLResponse(content="<h1>Error</h1><p>Failed to clone repository locally</p>")

        # Phase 3: Sync latest from LAN
        sync_result = GitService.sync_repo(repo_name)
        if not sync_result:
            logger.warning(f"Failed to sync repo: {repo_name}, but clone exists")

        # Phase 3: Show repo details from temp_local
        status = GitService.get_status(temp_repo_path)
        branches = GitService.get_branches(temp_repo_path)
        commits = GitService.get_commits(temp_repo_path, max_count=10)
        commit_count = GitService.get_commit_count(temp_repo_path)

        # Check if local clone has files (not just if bare repo is empty)
        root_listing = GitService.list_directory(temp_repo_path, "")
        has_files = bool(root_listing.get("entries"))
        # If local clone has files, it's not empty even if bare repo has no commits
        is_empty = not has_files and GitService.is_empty_repo(repo_config["remote_path"])

        # Add previewability flag to root entries
        for entry in root_listing.get("entries", []):
            if not entry.get("is_dir"):
                entry_path = temp_repo_path / entry["path"]
                entry["is_previewable"] = GitService.is_text_file(entry_path)

        return templates.TemplateResponse(
            request,
            "repo.html",
            {
                "repo_name": repo_name,
                "repo_config": repo_config,
                "status": status,
                "branches": branches,
                "recent_commits": commits,
                "sync_status": "success" if sync_result else "warning",
                "is_empty": is_empty,
                "has_files": has_files,
                "root_entries": root_listing.get("entries", []),
                "commit_count": commit_count,
                "remote_path": repo_config["remote_path"],
            },
        )
    except Exception as e:
        logger.error(f"Error rendering repo page: {e}")
        return HTMLResponse(content=f"<h1>Error</h1><p>{str(e)}</p>")


@router.get("/repo/{repo_name}/branches", response_class=HTMLResponse)
async def branches_page(request: Request, repo_name: str) -> HTMLResponse:
    """Repository branches page - ensures clone exists."""
    try:
        repo_config = RepositoryStorage.get_repo(repo_name)
        if not repo_config:
            return HTMLResponse(content="<h1>404</h1><p>Repository not found</p>", status_code=404)

        temp_repo_path = GitService.ensure_local_clone(repo_name)
        if not temp_repo_path:
            return HTMLResponse(content="<h1>Error</h1><p>Failed to clone repository locally</p>")

        branches = GitService.get_branches(temp_repo_path)
        return templates.TemplateResponse(
            request,
            "branches.html",
            {"repo_name": repo_name, "branches": branches},
        )
    except Exception as e:
        logger.error(f"Error rendering branches page: {e}")
        return HTMLResponse(content=f"<h1>Error</h1><p>{str(e)}</p>")


@router.get("/repo/{repo_name}/commits", response_class=HTMLResponse)
async def commits_page(request: Request, repo_name: str) -> HTMLResponse:
    """Repository commits page - ensures clone exists."""
    try:
        repo_config = RepositoryStorage.get_repo(repo_name)
        if not repo_config:
            return HTMLResponse(content="<h1>404</h1><p>Repository not found</p>", status_code=404)

        temp_repo_path = GitService.ensure_local_clone(repo_name)
        if not temp_repo_path:
            return HTMLResponse(content="<h1>Error</h1><p>Failed to clone repository locally</p>")

        commits = GitService.get_commits(temp_repo_path, max_count=50)
        return templates.TemplateResponse(
            request,
            "commits.html",
            {"repo_name": repo_name, "commits": commits},
        )
    except Exception as e:
        logger.error(f"Error rendering commits page: {e}")
        return HTMLResponse(content=f"<h1>Error</h1><p>{str(e)}</p>")


@router.get("/repo/{repo_name}/status", response_class=HTMLResponse)
async def status_page(request: Request, repo_name: str) -> HTMLResponse:
    """Repository status page - ensures clone exists."""
    try:
        repo_config = RepositoryStorage.get_repo(repo_name)
        if not repo_config:
            return HTMLResponse(content="<h1>404</h1><p>Repository not found</p>", status_code=404)

        temp_repo_path = GitService.ensure_local_clone(repo_name)
        if not temp_repo_path:
            return HTMLResponse(content="<h1>Error</h1><p>Failed to clone repository locally</p>")

        status = GitService.get_status(temp_repo_path)
        return templates.TemplateResponse(
            request,
            "status.html",
            {"repo_name": repo_name, "status": status},
        )
    except Exception as e:
        logger.error(f"Error rendering status page: {e}")
        return HTMLResponse(content=f"<h1>Error</h1><p>{str(e)}</p>")


@router.get("/repo/{repo_name}/diff/{commit_sha}", response_class=HTMLResponse)
async def diff_page(request: Request, repo_name: str, commit_sha: str) -> HTMLResponse:
    """Commit diff page - ensures clone exists."""
    try:
        repo_config = RepositoryStorage.get_repo(repo_name)
        if not repo_config:
            return HTMLResponse(content="<h1>404</h1><p>Repository not found</p>", status_code=404)

        temp_repo_path = GitService.ensure_local_clone(repo_name)
        if not temp_repo_path:
            return HTMLResponse(content="<h1>Error</h1><p>Failed to clone repository locally</p>")

        diff = GitService.get_diff(temp_repo_path, commit_sha)
        return templates.TemplateResponse(
            request,
            "diff.html",
            {"repo_name": repo_name, "commit_sha": commit_sha, "diff": diff},
        )
    except Exception as e:
        logger.error(f"Error rendering diff page: {e}")
        return HTMLResponse(content=f"<h1>Error</h1><p>{str(e)}</p>")


@router.get("/repo/{repo_name}/files", response_class=HTMLResponse)
async def files_page(request: Request, repo_name: str, path: str = "") -> HTMLResponse:
    """Repository file browser page."""
    try:
        repo_config = RepositoryStorage.get_repo(repo_name)
        if not repo_config:
            return HTMLResponse(content="<h1>404</h1><p>Repository not found</p>", status_code=404)

        temp_repo_path = GitService.ensure_local_clone(repo_name)
        if not temp_repo_path:
            return HTMLResponse(content="<h1>Error</h1><p>Failed to clone repository locally</p>")

        target_path = validate_repo_file_path(repo_name, path)
        if target_path is None:
            return HTMLResponse(content="<h1>403</h1><p>Invalid path</p>", status_code=403)

        if not target_path.exists():
            return HTMLResponse(content="<h1>404</h1><p>Path not found</p>", status_code=404)

        # If path is a file, redirect to view
        if target_path.is_file():
            from fastapi.responses import RedirectResponse
            return RedirectResponse(
                url=request.url_for("view_file_page", repo_name=repo_name).include_query_params(path=path)
            )

        result = GitService.list_directory(temp_repo_path, path)

        # Add is_binary flag to entries
        for entry in result.get("entries", []):
            if not entry.get("is_dir"):
                entry_path = target_path / entry["name"]
                entry["is_binary"] = not GitService.is_text_file(entry_path)

        # Breadcrumb parts
        breadcrumb_parts = []
        if path:
            parts = path.strip("/").split("/")
            accum = ""
            for part in parts:
                accum = f"{accum}/{part}" if accum else part
                breadcrumb_parts.append({"name": part, "path": accum})

        # Parent path for back button
        parent_path = "/".join(path.strip("/").split("/")[:-1]) if path else ""

        return templates.TemplateResponse(
            request,
            "files.html",
            {
                "repo_name": repo_name,
                "repo_config": repo_config,
                "path": path,
                "entries": result["entries"],
                "error": result["error"],
                "breadcrumb_parts": breadcrumb_parts,
                "parent_path": parent_path,
            },
        )
    except Exception as e:
        logger.error(f"Error rendering files page: {e}")
        return HTMLResponse(content=f"<h1>Error</h1><p>{str(e)}</p>")


@router.get("/repo/{repo_name}/download")
async def download_file(repo_name: str, path: str = ""):
    """Download a file from the repository."""
    repo_config = RepositoryStorage.get_repo(repo_name)
    if not repo_config:
        return HTMLResponse(content="Repository not found", status_code=404)

    target_path = validate_repo_file_path(repo_name, path)
    if target_path is None:
        return HTMLResponse(content="Invalid path", status_code=403)

    if not target_path.exists() or not target_path.is_file():
        return HTMLResponse(content="File not found", status_code=404)

    mime = GitService.get_safe_mime_type(target_path)
    return FileResponse(
        path=str(target_path),
        media_type=mime,
        filename=target_path.name,
    )


@router.get("/repo/{repo_name}/view", response_class=HTMLResponse)
async def view_file_page(request: Request, repo_name: str, path: str = "") -> HTMLResponse:
    """View a text file from the repository."""
    try:
        repo_config = RepositoryStorage.get_repo(repo_name)
        if not repo_config:
            return HTMLResponse(content="<h1>404</h1><p>Repository not found</p>", status_code=404)

        temp_repo_path = GitService.ensure_local_clone(repo_name)
        if not temp_repo_path:
            return HTMLResponse(content="<h1>Error</h1><p>Failed to clone repository locally</p>")

        target_path = validate_repo_file_path(repo_name, path)
        if target_path is None:
            return HTMLResponse(content="<h1>403</h1><p>Invalid path</p>", status_code=403)

        if not target_path.exists() or not target_path.is_file():
            return HTMLResponse(content="<h1>404</h1><p>File not found</p>", status_code=404)

        if not GitService.is_text_file(target_path):
            return HTMLResponse(
                content="<h1>415</h1><p>Binary files cannot be previewed. Please download instead.</p>",
                status_code=415,
            )

        # Read content safely
        try:
            content = target_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            content = "Error reading file."

        # Breadcrumb parts
        breadcrumb_parts = []
        if path:
            parts = path.strip("/").split("/")
            accum = ""
            for part in parts:
                accum = f"{accum}/{part}" if accum else part
                breadcrumb_parts.append({"name": part, "path": accum})

        # Parent path for back link
        parent_path = "/".join(path.strip("/").split("/")[:-1]) if path else ""

        lang_class = GitService._get_lang_class(
            target_path.suffix.lower().lstrip(".")
        )

        return templates.TemplateResponse(
            request,
            "view.html",
            {
                "repo_name": repo_name,
                "path": path,
                "filename": target_path.name,
                "content": content,
                "breadcrumb_parts": breadcrumb_parts,
                "parent_path": parent_path,
                "lang_class": lang_class,
            },
        )
    except Exception as e:
        logger.error(f"Error rendering view page: {e}")
        return HTMLResponse(content=f"<h1>Error</h1><p>{str(e)}</p>")


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request) -> HTMLResponse:
    """Settings page."""
    try:
        return templates.TemplateResponse(
            request,
            "settings.html",
            {
                "host": settings.host,
                "port": settings.port,
                "allowed_paths": settings.allowed_paths,
                "temp_local_dir": settings.temp_local_dir,
            },
        )
    except Exception as e:
        logger.error(f"Error rendering settings page: {e}")
        return HTMLResponse(content=f"<h1>Error</h1><p>{str(e)}</p>")
