"""
author_card.py
--------------
Reusable author card component for displaying team member information.

Usage:
    author_card("Kimberly Klaire H. Gamboa")
"""

from nicegui import ui


def author_card(name: str):
    """
    Display an author card with name and team information.
    """
    with ui.card().classes("p-6 rounded-xl shadow w-64 text-center"):
        ui.icon("person").classes("text-green-500 text-4xl mb-2")
        ui.label(name).classes("font-semibold text-green-800")
        ui.label("Group 3 · CSC512C").classes("text-xs text-gray-400")
