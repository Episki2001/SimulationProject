"""
simulations.py
--------------
Simulations page for the CSC512C Cache Simulation Project.

Main dashboard for creating and managing cache simulations.
"""

from nicegui import ui

from components.navbar import navbar
from components.footer import footer
from components.stats_card import stats_card
from components.simulation_form import simulation_form
from components.simulation_card import simulation_card
from backend.data import get_all_simulations, get_stats, delete_all_simulations


@ui.refreshable
def _simulations_list():
    """Refreshable simulations list that updates when new simulations are added."""
    simulations = get_all_simulations()
    if not simulations:
        ui.label("No simulations yet.").classes("text-gray-400 italic")
    else:
        with ui.column().classes("w-full gap-3"):
            # Display most recent simulations first
            for sim in reversed(simulations):
                simulation_card(sim)


def _handle_delete_all(refresh_callback):
    """Handle delete all simulations with confirmation dialog."""
    simulations = get_all_simulations()
    if not simulations:
        ui.notify("No simulations to delete", type="info")
        return
    
    with ui.dialog() as dialog, ui.card():
        ui.label("Delete All Simulations?").classes("text-lg font-bold")
        ui.label(f"Are you sure you want to delete all {len(simulations)} simulation(s)? This action cannot be undone.").classes("text-gray-700 mb-4")
        with ui.row().classes("gap-2 ml-auto"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Delete All", 
                     on_click=lambda: (delete_all_simulations(), 
                                     ui.notify(f"Deleted {len(simulations)} simulation(s)", type="positive"),
                                     dialog.close(),
                                     refresh_callback()), 
                     color="red").props("flat")
    
    dialog.open()


@ui.page("/simulations")
def simulations_page():
    """
    Simulations dashboard endpoint - Main page for creating and managing cache simulations.
    """
    navbar()

    with ui.column().classes("w-full max-w-5xl mx-auto py-10 px-6 gap-6"):
        ui.label("Cache Simulations Dashboard").classes("text-3xl font-bold text-green-800")

        ui.separator()

        # Add simulation form 
        simulation_form(on_success=_simulations_list.refresh)

        ui.separator()
        
        # Display simulations 
        with ui.row().classes("gap-2"):
            ui.label("Cache Simulations").classes("text-lg font-semibold text-green-700")
            ui.button("Delete All", on_click=lambda: _handle_delete_all(_simulations_list.refresh), color="red") \
                .props("flat size=sm") \
                .classes("ml-auto")
        
        _simulations_list()

    footer()
