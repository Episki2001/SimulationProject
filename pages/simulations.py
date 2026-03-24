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


@ui.page("/simulations")
def simulations_page():
    """
    Simulations dashboard endpoint - Main page for creating and managing cache simulations.
    """
    navbar()

    with ui.column().classes("w-full max-w-5xl mx-auto py-10 px-6 gap-6"):
        ui.label("Cache Simulations Dashboard").classes("text-3xl font-bold text-green-800")

        # --- Stats row ---
        stats = get_stats()
        ui.separator()

        # --- Simulation list (refreshable) - Define first so we can reference its refresh method ---
        @ui.refreshable
        def simulations_list():
            """Refreshable simulations list that updates when new simulations are added."""
            simulations = get_all_simulations()
            if not simulations:
                ui.label("No simulations yet.").classes("text-gray-400 italic")
            else:
                with ui.column().classes("w-full gap-3"):
                    # Display most recent simulations first
                    for sim in reversed(simulations):
                        simulation_card(sim)

        # --- Add simulation form ---
        simulation_form(on_success=simulations_list.refresh)

        ui.separator()
        
        # --- Display simulations ---
        async def handle_delete_all():
            """Handle delete all simulations with confirmation dialog."""
            simulations = get_all_simulations()
            if not simulations:
                ui.notify("No simulations to delete", type="info")
                return
            
            result = await ui.dialog().props("persistent") \
                .with_slots('<v-card>' + 
                           '<v-card-title>Delete All Simulations?</v-card-title>' +
                           f'<v-card-text>Are you sure you want to delete all {len(simulations)} simulation(s)? This action cannot be undone.</v-card-text>' +
                           '<v-card-actions>' +
                           '<v-spacer></v-spacer>' +
                           '<v-btn flat @click="$emit(\'close\', false)">Cancel</v-btn>' +
                           '<v-btn flat color="red" @click="$emit(\'close\', true)">Delete All</v-btn>' +
                           '</v-card-actions>' +
                           '</v-card>')
            
            if result:
                count = delete_all_simulations()
                ui.notify(f"Deleted {count} simulation(s)", type="positive")
                simulations_list.refresh()
        
        with ui.row().classes("gap-2"):
            ui.label("Cache Simulations").classes("text-lg font-semibold text-green-700")
            ui.button("Delete All", on_click=handle_delete_all, color="red") \
                .props("flat size=sm") \
                .classes("ml-auto")
        
        simulations_list()

    footer()
