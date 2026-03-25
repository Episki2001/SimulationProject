import os
from nicegui import ui

# Import page modules to register @ui.page routes
from pages.home import home_page
from pages.simulations import simulations_page
from pages.about import about_page


# ---------------------------------------------------------------------------
# Launch
# ---------------------------------------------------------------------------

if __name__ in {"__main__", "__mp_main__"}:
    # Get configuration from environment variables (for cloud deployment)
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    reload = os.getenv("RELOAD", "false").lower() == "true"
    storage_secret = os.getenv("STORAGE_SECRET", "csc512c-cache-simulation-secret-key")
    
    ui.run(
        title="CSC512C Simulation Project",
        favicon="🔬",
        host=host,
        port=port,
        reload=reload,
        storage_secret=storage_secret
    )
