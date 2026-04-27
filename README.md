# Mini GitHub LAN

## Overview
A local GitHub-like desktop application for managing Git repositories stored on LAN shares. Built with FastAPI, Jinja2, and GitPython.

## Architecture

- **Backend**: FastAPI (async web framework)
- **Frontend**: HTML/CSS/JavaScript with Jinja2 templating
- **Git Operations**: GitPython library
- **Storage**: JSON configuration + local clones
- **Desktop**: PyInstaller executable

### Key Features
- Clone repositories from LAN shares to local temp_local directory
- Automatic fetch/pull for existing clones
- Web-based UI for repository management
- View branches, commits, and diffs
- Stage, commit, and push changes
- Secure path validation (no directory traversal)
- Localhost-only binding for security

## Project Structure
```
├── app/
│   ├── core/
│   │   ├── config.py      # Settings from config/settings.json
│   │   └── logger.py      # Logging setup
│   ├── routers/
│   │   ├── api.py         # JSON API endpoints
│   │   └── web.py         # HTML web routes
│   ├── services/
│   │   └── git_service.py # Git operations (GitPython wrapper)
│   ├── utils/
│   │   ├── path_security.py  # Path validation, prevent traversal
│   │   └── storage.py        # repos.json management
│   └── main.py            # FastAPI app initialization
├── config/
│   ├── settings.json      # Server configuration
│   └── repos.json         # Registered repositories
├── templates/             # Jinja2 HTML templates
├── static/
│   ├── css/style.css      # Stylesheet
│   └── js/app.js          # Frontend JavaScript
├── logs/                  # Application logs
├── temp_local/            # Local clones
├── app_launcher.py        # Entry point (localhost + auto-open browser)
├── build_exe.py           # PyInstaller build script
└── requirements.txt       # Python dependencies
```

## Installation

### Requirements
- Python 3.14+
- Git installed and in PATH

### Setup
```bash
# Clone or download the project
cd git-mini-lan

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python app_launcher.py
```

The app will:
1. Start FastAPI server on 127.0.0.1:8000 (localhost only)
2. Open your default browser automatically
3. Show the repository management UI

## Configuration

### config/settings.json
```json
{
  "host": "127.0.0.1",
  "port": 8000,
  "allowed_paths": [
    "\\\\192.168.0.123\\share\\reposv2"
  ],
  "temp_local_dir": "temp_local"
}
```

- **host**: Bind address (127.0.0.1 = localhost only)
- **port**: Server port
- **allowed_paths**: UNC paths to LAN shares with bare repos
- **temp_local_dir**: Where clones are stored locally

### config/repos.json
Auto-created with registered repositories:
```json
{
  "my-project": {
    "remote_path": "\\\\192.168.0.123\\share\\reposv2\\my-project.git",
    "last_opened": null
  }
}
```

## API Endpoints

### Repository Management
- `GET /api/repositories` - List all repositories
- `POST /api/repositories` - Register new repository
- `DELETE /api/repositories/{repo_name}` - Remove repository
- `POST /api/repositories/{repo_name}/clone-or-fetch` - Clone or update

### Repository Info
- `GET /api/repositories/{repo_name}/branches` - List branches
- `GET /api/repositories/{repo_name}/commits?branch=&max_count=50` - Get commits
- `GET /api/repositories/{repo_name}/status` - Repository status
- `GET /api/repositories/{repo_name}/diff/{commit_sha}` - Commit diff

### Git Operations
- `POST /api/repositories/{repo_name}/stage-all` - Stage all changes
- `POST /api/repositories/{repo_name}/commit` - Create commit
- `POST /api/repositories/{repo_name}/push` - Push changes

### Web Routes
- `GET /` - Repository list (HTML)
- `GET /repo/{repo_name}` - Repository overview
- `GET /repo/{repo_name}/branches` - Branches page
- `GET /repo/{repo_name}/commits` - Commits page
- `GET /repo/{repo_name}/status` - Status page
- `GET /repo/{repo_name}/diff/{commit_sha}` - Diff viewer
- `GET /settings` - Settings page

## Security

### Path Validation
- All paths are validated against `allowed_paths` from settings
- No `shell=True` - all Git operations use GitPython API
- Repository names validated to prevent directory traversal
- Localhost-only binding (127.0.0.1)

### Design
- No execution of untrusted shell commands
- Path resolution uses `Path.resolve()` + `relative_to()` checks
- UNC paths supported for LAN share access
- Git operations use secure GitPython library

## Building Standalone Executable

### Requirements
- PyInstaller
- All dependencies in requirements.txt

### Build
```bash
python build_exe.py
```

Output: `dist/Mini-GitHub-LAN.exe`

The executable includes:
- All Python packages
- FastAPI + Uvicorn server
- Git wrapper (GitPython)
- All templates and static files
- Single self-contained file

## Usage Workflow

1. **Register Repository**
   - Click "Add Repository"
   - Provide name and UNC path to bare repo on LAN share
   - Click "Add"

2. **Clone/Fetch**
   - Click "Clone/Fetch" button
   - First time: clones to temp_local/{repo_name}
   - Subsequent: fetches and pulls latest changes

3. **View Repository**
   - Click "Open" to view repository details
   - Navigate to Branches, Commits, Status

4. **Make Changes**
   - View Status to see staged/unstaged changes
   - Click "Stage All" to stage changes
   - Click "Commit" to create a commit
   - Click "Push" to push to remote

5. **Cleanup**
   - Delete repository from settings (won't delete remote)
   - Local clone stays in temp_local/ (manual delete if needed)

## Troubleshooting

### Repository won't clone
- Verify UNC path is correct and accessible
- Check path is in `allowed_paths` in settings.json
- Ensure Windows network/SMB access works

### Changes won't push
- Verify branch name (default: main)
- Check Git user is configured globally
- Ensure remote access permissions are correct

### Port already in use
- Change port in config/settings.json
- Or stop other application using that port

### Logs
- Check `logs/app.log` for detailed error information
- Application logs to both file and console

## Modular Design

### Core Components
1. **Config Module** - Settings management with validation
2. **Logger Module** - Rotating file + console logging
3. **Path Security** - Centralized path validation
4. **Storage Module** - Persistent repos.json management
5. **Git Service** - GitPython operations wrapper
6. **API Router** - RESTful JSON endpoints
7. **Web Router** - HTML UI routes with Jinja2

### Benefits
- Each module is independently testable
- Clear separation of concerns
- Easy to extend with new routes/operations
- Secure by design (no shell execution)
- Production-ready error handling

## Development

### Running in Development Mode
```bash
python app_launcher.py
```

### Running Uvicorn Directly
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Code Quality
- Uses `ruff` for linting
- Uses `black` for formatting
- Type hints throughout
- Error handling and validation

## Production Considerations

### Deployment
- Build standalone executable with PyInstaller
- No Python installation required on target
- Single file distribution
- Auto-opens UI in default browser

### Performance
- Async FastAPI handlers
- Efficient GitPython usage
- Rotating file logs (10MB max)
- Lazy template compilation

### Security
- Localhost binding only
- Path traversal protection
- No shell command injection
- UNC path validation

## License
Internal use only
