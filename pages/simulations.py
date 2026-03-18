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
from backend.data import get_all_simulations, get_stats


@ui.page("/simulations")
def simulations_page():
    """
    Simulations dashboard endpoint - Main page for creating and managing cache simulations.
    
    Endpoint: GET /simulations
    
    Features:
        1. Statistics Dashboard:
           - Total simulations count
           - Completed simulations count
           - Running simulations count
        
        2. Simulation Creation Form:
           - Simulation name input
           - Simulation type selector (Direct Mapped / 8-Way Set Associative + LRU)
           - Cache configuration:
               * Cache blocks (power-of-2, min 4)
               * Block size in words (power-of-2, min 2)
           - Timing configuration:
               * Cache access time (ns per block)
               * Memory access time (ns per word)
           - Test pattern selector (sequential, mid_repeat, random, custom)
           - Custom pattern input (shown only when custom is selected)
           - Create button to run simulation
        
        3. Simulations List (most recent first):
           Each simulation card displays:
           - Header: ID, name, status (DONE/RUNNING/ERROR)
           - Configuration: simulation type, memory space, cache size, block size,
                          cache access time, memory access time, test pattern
           - Custom pattern details (if applicable)
           - Results (if completed):
               * Accesses, hits, misses
               * Hit rate, miss rate
               * Miss penalty, average access time, total access time
           - Cache Animation: Step-by-step visualization with play controls
           - Final Cache Memory: Visual representation of cache state
           - Delete button to remove simulation
    
    Data Storage:
        - All simulations stored in browser localStorage (per-user)
        - Automatically persisted across browser sessions
        - Isolated per user/browser
    
    UI Components:
        - navbar(): Navigation bar component
        - stats_card(): Statistics display cards
        - simulation_form(): Form for creating new simulations
        - simulation_card(): Display individual simulation details
        - footer(): Footer component
    
    Actions:
        - Create simulation: Handled by simulation_form component
        - Delete simulation: Handled by simulation_card component
        - Animation controls: Handled by simulation_card component
    
    Validation:
        - Handled by simulation_form component
    
    Storage Functions Called:
        - get_stats(): Retrieve simulation statistics
        - get_all_simulations(): Retrieve all simulations
    """
    navbar()

    with ui.column().classes("w-full max-w-5xl mx-auto py-10 px-6 gap-6"):
        ui.label("Cache Simulations Dashboard").classes("text-3xl font-bold text-green-800")

        # --- Stats row ---
        stats = get_stats()
        # with ui.row().classes("gap-4 flex-wrap"):
        #     stats_card("Total",   sum(stats.values()),       "green")
        #     stats_card("Done",    stats.get("done", 0),      "green")
        #     stats_card("Running", stats.get("running", 0),   "yellow")

        ui.separator()

        # --- Simulation list (refreshable) - Define first so we can reference its refresh method ---
        @ui.refreshable
        def simulations_list():
            """Refreshable simulations list that updates when new simulations are added."""
            ui.label("Cache Simulations").classes("text-lg font-semibold text-green-700")

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
        simulations_list()

    footer()
