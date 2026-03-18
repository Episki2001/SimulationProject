"""
simulation_card.py
------------------
Component for displaying individual simulation details with results and visualizations.

Displays simulation configuration, results, cache animation, and memory state.
"""

from datetime import datetime
from nicegui import ui
from backend.data import delete_simulation


STATUS_COLORS = {
    "done":    "text-green-600",
    "running": "text-yellow-600",
    "error":   "text-red-600",
}


def simulation_card(sim):
    """
    Display a complete simulation card with all details, results, and visualizations.
    
    Args:
        sim: Simulation object containing all simulation data and results
    
    Displays:
        - Header: ID, name, status
        - Configuration: type, memory space, cache size, block size, timings, test pattern
        - Custom pattern details (if applicable)
        - Results: hits, misses, rates, timing metrics (if completed)
        - Cache Animation: Step-by-step cache visualization with play controls
        - Final Cache Memory: Visual representation of final cache state
        - Footer: Created date and delete button
    """
    with ui.card().classes("p-4 rounded-lg shadow-sm w-full"):
        # Header row: ID, Name, Status
        with ui.row().classes("items-center gap-4 mb-3 pb-3 border-b border-gray-200"):
            ui.label(f"#{sim.id}").classes("font-mono text-gray-400 w-8")
            ui.label(sim.name).classes("font-bold text-gray-800 flex-1 text-base")
            ui.label(sim.status.upper()).classes(
                f"text-xs font-bold px-2 py-1 rounded "
                f"{STATUS_COLORS.get(sim.status, 'text-gray-500')}"
            )
        
        # Config row: Cache parameters (per CSC512C spec)
        with ui.row().classes("gap-6 items-start mb-3 text-sm flex-wrap"):
            with ui.column().classes("gap-1"):
                ui.label("Simulation Type:").classes("text-xs font-semibold text-gray-600")
                if sim.associativity == 1:
                    sim_type_text = "Direct Mapped"
                elif sim.associativity == 8 and sim.replacement_policy == "LRU":
                    sim_type_text = "8-Way Set Associative + LRU"
                else:
                    sim_type_text = f"{sim.associativity}-way + {sim.replacement_policy}"
                ui.label(sim_type_text).classes("text-gray-800 font-semibold")
            with ui.column().classes("gap-1"):
                ui.label("Memory Space:").classes("text-xs font-semibold text-gray-600")
                ui.label("1024 blocks").classes("text-gray-800")
            with ui.column().classes("gap-1"):
                ui.label("Cache Size:").classes("text-xs font-semibold text-gray-600")
                ui.label(f"{sim.cache_blocks} blocks").classes("text-gray-800")
            with ui.column().classes("gap-1"):
                ui.label("Block Size:").classes("text-xs font-semibold text-gray-600")
                ui.label(f"{sim.block_size} words").classes("text-gray-800")
            with ui.column().classes("gap-1"):
                ui.label("Cache Access Time:").classes("text-xs font-semibold text-gray-600")
                ui.label(f"{sim.cache_access_time} ns/block").classes("text-gray-800")
            with ui.column().classes("gap-1"):
                ui.label("Memory Access Time:").classes("text-xs font-semibold text-gray-600")
                ui.label(f"{sim.memory_access_time} ns/word").classes("text-gray-800")
            with ui.column().classes("gap-1"):
                ui.label("Test Pattern:").classes("text-xs font-semibold text-gray-600")
                if sim.test_pattern == "custom" and sim.custom_pattern:
                    pattern_text = f"custom ({len(sim.custom_pattern)} accesses)"
                elif sim.test_pattern == "sequential":
                    pattern_text = f"sequential ({4 * sim.cache_blocks} accesses)"
                elif sim.test_pattern == "mid_repeat":
                    n = sim.cache_blocks
                    base_length = 1 + 2 * (n - 1) + n
                    pattern_text = f"mid_repeat ({2 * base_length} accesses)"
                elif sim.test_pattern == "random":
                    random_len = getattr(sim, 'random_length', 64)
                    pattern_text = f"random ({random_len} accesses)"
                else:
                    pattern_text = sim.test_pattern
                ui.label(pattern_text).classes("text-gray-800")
        
        # Show custom pattern details if custom
        if sim.test_pattern == "custom" and sim.custom_pattern:
            with ui.expansion("Custom Pattern Details", icon="format_list_numbered").classes("w-full mt-2"):
                pattern_str = ", ".join(map(str, sim.custom_pattern[:50]))
                if len(sim.custom_pattern) > 50:
                    pattern_str += f"... and {len(sim.custom_pattern) - 50} more"
                ui.label(f"Access sequence: {pattern_str}").classes("text-xs font-mono text-gray-700")
        
        # Results row: Hit/Miss stats + timing (only if simulation ran)
        if sim.status == "done" and sim.total_accesses > 0:
            with ui.row().classes("gap-6 items-start text-sm flex-wrap"):
                with ui.column().classes("gap-1"):
                    ui.label("Accesses:").classes("text-xs font-semibold text-gray-600")
                    ui.label(f"{sim.total_accesses}").classes("text-gray-800")
                with ui.column().classes("gap-1"):
                    ui.label("Hits:").classes("text-xs font-semibold text-gray-600")
                    ui.label(f"{sim.cache_hits}").classes("text-green-700 font-semibold")
                with ui.column().classes("gap-1"):
                    ui.label("Misses:").classes("text-xs font-semibold text-gray-600")
                    ui.label(f"{sim.cache_misses}").classes("text-red-700 font-semibold")
                with ui.column().classes("gap-1"):
                    ui.label("Hit Rate:").classes("text-xs font-semibold text-gray-600")
                    hit_rate_pct = f"{sim.hit_rate * 100:.1f}%"
                    ui.label(hit_rate_pct).classes("text-green-700 font-semibold")
                with ui.column().classes("gap-1"):
                    ui.label("Miss Rate:").classes("text-xs font-semibold text-gray-600")
                    miss_rate_pct = f"{sim.miss_rate * 100:.1f}%"
                    ui.label(miss_rate_pct).classes("text-red-700 font-semibold")
                with ui.column().classes("gap-1"):
                    ui.label("Miss Penalty:").classes("text-xs font-semibold text-gray-600")
                    ui.label(f"{sim.miss_penalty} ns").classes("text-gray-800")
                with ui.column().classes("gap-1"):
                    ui.label("Avg Access Time:").classes("text-xs font-semibold text-gray-600")
                    ui.label(f"{sim.avg_memory_access_time:.2f} ns").classes("text-gray-800")
                with ui.column().classes("gap-1"):
                    ui.label("Total Access Time:").classes("text-xs font-semibold text-gray-600")
                    ui.label(f"{sim.total_memory_access_time:.0f} ns").classes("text-gray-800")
            
            # Animated Cache Visualization
            with ui.expansion("Cache Animation", icon="play_circle").classes("w-full mt-3"):
                if sim.cache_snapshots and len(sim.cache_snapshots) > 0:
                    _create_animation_viewer(sim)
                else:
                    ui.label("No animation data available").classes("text-xs text-gray-500")
            
            # Expandable final cache memory view
            with ui.expansion("Final Cache Memory", icon="database").classes("w-full mt-3"):
                if sim.final_cache_memory:
                    _display_final_cache_memory(sim)
                else:
                    ui.label("No cache memory (all misses or cache empty)").classes("text-xs text-gray-500")
        
        # Footer: Created date and delete button
        with ui.row().classes("items-center justify-between pt-3 border-t border-gray-100 text-xs"):
            created_dt = datetime.fromisoformat(sim.created_at)
            ui.label(created_dt.strftime("%Y-%m-%d %H:%M")).classes("text-gray-400")
            
            def make_delete(sid: int):
                def _delete():
                    delete_simulation(sid)
                    ui.notify("Simulation deleted.", type="info")
                    ui.navigate.reload()
                return _delete

            ui.button(
                icon="delete",
                on_click=make_delete(sim.id),
            ).classes("text-red-400 hover:text-red-600").props("flat round")


