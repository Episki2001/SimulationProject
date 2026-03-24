from nicegui import ui


def navbar(title: str = "Simulation Project") -> None:
    """Render a sticky top navigation bar."""
    with ui.header().classes("items-center justify-between px-6 py-3 bg-green-700 text-white shadow-md"):
        # Brand / title
        ui.label(title).classes("text-xl font-bold tracking-wide")

        # Navigation links
        with ui.row().classes("gap-4"):
            ui.link("Home",        "/").classes("text-white hover:text-green-200 font-medium")
            ui.link("Simulations", "/simulations").classes("text-white hover:text-green-200 font-medium")
            ui.link("About",       "/about").classes("text-white hover:text-green-200 font-medium")
