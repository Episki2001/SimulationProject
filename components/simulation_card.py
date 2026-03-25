import os
from datetime import datetime
from nicegui import ui
from backend.data import delete_simulation


def _generate_trace_log_file(sim):
    """Generate trace log content as a text file."""
    content = "=" * 80 + "\n"
    content += "CACHE SIMULATION TRACE LOG\n"
    content += "=" * 80 + "\n\n"
    
    # Header information
    content += f"Simulation Name: {sim.name}\n"
    content += f"Created:         {sim.created_at}\n"
    content += "\n"
    
    # Configuration
    content += "-" * 80 + "\n"
    content += "CONFIGURATION\n"
    content += "-" * 80 + "\n"
    
    if sim.associativity == 1:
        sim_type_text = "Direct Mapped"
    elif sim.associativity == 8 and sim.replacement_policy == "LRU":
        if sim.cache_blocks < 8:
            sim_type_text = "Full Associative LRU"
        else:
            sim_type_text = "8-Way Set Associative + LRU"
    else:
        sim_type_text = f"{sim.associativity}-way + {sim.replacement_policy}"
    
    content += f"Simulation Type:     {sim_type_text}\n"
    content += f"Memory Space:        1024 blocks\n"
    content += f"Cache Size:          {sim.cache_blocks} blocks\n"
    content += f"Block Size:          {sim.block_size} words\n"
    content += f"Cache Access Time:   {sim.cache_access_time} ns/block\n"
    content += f"Memory Access Time:  {sim.memory_access_time} ns/word\n"
    
    # Test pattern
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
    
    content += f"Test Pattern:        {pattern_text}\n"
    
    # Custom pattern details
    if sim.test_pattern == "custom" and sim.custom_pattern:
        content += f"\nCustom Pattern Access Sequence:\n"
        # Format in rows of 20 numbers
        for i in range(0, len(sim.custom_pattern), 20):
            chunk = sim.custom_pattern[i:i+20]
            content += "  " + ", ".join(map(str, chunk)) + "\n"
    
    content += "\n"
    
    # Results
    if sim.total_accesses > 0:
        content += "-" * 80 + "\n"
        content += "RESULTS\n"
        content += "-" * 80 + "\n"
        content += f"Total Accesses:      {sim.total_accesses}\n"
        content += f"Cache Hits:          {sim.cache_hits}\n"
        content += f"Cache Misses:        {sim.cache_misses}\n"
        content += f"Hit Rate:            {sim.hit_rate * 100:.2f}%\n"
        content += f"Miss Rate:           {sim.miss_rate * 100:.2f}%\n"
        content += f"Miss Penalty:        {sim.miss_penalty} ns\n"
        content += f"Avg Access Time:     {sim.avg_memory_access_time:.2f} ns\n"
        content += f"Total Access Time:   {sim.total_memory_access_time:.0f} ns\n"
        content += "\n"
    
    # Trace log
    content += "-" * 80 + "\n"
    content += "TRACE LOG\n"
    content += "-" * 80 + "\n"
    for i, trace_entry in enumerate(sim.trace_log, 1):
        content += f"{i:4d}. {trace_entry}\n"
    
    content += "\n" + "=" * 80 + "\n"
    content += "END OF TRACE LOG\n"
    content += "=" * 80 + "\n"
    
    return content.encode('utf-8')