def _create_animation_viewer(sim_data):
    """Create interactive cache animation viewer with play controls and speed adjustment."""
    @ui.refreshable
    def animation_display():
        step_idx = animation_display.step
        snapshot = sim_data.cache_snapshots[step_idx]
        
        with ui.column().classes("w-full gap-3"):
            # Animation controls - Row 1: Play/Stop and navigation
            with ui.row().classes("items-center gap-3 flex-wrap"):
                ui.label(f"Step: {step_idx + 1} / {len(sim_data.cache_snapshots)}").classes("text-sm font-semibold")
                
                if animation_display.playing:
                    ui.button("⏸ Stop", on_click=lambda: stop_animation()).props("size=sm color=orange")
                else:
                    ui.button("▶ Play", on_click=lambda: play_animation()).props("size=sm color=green")
                
                ui.button("◀ Prev", on_click=lambda: go_prev()).props("size=sm color=green flat")
                ui.button("Next ▶", on_click=lambda: go_next()).props("size=sm color=green flat")
                ui.button("⟲ Reset", on_click=lambda: reset()).props("size=sm color=green flat")
            
            # Animation controls - Row 2: Speed controls
            with ui.row().classes("items-center gap-2 flex-wrap"):
                ui.label("Speed:").classes("text-xs font-semibold text-gray-600")
                ui.button("🐢 Slow", on_click=lambda: decrease_speed()).props("size=sm color=blue flat")
                ui.label(f"{animation_display.speed}x").classes("text-sm font-semibold text-blue-700 px-2")
                ui.button("🐇 Fast", on_click=lambda: increase_speed()).props("size=sm color=blue flat")
                ui.label(f"({animation_display.interval:.2f}s/step)").classes("text-xs text-gray-500")
            
            # Calculate set information
            num_sets = sim_data.cache_blocks // sim_data.associativity if sim_data.associativity > 0 else 1
            accessed = snapshot["accessed_block"]
            accessed_set = accessed % num_sets if num_sets > 0 else 0
            
            # Access info
            if snapshot["is_hit"]:
                if sim_data.associativity == 8:
                    ui.label(f"✓ ACCESS Block {accessed} (Set {accessed_set}) - HIT!").classes("text-sm font-semibold text-green-700")
                else:
                    ui.label(f"✓ ACCESS Block {accessed} - HIT!").classes("text-sm font-semibold text-green-700")
            else:
                if snapshot["evicted_block"] is not None:
                    if sim_data.associativity == 8:
                        evicted_set = snapshot["evicted_block"] % num_sets if num_sets > 0 else 0
                        ui.label(f"✗ ACCESS Block {accessed} (Set {accessed_set}) - MISS (evicted Block {snapshot['evicted_block']} from Set {evicted_set})").classes("text-sm font-semibold text-red-700")
                    else:
                        ui.label(f"✗ ACCESS Block {accessed} - MISS (evicted Block {snapshot['evicted_block']})").classes("text-sm font-semibold text-red-700")
                else:
                    if sim_data.associativity == 8:
                        ui.label(f"✗ ACCESS Block {accessed} (Set {accessed_set}) - MISS (loaded)").classes("text-sm font-semibold text-orange-700")
                    else:
                        ui.label(f"✗ ACCESS Block {accessed} - MISS (loaded)").classes("text-sm font-semibold text-orange-700")
            
            # Cache visualization
            _display_cache_state(sim_data, snapshot, accessed, accessed_set, num_sets)
            
            ui.label(f"Stats: Hits: {snapshot['hits']} | Misses: {snapshot['misses']}").classes("text-sm mt-3 text-gray-700")
    
    def go_prev():
        if animation_display.playing:
            animation_display.timer.active = False
            animation_display.playing = False
        animation_display.step = max(0, animation_display.step - 1)
        animation_display.refresh()
    
    def go_next():
        if animation_display.playing:
            animation_display.timer.active = False
            animation_display.playing = False
        animation_display.step = min(len(sim_data.cache_snapshots) - 1, animation_display.step + 1)
        animation_display.refresh()
    
    def reset():
        animation_display.step = 0
        if animation_display.playing:
            animation_display.timer.active = False
            animation_display.playing = False
        animation_display.refresh()
    
    def auto_advance():
        if animation_display.step < len(sim_data.cache_snapshots) - 1:
            animation_display.step += 1
            animation_display.refresh()
        else:
            # Reached end - stop animation
            animation_display.timer.active = False
            animation_display.playing = False
            ui.timer(0.05, lambda: animation_display.refresh(), once=True)
    
    def play_animation():
        if not animation_display.playing:
            animation_display.playing = True
            animation_display.timer.interval = animation_display.interval  # Ensure interval is set
            animation_display.timer.active = True
            animation_display.refresh()
    
    def stop_animation():
        # Always stop the timer first, regardless of state
        animation_display.timer.active = False
        animation_display.playing = False
        # Use a deferred refresh to avoid race conditions with button clicks
        ui.timer(0.05, lambda: animation_display.refresh(), once=True)
    
    def increase_speed():
        """Increase animation speed (decrease interval)."""
        current_speed_idx = animation_display.speeds.index(animation_display.speed)
        if current_speed_idx < len(animation_display.speeds) - 1:
            animation_display.speed = animation_display.speeds[current_speed_idx + 1]
            animation_display.interval = animation_display.base_interval / animation_display.speed
            
            # If playing, restart timer with new interval
            was_playing = animation_display.playing
            if was_playing:
                animation_display.timer.active = False
            
            animation_display.timer.interval = animation_display.interval
            
            if was_playing:
                animation_display.timer.active = True
            
            animation_display.refresh()
    
    def decrease_speed():
        """Decrease animation speed (increase interval)."""
        current_speed_idx = animation_display.speeds.index(animation_display.speed)
        if current_speed_idx > 0:
            animation_display.speed = animation_display.speeds[current_speed_idx - 1]
            animation_display.interval = animation_display.base_interval / animation_display.speed
            
            # If playing, restart timer with new interval
            was_playing = animation_display.playing
            if was_playing:
                animation_display.timer.active = False
            
            animation_display.timer.interval = animation_display.interval
            
            if was_playing:
                animation_display.timer.active = True
            
            animation_display.refresh()
    
    # Initialize animation state
    animation_display.step = 0
    animation_display.playing = False
    animation_display.speeds = [0.25, 0.5, 1, 2, 4]  # Speed multipliers
    animation_display.speed = 1  # Current speed (1x = normal)
    animation_display.base_interval = 1.0  # Base interval in seconds
    animation_display.interval = animation_display.base_interval / animation_display.speed
    animation_display.timer = ui.timer(animation_display.interval, auto_advance, active=False)
    animation_display()


