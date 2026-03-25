import math
from datetime import datetime
from nicegui import ui
from backend.data import add_simulation


def is_power_of_2(n: int) -> bool:
    """Check if a number is a power of 2."""
    if n <= 0:
        return False
    return math.log2(n) % 1 == 0


def simulation_form(on_success=None):
    """
    Display the simulation creation form with all configuration options.
    """
    ui.label("Add New Cache Simulation").classes("text-lg font-semibold text-green-700")
    
    with ui.column().classes("w-full gap-4 p-4 bg-green-50 rounded-lg"):
        # Basic info
        name_input = ui.input(label="Simulation Name", placeholder="e.g., L1 Direct-Mapped").classes("w-full")
        
        # Simulation type selection
        sim_type_select = ui.select(
            label="Simulation Type",
            value="direct_mapped",
            options={
                "direct_mapped": "Direct Mapped",
                "8way_lru": "8-Way Block Set Associative + LRU"
            }
        ).classes("w-full")
        
        # Memory configuration info
        with ui.card().classes("p-3 bg-blue-50 border-l-4 border-blue-500"):
            ui.label("Memory Configuration").classes("font-semibold text-blue-900 text-sm mb-1")
            with ui.row().classes("gap-6 text-xs text-blue-800"):
                ui.label("📦 Total Memory Space: 1024 blocks ")
                ui.label("💾 Cache Size: Configurable below (holds subset of memory)")
        
        # Cache configuration 
        with ui.row().classes("w-full gap-4"):
            cache_blocks_input = ui.number(label="Cache Blocks (power-of-2, min 4, max 512)", value=4).classes("flex-1")
            block_size_input = ui.number(label="Block Size in words (power-of-2, min 2)", value=2).classes("flex-1")
        
        # Timing configuration
        with ui.row().classes("w-full gap-4"):
            cache_access_time_input = ui.number(label="Cache Access Time (ns per block)", value=1).classes("flex-1")
            memory_access_time_input = ui.number(label="Memory Access Time (ns per word)", value=10).classes("flex-1")
        
        # Test pattern selection
        pattern_select = ui.select(
            label="Test Pattern",
            value="sequential",
            options=["sequential", "mid_repeat", "random", "custom"]
        ).classes("w-full")
        
        # Custom pattern input (shown only when custom is selected)
        custom_pattern_input = ui.input(
            label="Custom Pattern (comma-separated block numbers, e.g., 0,1,2,3,0,1)",
            placeholder="Enter memory blocks: 0,1,5,10,..."
        ).classes("w-full")
        custom_pattern_input.set_visibility(False)
        
        # Random pattern length input (shown only when random is selected)
        random_length_input = ui.number(
            label="Random Pattern Length (number of accesses)",
            value=64
        ).classes("w-full")
        random_length_input.set_visibility(False)
        
        def on_pattern_change():
            is_custom = pattern_select.value == "custom"
            is_random = pattern_select.value == "random"
            custom_pattern_input.set_visibility(is_custom)
            random_length_input.set_visibility(is_random)
        
        pattern_select.on_value_change(on_pattern_change)
        on_pattern_change()  # Initialize visibility
        
        def on_add():
            # Auto-generate simulation name if not provided
            name = name_input.value.strip()
            if not name:
                # Generate name based on simulation type and timestamp
                sim_type = sim_type_select.value
                if sim_type == "direct_mapped":
                    sim_type_text = "Direct Mapped"
                elif sim_type == "8way_lru":
                    # Check if cache blocks < 8 to determine if it's fully associative
                    try:
                        cache_blocks = int(cache_blocks_input.value)
                        if cache_blocks < 8:
                            sim_type_text = "Full Associative LRU"
                        else:
                            sim_type_text = "8-Way LRU"
                    except (ValueError, TypeError):
                        sim_type_text = "8-Way LRU"
                else:
                    sim_type_text = "Simulation"
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                name = f"{sim_type_text} - {timestamp}"
            
            # Validate cache configuration
            try:
                cache_blocks = int(cache_blocks_input.value)
            except (ValueError, TypeError):
                ui.notify("Cache blocks must be a valid number.", type="warning")
                return
            
            try:
                block_size = int(block_size_input.value)
            except (ValueError, TypeError):
                ui.notify("Block size must be a valid number.", type="warning")
                return
            
            # Validate cache blocks is power of 2
            if not is_power_of_2(cache_blocks):
                ui.notify(f"Cache blocks must be a power of 2 (e.g., 4, 8, 16, 32, 64...).", type="warning")
                return
            
            # Validate cache blocks minimum
            if cache_blocks < 4:
                ui.notify(f"Cache blocks must be at least 4. Got: {cache_blocks}", type="warning")
                return
            
            # Validate cache blocks maximum
            if cache_blocks > 512:
                ui.notify(f"Cache blocks must be at most 512. Got: {cache_blocks}", type="warning")
                return
            
            # Validate block size is power of 2
            if not is_power_of_2(block_size):
                ui.notify(f"Block size must be a power of 2 (e.g., 2, 4, 8, 16, 32...).", type="warning")
                return
            
            # Validate block size minimum
            if block_size < 2:
                ui.notify(f"Block size must be at least 2. Got: {block_size}", type="warning")
                return
            
            # Validate timing parameters
            try:
                cache_access_time = int(cache_access_time_input.value)
            except (ValueError, TypeError):
                ui.notify("Cache access time must be a valid number.", type="warning")
                return
            
            try:
                memory_access_time = int(memory_access_time_input.value)
            except (ValueError, TypeError):
                ui.notify("Memory access time must be a valid number.", type="warning")
                return
            
            if cache_access_time < 1 or cache_access_time > 100:
                ui.notify(f"Cache access time must be between 1 and 100 ns. Got: {cache_access_time}", type="warning")
                return
            
            if memory_access_time < 1 or memory_access_time > 1000:
                ui.notify(f"Memory access time must be between 1 and 1000 ns. Got: {memory_access_time}", type="warning")
                return
            
            # Determine associativity and policy based on simulation type
            sim_type = sim_type_select.value
            if sim_type == "direct_mapped":
                associativity = 1
                replacement_policy = "LRU"  # Not used for direct-mapped, but set for consistency
            elif sim_type == "8way_lru":
                associativity = 8
                replacement_policy = "LRU"
            else:
                ui.notify("Invalid simulation type.", type="warning")
                return
            
            # Parse custom pattern if selected
            custom_pattern = []
            if pattern_select.value == "custom":
                pattern_str = custom_pattern_input.value.strip()
                if not pattern_str:
                    ui.notify("Please enter a custom pattern for custom test pattern.", type="warning")
                    return
                try:
                    custom_pattern = [int(x.strip()) for x in pattern_str.split(",") if x.strip()]
                    if not custom_pattern:
                        ui.notify("Custom pattern cannot be empty.", type="warning")
                        return
                    # Validate block numbers are within range 0-1023
                    if any(b < 0 or b > 1023 for b in custom_pattern):
                        ui.notify("Block numbers in custom pattern must be between 0 and 1023.", type="warning")
                        return
                except ValueError:
                    ui.notify("Invalid custom pattern format. Use comma-separated integers (e.g., 0,1,5,10).", type="warning")
                    return
            
            # Get random pattern length
            try:
                random_length = int(random_length_input.value) if pattern_select.value == "random" else 64
            except (ValueError, TypeError):
                ui.notify("Random pattern length must be a valid number.", type="warning")
                return
            
            if random_length < 1:
                ui.notify("Random pattern length must be at least 1.", type="warning")
                return
            
            try:
                add_simulation(
                    name=name,
                    cache_blocks=cache_blocks,
                    block_size=block_size,
                    associativity=associativity,
                    replacement_policy=replacement_policy,
                    test_pattern=pattern_select.value,
                    custom_pattern=custom_pattern,
                    random_length=random_length,
                    cache_access_time=cache_access_time,
                    memory_access_time=memory_access_time
                )
                ui.notify(f'"{name}" created successfully!', type="positive")
                # Clear only the name input to allow easy creation of similar simulations
                name_input.set_value("")
                # Trigger the simulations list refresh if callback provided
                if on_success:
                    on_success()
            except Exception as e:
                ui.notify(f"Error creating simulation: {str(e)}", type="negative")

        ui.button("Create Simulation", on_click=on_add).classes(
            "bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 font-semibold w-full"
        )
