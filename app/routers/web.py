"""Web routes for HTML UI."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

from app.core.config import settings
from app.core.logger import logger
from app.utils.storage import RepositoryStorage
from app.services.git_service import GitService
from app.utils.path_security import validate_temp_local_path

router = APIRouter(tags=["web"])

# Set up Jinja2
templates_path = settings.base_dir / "templates"
env = Environment(loader=FileSystemLoader(str(templates_path)))


@router.get("/", response_class=HTMLResponse)
async def index() -> str:
    """Home page - list repositories."""
    try:
        repos = RepositoryStorage.list_repos()
        template = env.get_template("index.html")
        return template.render(repositories=repos)
    except Exception as e:
        logger.error(f"Error rendering index: {e}")
        return f"<h1>Error</h1><p>{str(e)}</p>"


@router.get("/repo/{repo_name}", response_class=HTMLResponse)
async def repo_page(repo_name: str) -> str:
    """Repository overview page - ensures clone exists, syncs, shows details."""
    try:
        repo_config = RepositoryStorage.get_repo(repo_name)
        if not repo_config:
            return "<h1>404</h1><p>Repository not found</p>"

        # Phase 3: Ensure local clone exists
        temp_repo_path = GitService.ensure_local_clone(repo_name)
        if not temp_repo_path:
            return "<h1>Error</h1><p>Failed to clone repository locally</p>"

        # Phase 3: Sync latest from LAN
        sync_result = GitService.sync_repo(repo_name)
        if not sync_result:
            logger.warning(f"Failed to sync repo: {repo_name}, but clone exists")

        # Phase 3: Show repo details from temp_local
        status = GitService.get_status(temp_repo_path)
        branches = GitService.get_branches(temp_repo_path)
        commits = GitService.get_commits(temp_repo_path, max_count=10)

        template = env.get_template("repo.html")
        return template.render(
            repo_name=repo_name,
            repo_config=repo_config,
            status=status,
            branches=branches,
            recent_commits=commits,
            sync_status="success" if sync_result else "warning",
        )
    except Exception as e:
        logger.error(f"Error rendering repo page: {e}")
        return f"<h1>Error</h1><p>{str(e)}</p>"


@router.get("/repo/{repo_name}/branches", response_class=HTMLResponse)
async def branches_page(repo_name: str) -> str:
    """Repository branches page - ensures clone exists."""
    try:
        repo_config = RepositoryStorage.get_repo(repo_name)
        if not repo_config:
            return "<h1>404</h1><p>Repository not found</p>"

        temp_repo_path = GitService.ensure_local_clone(repo_name)
        if not temp_repo_path:
            return "<h1>Error</h1><p>Failed to clone repository locally</p>"

        branches = GitService.get_branches(temp_repo_path)
        template = env.get_template("branches.html")
        return template.render(repo_name=repo_name, branches=branches)
    except Exception as e:
        logger.error(f"Error rendering branches page: {e}")
        return f"<h1>Error</h1><p>{str(e)}</p>"


@router.get("/repo/{repo_name}/commits", response_class=HTMLResponse)
async def commits_page(repo_name: str) -> str:
    """Repository commits page - ensures clone exists."""
    try:
        repo_config = RepositoryStorage.get_repo(repo_name)
        if not repo_config:
            return "<h1>404</h1><p>Repository not found</p>"

        temp_repo_path = GitService.ensure_local_clone(repo_name)
        if not temp_repo_path:
            return "<h1>Error</h1><p>Failed to clone repository locally</p>"

        commits = GitService.get_commits(temp_repo_path, max_count=50)
        template = env.get_template("commits.html")
        return template.render(repo_name=repo_name, commits=commits)
    except Exception as e:
        logger.error(f"Error rendering commits page: {e}")
        return f"<h1>Error</h1><p>{str(e)}</p>"


@router.get("/repo/{repo_name}/status", response_class=HTMLResponse)
async def status_page(repo_name: str) -> str:
    """Repository status page - ensures clone exists."""
    try:
        repo_config = RepositoryStorage.get_repo(repo_name)
        if not repo_config:
            return "<h1>404</h1><p>Repository not found</p>"

        temp_repo_path = GitService.ensure_local_clone(repo_name)
        if not temp_repo_path:
            return "<h1>Error</h1><p>Failed to clone repository locally</p>"

        status = GitService.get_status(temp_repo_path)
        template = env.get_template("status.html")
        return template.render(repo_name=repo_name, status=status)
    except Exception as e:
        logger.error(f"Error rendering status page: {e}")
        return f"<h1>Error</h1><p>{str(e)}</p>"


@router.get("/repo/{repo_name}/diff/{commit_sha}", response_class=HTMLResponse)
async def diff_page(repo_name: str, commit_sha: str) -> str:
    """Commit diff page - ensures clone exists."""
    try:
        repo_config = RepositoryStorage.get_repo(repo_name)
        if not repo_config:
            return "<h1>404</h1><p>Repository not found</p>"

        temp_repo_path = GitService.ensure_local_clone(repo_name)
        if not temp_repo_path:
            return "<h1>Error</h1><p>Failed to clone repository locally</p>"

        diff = GitService.get_diff(temp_repo_path, commit_sha)
        template = env.get_template("diff.html")
        return template.render(repo_name=repo_name, commit_sha=commit_sha, diff=diff)
    except Exception as e:
        logger.error(f"Error rendering diff page: {e}")
        return f"<h1>Error</h1><p>{str(e)}</p>"


@router.get("/settings", response_class=HTMLResponse)
async def settings_page() -> str:
    """Settings page."""
    try:
        template = env.get_template("settings.html")
        return template.render(
            host=settings.host,
            port=settings.port,
            allowed_paths=settings.allowed_paths,
            temp_local_dir=settings.temp_local_dir,
        )
    except Exception as e:
        logger.error(f"Error rendering settings page: {e}")
        return f"<h1>Error</h1><p>{str(e)}</p>"
