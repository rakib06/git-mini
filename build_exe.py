"""PyInstaller build script for Mini GitHub LAN desktop app."""

import PyInstaller.__main__
from pathlib import Path

# Get project root
project_root = Path(__file__).parent

# Build command
PyInstaller.__main__.run(
    [
        str(project_root / "app_launcher.py"),
        "--name=Mini-GitHub-LAN",
        "--onefile",
        "--windowed",
        f'--distpath={project_root / "dist"}',
        f'--buildpath={project_root / "build"}',
        f'--specpath={project_root / "build"}',
        "--hidden-import=git",
        "--hidden-import=fastapi",
        "--hidden-import=uvicorn",
        "--hidden-import=jinja2",
        "--collect-all=fastapi",
        "--collect-all=uvicorn",
    ]
)

print("Build complete! Find the executable in: dist/Mini-GitHub-LAN.exe")