def _display_cache_state(sim_data, snapshot, accessed, accessed_set, num_sets):
    """Display cache state visualization for animation snapshots."""
    with ui.card().classes("w-full p-4 bg-gray-50"):
        if sim_data.associativity == 8:
            ui.label(f"Cache State: {sim_data.associativity}-way Set Associative ({num_sets} sets)").classes("text-xs font-semibold text-gray-600 mb-2")
        elif sim_data.associativity > 1:
            ui.label(f"Cache State: {sim_data.associativity}-way Set Associative").classes("text-xs font-semibold text-gray-600 mb-2")
        else:
            ui.label("Cache State: Direct Mapped").classes("text-xs font-semibold text-gray-600 mb-2")
        
        cache_state = snapshot["cache_state"]
        block_ages = snapshot.get("block_ages", [])
        is_direct_mapped = snapshot.get("is_direct_mapped", sim_data.associativity == 1)
        
        if is_direct_mapped:
            _display_direct_mapped_cache(sim_data, cache_state, block_ages, accessed, accessed_set, snapshot, num_sets)
        else:
            _display_set_associative_cache(sim_data, cache_state, block_ages, accessed, accessed_set, snapshot, num_sets)
        
        # Show set organization only for 8-way
        if sim_data.associativity == 8 and num_sets > 1:
            _display_set_organization(cache_state, is_direct_mapped, num_sets, accessed_set)


