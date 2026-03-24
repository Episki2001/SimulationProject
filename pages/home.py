from nicegui import ui

from components.navbar import navbar
from components.links import links
from components.footer import footer


@ui.page("/")
def home_page():
    """
    Home page endpoint - Landing page for the cache simulation application.
    """
    navbar()

    links(
        heading="CSC512C Cache Simulation Project",
        subheading="Simulate, analyse, and optimize cache performance with configurable parameters.",
        cta_label="View Cache Simulations",
        cta_target="/simulations",
    )

    footer()
