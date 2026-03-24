"""
about.py
--------
About page for the CSC512C Cache Simulation Project.

Displays information about the project and team members.
"""

from nicegui import ui

from components.navbar import navbar
from components.footer import footer
from components.author_card import author_card


@ui.page("/about")
def about_page():
    """
    About page endpoint - Information about the project and team.
    
    Endpoint: GET /about
    
    Displays:
        - Navigation bar with links to all pages
        - Page title: "About Cache Simulations"
        - Project description:
            * Academic context (CSC512C 2nd Term)
            * Purpose: web-based platform for simulating and analyzing CPU cache behavior
            * Capabilities: various configurations, replacement policies, performance metrics
        - Authors section:
            * Team members with profile icons
            * Names: Kimberly Klaire H. Gamboa, Andre Emmanuel S. Garcia
            * Team designation: Group 3 · CSC512C
        - Footer with additional information
    
    UI Components:
        - navbar(): Navigation bar component
        - author_card(): Author information cards
        - footer(): Footer component
    
    Layout:
        - Centered content (max-width: 2xl)
        - Vertical spacing with gaps
        - Responsive author cards in a row
    """
    navbar()

    with ui.column().classes("items-center text-center py-16 px-6 gap-4 max-w-2xl mx-auto"):
        ui.label("About Cache Simulations").classes("text-3xl font-bold text-green-800")
        ui.separator().classes("w-24")
        ui.label(
            "This application was built as part of CSC512C 2nd Term. "
            "It provides a web-based platform for simulating and analyzing CPU cache behavior "
            "with various configurations, replacement policies, and performance metrics."
        ).classes("text-gray-600 leading-relaxed")

        # Authors section
        ui.label("Authors").classes("text-xl font-semibold text-green-800 mt-8 mb-2")
        with ui.row().classes("gap-6 mt-4"):
            author_card("Kimberly Klaire H. Gamboa")
            author_card("Andre Emmanuel S. Garcia")

    footer()
