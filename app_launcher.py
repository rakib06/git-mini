"""Application launcher - entry point for the desktop app."""

import sys
import webbrowser
import time
from pathlib import Path

import uvicorn

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.core.logger import logger


def main() -> None:
    """Main entry point for the application."""
    logger.info("Mini GitHub LAN starting...")

    # Open browser after a short delay
    def open_browser() -> None:
        """Open browser to localhost."""
        time.sleep(2)
        url = f"http://{settings.host}:{settings.port}"
        logger.info(f"Opening browser at {url}")
        webbrowser.open(url)

    import threading

    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    # Start Uvicorn server
    logger.info(f"Starting server at {settings.host}:{settings.port}")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        log_level="info",
        reload=False,
    )


if __name__ == "__main__":
    main()
