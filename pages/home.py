"""
home.py
-------
Home page for the CSC512C Cache Simulation Project.

Displays landing page with project overview and feature highlights.
"""

from nicegui import ui

from components.navbar import navbar
from components.hero import hero
from components.footer import footer


@ui.page("/")
def home_page():
    """
    Home page endpoint - Landing page for the cache simulation application.
    
    Endpoint: GET /
    
    Displays:
        - Navigation bar with links to all pages
        - Hero section with project title, description, and CTA button
        - Feature highlights showcasing:
            * Cache configuration capabilities
            * Performance metrics tracking
            * Team information
        - Footer with additional information
    
    UI Components:
        - navbar(): Navigation bar component
        - hero(): Hero banner with heading, subheading, and call-to-action
        - Feature cards: 3 cards highlighting main features
        - footer(): Footer component
    
    Navigation:
        - CTA button links to /simulations page
        - Navbar provides links to /simulations and /about pages
    """
    navbar()

    hero(
        heading="CSC512C Cache Simulation Project",
        subheading="Simulate, analyse, and optimize cache performance with configurable parameters.",
        cta_label="View Cache Simulations",
        cta_target="/simulations",
    )

    footer()