def simulation_card(sim):
    """
    Display a complete simulation card with all details, results, and visualizations.
    """
    with ui.card().classes("p-4 rounded-lg shadow-sm w-full"):
        # Header row: ID and Name
        with ui.row().classes("items-center gap-4 mb-3 pb-3 border-b border-gray-200"):
            ui.label(f"#{sim.id}").classes("font-mono text-gray-400 w-8")
            ui.label(sim.name).classes("font-bold text-gray-800 flex-1 text-base")
        
        # Config row: Cache parameters (per CSC512C spec)
        with ui.row().classes("gap-6 items-start mb-3 text-sm flex-wrap"):
            with ui.column().classes("gap-1"):
                ui.label("Simulation Type:").classes("text-xs font-semibold text-gray-600")
                if sim.associativity == 1:
                    sim_type_text = "Direct Mapped"
                elif sim.associativity == 8 and sim.replacement_policy == "LRU":
                    if sim.cache_blocks < 8:
                        sim_type_text = "Full Associative LRU"
                    else:
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
        
        # Results row: Hit/Miss stats + timing
        if sim.total_accesses > 0:
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
            
            # Text-based Trace Log
            with ui.expansion("Trace Log", icon="article").classes("w-full mt-3"):
                if sim.trace_log and len(sim.trace_log) > 0:
                    # Create filename based on simulation name
                    safe_name = sim.name.replace(' ', '_').replace('/', '_').replace('\\', '_').replace(':', '_').replace('-', '_')
                    filename = f"{safe_name}.txt"
                    
                    ui.button("Download Trace Log", icon="download", 
                             on_click=lambda: ui.download(_generate_trace_log_file(sim), filename)) \
                        .props("flat size=sm color=blue") \
                        .classes("mb-2")
                    
                    with ui.column().classes("w-full gap-1 max-h-96 overflow-y-auto"):
                        for i, trace_entry in enumerate(sim.trace_log, 1):
                            # Color code based on HIT/MISS
                            if "HIT" in trace_entry:
                                color_class = "text-green-700"
                            elif "evicted" in trace_entry:
                                color_class = "text-red-700"
                            else:
                                color_class = "text-orange-700"
                            ui.label(f"{i}. {trace_entry}").classes(f"text-xs font-mono {color_class}")
                else:
                    ui.label("No trace log available").classes("text-xs text-gray-500")
            
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
            
            ui.button(
                icon="delete",
                on_click=lambda sid=sim.id: (delete_simulation(sid), ui.notify("Simulation deleted.", type="info"), ui.navigate.reload()),
            ).classes("text-red-400 hover:text-red-600").props("flat round")


