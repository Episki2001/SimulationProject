from nicegui import ui


def links(
    heading: str = "Welcome to the Simulation Project",
    subheading: str = "Run, track, and analyse simulations with ease.",
    cta_label: str = "Get Started",
    cta_target: str = "/simulations",
) -> None:
    """Render a centred hero banner."""
    with ui.column().classes("items-center justify-center text-center py-20 px-6 w-full bg-green-50"):
        ui.label(heading).classes("text-4xl font-extrabold text-green-800 mb-4")
        ui.label(subheading).classes("text-lg text-gray-600 mb-8 max-w-xl")
        ui.button(cta_label, on_click=lambda: ui.navigate.to(cta_target)).classes(
            "bg-green-600 text-white px-6 py-3 rounded-lg text-base font-semibold hover:bg-green-700"
        )
