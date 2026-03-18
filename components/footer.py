"""
components/footer.py
--------------------
Simple page footer component.
"""

from nicegui import ui


def footer(text: str = "© 2026 Group 3 — Garcia & Gamboa | CSC512C") -> None:
    """Render a bottom footer bar."""
    with ui.footer().classes("flex items-center justify-center py-4 bg-green-700 text-white text-sm"):
        ui.label(text)
