"""
feature_card.py
---------------
Reusable feature card component for displaying feature highlights.

Usage:
    feature_card(
        icon="memory",
        title="Cache Config",
        description="Customize cache size, block size, associativity, and replacement policy."
    )
"""

from nicegui import ui


def feature_card(icon: str, title: str, description: str):
    """
    Display a feature card with icon, title, and description.
    
    Args:
        icon: Material icon name (e.g., 'memory', 'bar_chart', 'group')
        title: Feature title
        description: Feature description text
    """
    with ui.card().classes("p-6 rounded-xl shadow w-64 text-center"):
        ui.icon(icon).classes("text-green-600 text-4xl mb-3")
        ui.label(title).classes("font-semibold text-lg text-green-800 mb-1")
        ui.label(description).classes("text-sm text-gray-500")
