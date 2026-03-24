from nicegui import ui


def stats_card(label: str, value: str | int, color: str = "green") -> None:
    """Render a coloured stat card."""
    with ui.card().classes(f"p-6 rounded-xl shadow text-center border-t-4 border-{color}-500 w-40"):
        ui.label(str(value)).classes(f"text-3xl font-bold text-{color}-700")
        ui.label(label).classes("text-sm text-gray-500 mt-1 uppercase tracking-wide")
