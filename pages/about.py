from nicegui import ui

from components.navbar import navbar
from components.footer import footer
from components.author_card import author_card


@ui.page("/about")
def about_page():
    """
    Information about the project and team.
    """
    navbar()

    with ui.column().classes("items-center text-center py-16 px-6 gap-4 max-w-2xl mx-auto"):
        ui.label("About Cache Simulations").classes("text-3xl font-bold text-green-800")
        ui.separator().classes("w-24")
        ui.label(
            "This application was built as part of CSC512C 2nd Term. "
            "It provides a web-based platform for simulating and analyzing cache memory behavior "
            "with various configurations and performance metrics." 
            "This application currently supports Direct Mapping, and 8-Way Set Associative cache Types, with LRU Replacement Policy."
        ).classes("text-gray-600 leading-relaxed")

        # Authors section
        ui.label("Authors").classes("text-xl font-semibold text-green-800 mt-8 mb-2")
        with ui.row().classes("gap-6 mt-4"):
            author_card("Kimberly Klaire H. Gamboa")
            author_card("Andre Emmanuel S. Garcia")

    footer()
