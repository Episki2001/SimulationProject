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
    # Get port from environment variable (for Render) or default to 8080
    port = int(os.getenv("PORT", 8080))
    
    # Detect if running in production
    is_production = os.getenv("RENDER") is not None
    
    ui.run(
        title="CSC512C Simulation Project",
        favicon="🔬",
        host="0.0.0.0",  # Required for Render to bind correctly
        port=port,
        reload=not is_production,  # Disable reload in production
        storage_secret="csc512c-cache-simulation-secret-key" 
    )