def _display_direct_mapped_cache(sim_data, cache_state, block_ages, accessed, accessed_set, snapshot, num_sets):
    """Display direct-mapped cache visualization."""
    age_map = {item["position"]: item["age"] for item in block_ages}
    
    with ui.grid(columns=8).classes("gap-2"):
        for i in range(sim_data.cache_blocks):
            block = cache_state[i] if i < len(cache_state) else None
            if block is not None:
                age = age_map.get(i, 0)
                block_set = block % num_sets if num_sets > 0 else 0
                
                if block == accessed:
                    bg_class = "bg-green-200"
                elif snapshot.get("evicted_block") is not None and block == snapshot.get("evicted_block"):
                    bg_class = "bg-red-200"
                elif sim_data.associativity == 8 and block_set == accessed_set:
                    bg_class = "bg-blue-200"
                else:
                    bg_class = "bg-blue-100"
                
                display_text = f"[{i}] B{block}"
                if sim_data.associativity == 8:
                    display_text += f" Set{block_set}"
                
                ui.input(value=display_text).props("readonly dense outlined").classes(f"text-center {bg_class} font-semibold").style("max-width: 120px; font-size: 0.75rem;")
            else:
                ui.input(value=f"[{i}] —").props("readonly dense outlined").classes("text-center bg-white text-gray-400").style("max-width: 120px; font-size: 0.75rem;")