class CacheAnimationViewer:
    """Interactive cache animation viewer with play controls and speed adjustment."""
    
    def __init__(self, sim_data):
        self.sim_data = sim_data
        self.step = 0
        self.playing = False
        self._generation = 0  # Track state changes to prevent race conditions
        self._current_play_generation = None  # Track which play session is current
        
        # Read max speed from environment variable (default to 2x)
        max_speed = float(os.getenv("ANIMATION_MAX_SPEED", "4"))
        # Generate speed multipliers: [0.25, 0.5, 1, 2, ...up to max_speed]
        self.speeds = [0.25, 0.5, 1]
        current = 2
        while current <= max_speed:
            self.speeds.append(current)
            current *= 2
        
        self.speed = 1  # Current speed (1x = normal)
        self.base_interval = 1.0  # Base interval in seconds
        self.interval = self.base_interval / self.speed
        self.timer = ui.timer(self.interval, self._timer_callback, active=False)
    
    @ui.refreshable
    def display(self):
        """Render the animation display with current state."""
        snapshot = self.sim_data.cache_snapshots[self.step]
        
        with ui.column().classes("w-full gap-3"):
            # Animation controls - Row 1: Play/Stop and navigation
            with ui.row().classes("items-center gap-3 flex-wrap"):
                ui.label(f"Step: {snapshot['step']} / {len(self.sim_data.cache_snapshots) - 1}").classes("text-sm font-semibold")
                
                if self.playing:
                    ui.button("⏸ Stop", on_click=self.stop_animation).props("size=sm color=orange")
                else:
                    ui.button("▶ Play", on_click=self.play_animation).props("size=sm color=green")
                
                ui.button("◀ Prev", on_click=self.go_prev).props("size=sm color=green flat")
                ui.button("Next ▶", on_click=self.go_next).props("size=sm color=green flat")
                ui.button("⟲ Reset", on_click=self.reset).props("size=sm color=green flat")
            
            # Animation controls - Row 2: Speed controls
            with ui.row().classes("items-center gap-2 flex-wrap"):
                ui.label("Speed:").classes("text-xs font-semibold text-gray-600")
                ui.button("🐢 Slow", on_click=self.decrease_speed).props("size=sm color=blue flat")
                ui.label(f"{self.speed}x").classes("text-sm font-semibold text-blue-700 px-2")
                ui.button("🐇 Fast", on_click=self.increase_speed).props("size=sm color=blue flat")
                ui.label(f"({self.interval:.2f}s/step)").classes("text-xs text-gray-500")
            
            # Calculate set information
            num_sets = 1 if (self.sim_data.associativity == 0 or self.sim_data.associativity > self.sim_data.cache_blocks) else (self.sim_data.cache_blocks // self.sim_data.associativity)
            accessed = snapshot["accessed_block"]
            accessed_set = accessed % num_sets if accessed is not None and num_sets > 0 else 0
            
            # Access info - handle initial step 0
            if accessed is None:
                ui.label("INITIAL STATE").classes("text-sm font-semibold text-blue-700")
            elif snapshot["is_hit"]:
                if self.sim_data.associativity == 8:
                    ui.label(f"✓ ACCESS Block {accessed} (Set {accessed_set}) - HIT!").classes("text-sm font-semibold text-green-700")
                else:
                    ui.label(f"✓ ACCESS Block {accessed} - HIT!").classes("text-sm font-semibold text-green-700")
            else:
                if snapshot["evicted_block"] is not None:
                    if self.sim_data.associativity == 8:
                        evicted_set = snapshot["evicted_block"] % num_sets if num_sets > 0 else 0
                        ui.label(f"✗ ACCESS Block {accessed} (Set {accessed_set}) - MISS (evicted Block {snapshot['evicted_block']} from Set {evicted_set})").classes("text-sm font-semibold text-red-700")
                    else:
                        ui.label(f"✗ ACCESS Block {accessed} - MISS (evicted Block {snapshot['evicted_block']})").classes("text-sm font-semibold text-red-700")
                else:
                    if self.sim_data.associativity == 8:
                        ui.label(f"✗ ACCESS Block {accessed} (Set {accessed_set}) - MISS (loaded)").classes("text-sm font-semibold text-orange-700")
                    else:
                        ui.label(f"✗ ACCESS Block {accessed} - MISS (loaded)").classes("text-sm font-semibold text-orange-700")
            
            # Cache visualization
            _display_cache_state(self.sim_data, snapshot, accessed, accessed_set, num_sets)
            
            ui.label(f"Stats: Hits: {snapshot['hits']} | Misses: {snapshot['misses']}").classes("text-sm mt-3 text-gray-700")
    
    def _timer_callback(self):
        """Timer callback with generation checking to prevent race conditions."""
        if self._current_play_generation is not None and self._generation != self._current_play_generation:
            return  # Ignore callbacks from previous play sessions
        self._auto_advance()
    
    def _create_checked_callback(self, generation):
        """Create a callback wrapper that validates generation before executing.
        
        This prevents race conditions by ensuring timer callbacks from previous
        animation sessions are ignored when controls are clicked rapidly.
        """
        def checked_auto_advance():
            if self._generation != generation:
                return
            self._auto_advance()
        return checked_auto_advance
    
    def go_prev(self):
        """Navigate to previous step."""
        self._generation += 1
        self.playing = False
        self.timer.active = False
        
        self.step = max(0, self.step - 1)
        self.display.refresh()
    
    def go_next(self):
        """Navigate to next step."""
        self._generation += 1
        self.playing = False
        self.timer.active = False
        
        self.step = min(len(self.sim_data.cache_snapshots) - 1, self.step + 1)
        self.display.refresh()
    
    def reset(self):
        """Reset to first step."""
        self._generation += 1
        self.playing = False
        self.timer.active = False
        
        self.step = 0
        self.display.refresh()
    
    def _auto_advance(self):
        """Auto-advance to next step during playback."""
        if not self.playing:
            return
            
        if self.step < len(self.sim_data.cache_snapshots) - 1:
            self.step += 1
            self.display.refresh()
        else:
            # Reached end - stop animation
            self.playing = False
            self.timer.active = False
            self.display.refresh()
    
    def play_animation(self):
        """Start animation playback."""
        if not self.playing:
            self._generation += 1
            self._current_play_generation = self._generation
            self.playing = True
            self.timer.interval = self.interval
            self.timer.active = True
    
    def stop_animation(self):
        """Stop animation playback."""
        # Set state first to prevent timer callbacks
        self._generation += 1
        self.playing = False
        self.timer.active = False
        self.display.refresh()
    
    def increase_speed(self):
        """Increase animation speed (decrease interval)."""
        current_speed_idx = self.speeds.index(self.speed)
        if current_speed_idx < len(self.speeds) - 1:
            self._generation += 1
            was_playing = self.playing
            self.playing = False
            self.timer.active = False
            
            # Update speed and interval
            self.speed = self.speeds[current_speed_idx + 1]
            self.interval = self.base_interval / self.speed
            
            # Refresh display with new speed before restarting timer
            self.display.refresh()
            
            # Restart if was playing
            if was_playing:
                self._current_play_generation = self._generation
                self.playing = True
                self.timer.interval = self.interval
                self.timer.active = True
    
    def decrease_speed(self):
        """Decrease animation speed (increase interval)."""
        current_speed_idx = self.speeds.index(self.speed)
        if current_speed_idx > 0:
            self._generation += 1
            was_playing = self.playing
            self.playing = False
            self.timer.active = False
            
            # Update speed and interval
            self.speed = self.speeds[current_speed_idx - 1]
            self.interval = self.base_interval / self.speed
            
            # Refresh display with new speed before restarting timer
            self.display.refresh()
            
            # Restart if was playing
            if was_playing:
                self._current_play_generation = self._generation
                self.playing = True
                self.timer.interval = self.interval
                self.timer.active = True


def _create_animation_viewer(sim_data):
    """Create interactive cache animation viewer with play controls and speed adjustment."""
    viewer = CacheAnimationViewer(sim_data)
    viewer.display()


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
        if sim_data.associativity == 8 and num_sets >= 1:
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
                
                # Cache miss - highlight accessed block in red (eviction or initial empty)
                if not snapshot.get("is_hit", True) and block == accessed:
                    bg_class = "bg-red-200"
                elif block == accessed:
                    bg_class = "bg-green-200"
                elif sim_data.associativity == 8 and block_set == accessed_set:
                    bg_class = "bg-blue-200"
                else:
                    bg_class = "bg-blue-100"
                
                display_text = f"[{i}] B{block}"
                if sim_data.associativity == 8:
                    display_text += f" Set{block_set}"
                
                ui.input(value=display_text).props("readonly dense outlined").classes(f"text-center {bg_class} font-semibold").style("max-width: 150px; font-size: 0.75rem;")
            else:
                ui.input(value=f"[{i}] —").props("readonly dense outlined").classes("text-center bg-white text-gray-400").style("max-width: 150px; font-size: 0.75rem;")


def _display_set_associative_cache(sim_data, cache_state, block_ages, accessed, accessed_set, snapshot, num_sets):
    """Display set-associative cache visualization."""
    age_map = {(item["set"], item["block_index"]): item["age"] for item in block_ages}
    
    for set_id in range(num_sets):
        bg_color = "bg-purple-50" if set_id == accessed_set else "bg-gray-50"
        with ui.card().classes(f"w-full p-3 {bg_color} mb-2"):
            ui.label(f"Set {set_id}:").classes("text-xs font-semibold text-purple-700 mb-2")
            with ui.grid(columns=8).classes("gap-2"):
                # Use actual cache_state size instead of associativity value
                blocks_per_set = len(cache_state[set_id]) if set_id < len(cache_state) else 0
                for block_idx in range(blocks_per_set):
                    block = cache_state[set_id][block_idx] if set_id < len(cache_state) and block_idx < len(cache_state[set_id]) else None
                    if block is not None:
                        age = age_map.get((set_id, block_idx), 0)
                        
                        if not snapshot.get("is_hit", True) and block == accessed:
                            bg_class = "bg-red-200"
                        elif block == accessed:
                            bg_class = "bg-green-200"
                        else:
                            bg_class = "bg-blue-100"
                        
                        with ui.card().classes(f"{bg_class} p-2").style("min-width: 100px; max-width: 120px;"):
                            ui.label(f"[{block_idx}] B{block}").classes("text-center font-semibold text-xs")
                            ui.label(f"age: {age}").classes("text-center text-xs")
                    else:
                        ui.input(value=f"[{block_idx}] —").props("readonly dense outlined").classes("text-center bg-white text-gray-400").style("max-width: 120px; font-size: 0.75rem;")


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
        num_sets = 1 if (sim.associativity == 0 or sim.associativity > sim.cache_blocks) else (sim.cache_blocks // sim.associativity)
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
            if sim.associativity == 8 and num_sets >= 1:
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
                # Use actual cache_array_final size instead of associativity value
                blocks_per_set = len(cache_array_final[set_id]) if set_id < len(cache_array_final) else 0
                for block_idx in range(blocks_per_set):
                    block = cache_array_final[set_id][block_idx] if set_id < len(cache_array_final) and block_idx < len(cache_array_final[set_id]) else None
                    if block is not None:
                        display_text = f"[{block_idx}] B{block}"
                        ui.input(value=display_text).props("readonly dense outlined").classes("text-center bg-blue-100 font-semibold").style("max-width: 120px; font-size: 0.75rem;")
                    else:
                        ui.input(value=f"[{block_idx}] —").props("readonly dense outlined").classes("text-center bg-white text-gray-400").style("max-width: 120px; font-size: 0.75rem;")


def _display_final_set_organization(sim, cache_array_final, is_direct_mapped, num_sets):
    """Display final blocks organized by sets (8-way only)."""
    ui.label(f"Blocks Organized by Sets:").classes("text-xs font-semibold text-gray-600 mt-3 mb-2")
    # Calculate actual blocks per set
    actual_blocks_per_set = min(sim.associativity, sim.cache_blocks) if sim.associativity > 1 else sim.associativity
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
                    ui.label(f"({len(blocks_in_set)}/{actual_blocks_per_set} blocks)").classes("text-xs text-gray-500 italic")
                else:
                    ui.label("empty").classes("text-xs text-gray-400 italic")
