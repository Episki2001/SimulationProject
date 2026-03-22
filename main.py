from nicegui import ui

# Import page modules to register @ui.page routes
from pages.home import home_page
from pages.simulations import simulations_page
from pages.about import about_page


# ---------------------------------------------------------------------------
# Launch
# ---------------------------------------------------------------------------

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="CSC512C Simulation Project",
        favicon="🔬",
        port=8080,
        reload=True,
        storage_secret="csc512c-cache-simulation-secret-key" 
    )