def _display_set_associative_cache(sim_data, cache_state, block_ages, accessed, accessed_set, snapshot, num_sets):
    """Display set-associative cache visualization."""
    age_map = {(item["set"], item["block_index"]): item["age"] for item in block_ages}
    
    for set_id in range(num_sets):
        bg_color = "bg-purple-50" if set_id == accessed_set else "bg-gray-50"
        with ui.card().classes(f"w-full p-3 {bg_color} mb-2"):
            ui.label(f"Set {set_id}:").classes("text-xs font-semibold text-purple-700 mb-2")
            with ui.grid(columns=8).classes("gap-2"):
                for block_idx in range(sim_data.associativity):
                    block = cache_state[set_id][block_idx] if set_id < len(cache_state) and block_idx < len(cache_state[set_id]) else None
                    if block is not None:
                        age = age_map.get((set_id, block_idx), 0)
                        
                        if block == accessed:
                            bg_class = "bg-green-200"
                        elif snapshot.get("evicted_block") is not None and block == snapshot.get("evicted_block"):
                            bg_class = "bg-red-200"
                        else:
                            bg_class = "bg-blue-100"
                        
                        display_text = f"[{block_idx}] B{block} age:{age}"
                        ui.input(value=display_text).props("readonly dense outlined").classes(f"text-center {bg_class} font-semibold").style("max-width: 150px; font-size: 0.75rem;")
                    else:
                        ui.input(value=f"[{block_idx}] —").props("readonly dense outlined").classes("text-center bg-white text-gray-400").style("max-width: 150px; font-size: 0.75rem;")


def _display_set_organization(cache_state, is_direct_mapped, num_sets, accessed_set):
    """Display blocks organized by sets (8-way only)."""
    ui.label(f"Blocks by Set:").classes("text-xs font-semibold text-gray-600 mt-3 mb-1")
    with ui.row().classes("gap-2 flex-wrap"):
        for set_id in range(num_sets):
            if is_direct_mapped:
                blocks_in_set = [b for b in cache_state if b is not None and b % num_sets == set_id]
            else:
                blocks_in_set = [b for b in cache_state[set_id] if b is not None]
            
            bg_color = "bg-purple-100" if set_id == accessed_set else "bg-gray-100"
            with ui.card().classes(f"p-2 {bg_color}"):
                ui.label(f"Set {set_id}:").classes("text-xs font-semibold text-gray-700")
                if blocks_in_set:
                    ui.label(f"{blocks_in_set}").classes("text-xs text-gray-600")
                else:
                    ui.label("empty").classes("text-xs text-gray-400 italic")


def _display_final_cache_memory(sim):
    """Display final cache memory state."""
    with ui.column().classes("w-full gap-3"):
        cache_array_final = sim.final_cache_memory
        num_sets = sim.cache_blocks // sim.associativity if sim.associativity > 0 else 1
        is_direct_mapped = (sim.associativity == 1)
        
        # Count non-None blocks
        if is_direct_mapped:
            num_blocks_in_cache = sum(1 for b in cache_array_final if b is not None)
        else:
            num_blocks_in_cache = sum(1 for set_array in cache_array_final for b in set_array if b is not None)
        
        ui.label(f"Total blocks in cache: {num_blocks_in_cache} / {sim.cache_blocks}").classes("text-sm font-semibold text-gray-700")
        
        # Visual cache display
        with ui.card().classes("w-full p-4 bg-gray-50"):
            if sim.associativity == 8:
                ui.label(f"Final Cache State: {sim.associativity}-way Set Associative ({num_sets} sets)").classes("text-xs font-semibold text-gray-600 mb-2")
            elif sim.associativity > 1:
                ui.label(f"Final Cache State: {sim.associativity}-way Set Associative").classes("text-xs font-semibold text-gray-600 mb-2")
            else:
                ui.label("Final Cache State: Direct Mapped").classes("text-xs font-semibold text-gray-600 mb-2")
            
            if is_direct_mapped:
                _display_final_direct_mapped(sim, cache_array_final, num_sets)
            else:
                _display_final_set_associative(sim, cache_array_final, num_sets)
            
            # Show by set only for 8-way
            if sim.associativity == 8 and num_sets > 1:
                _display_final_set_organization(sim, cache_array_final, is_direct_mapped, num_sets)


def _display_final_direct_mapped(sim, cache_array_final, num_sets):
    """Display final state of direct-mapped cache."""
    with ui.grid(columns=8).classes("gap-2"):
        for i in range(sim.cache_blocks):
            block = cache_array_final[i] if i < len(cache_array_final) else None
            if block is not None:
                block_set = block % num_sets if num_sets > 0 else 0
                display_text = f"[{i}] B{block}"
                if sim.associativity == 8:
                    display_text += f" Set{block_set}"
                ui.input(value=display_text).props("readonly dense outlined").classes("text-center bg-blue-100 font-semibold").style("max-width: 120px; font-size: 0.75rem;")
            else:
                ui.input(value=f"[{i}] —").props("readonly dense outlined").classes("text-center bg-white text-gray-400").style("max-width: 120px; font-size: 0.75rem;")


def _display_final_set_associative(sim, cache_array_final, num_sets):
    """Display final state of set-associative cache."""
    for set_id in range(num_sets):
        with ui.card().classes("w-full p-3 bg-purple-50 mb-2"):
            ui.label(f"Set {set_id}:").classes("text-xs font-semibold text-purple-700 mb-2")
            with ui.grid(columns=8).classes("gap-2"):
                for block_idx in range(sim.associativity):
                    block = cache_array_final[set_id][block_idx] if set_id < len(cache_array_final) and block_idx < len(cache_array_final[set_id]) else None
                    if block is not None:
                        display_text = f"[{block_idx}] B{block}"
                        ui.input(value=display_text).props("readonly dense outlined").classes("text-center bg-blue-100 font-semibold").style("max-width: 120px; font-size: 0.75rem;")
                    else:
                        ui.input(value=f"[{block_idx}] —").props("readonly dense outlined").classes("text-center bg-white text-gray-400").style("max-width: 120px; font-size: 0.75rem;")


def _display_final_set_organization(sim, cache_array_final, is_direct_mapped, num_sets):
    """Display final blocks organized by sets (8-way only)."""
    ui.label(f"Blocks Organized by Sets:").classes("text-xs font-semibold text-gray-600 mt-3 mb-2")
    with ui.row().classes("gap-2 flex-wrap"):
        for set_id in range(num_sets):
            if is_direct_mapped:
                blocks_in_set = [b for b in cache_array_final if b is not None and b % num_sets == set_id]
            else:
                blocks_in_set = [b for b in cache_array_final[set_id] if b is not None]
            
            with ui.card().classes("p-2 bg-purple-50 border border-purple-300"):
                ui.label(f"Set {set_id}:").classes("text-xs font-semibold text-purple-700")
                if blocks_in_set:
                    ui.label(f"{blocks_in_set}").classes("text-xs text-gray-700")
                    ui.label(f"({len(blocks_in_set)}/{sim.associativity} blocks)").classes("text-xs text-gray-500 italic")
                else:
                    ui.label("empty").classes("text-xs text-gray-400 italic")
