"""
backend/simulation.py
---------------------
Cache simulation engine implementing CSC512C spec:
- Fixed 1024 memory blocks
- Three test patterns: sequential, mid_repeat, random
- Non load-through read policy
- Computes: hit rate, miss rate, avg/total access time

Authors:
    - Kimberly Claire H. Gamboa
    - Andre Emmanuel S. Garcia
"""

from __future__ import annotations

import random
from typing import Generator

from backend.data import CacheSimulation, get_simulation, _load_store, _save_store


class CacheSimulator:
    """Simulates a cache with given configuration per CSC512C spec."""

    def __init__(self, sim: CacheSimulation):
        self.sim = sim
        self.block_ages: dict[int, int] = {}  # track age of each block for visualization
        self.lru_order: dict[int, list[int]] = {}  # LRU order per set: {set_id: [blocks in LRU order]}
        self.fifo_order: dict[int, list[int]] = {}  # FIFO order per set: {set_id: [blocks in FIFO order]}
        self.access_trace: list[str] = []  # step-by-step trace log
        self.cache_snapshots: list[dict] = []  # cache state at each step
        self.hit_count = 0
        self.miss_count = 0
        self.access_count = 0  # total accesses (for age calculation)
        # Timing: hit_time = cache_access_time
        # miss_penalty = cache_access (check) + memory_access (fetch) + cache_access (write) - explicit for load-through option
        self.hit_time = sim.cache_access_time
        self.miss_penalty = sim.cache_access_time + (sim.block_size * sim.memory_access_time) + sim.cache_access_time
        # Store miss_penalty in simulation object for reference
        sim.miss_penalty = self.miss_penalty
        
        # Cache array structure:
        # - Direct-mapped (associativity == 1): 1D array [position] = block
        # - Set-associative (associativity > 1): 2D array [set_id][block_index] = block
        num_sets = self.get_num_sets()
        self.blocks_per_set = sim.associativity
        self.is_direct_mapped = (sim.associativity == 1)
        
        if self.is_direct_mapped:
            # 1D array for direct-mapped
            self.cache_array: list[int | None] | list[list[int | None]] = [None] * sim.cache_blocks
        else:
            # 2D array for set-associative: [set_id][way_index]
            self.cache_array = [[None] * self.blocks_per_set for _ in range(num_sets)]
        
        # Initialize LRU/FIFO tracking per set
        for set_id in range(num_sets):
            self.lru_order[set_id] = []
            self.fifo_order[set_id] = []

    def get_num_sets(self) -> int:
        """Calculate number of cache sets."""
        if self.sim.associativity == 0 or self.sim.associativity > self.sim.cache_blocks:
            return 1  # Fully associative
        return self.sim.cache_blocks // self.sim.associativity

    def get_set_id(self, block: int) -> int:
        """Get set ID for a memory block."""
        num_sets = self.get_num_sets()
        return block % num_sets if num_sets > 0 else 0

    def get_set_positions(self, set_id: int) -> list[int] | list[tuple[int, int]]:
        """Get cache array positions for a given set.
        Returns list of positions (int) for direct-mapped, or list of (set_id, block_index) tuples for set-associative.
        """
        if self.is_direct_mapped:
            # For direct-mapped, each set has only one position
            positions = []
            for block_idx in range(self.sim.associativity):
                pos = set_id * self.sim.associativity + block_idx
                if pos < self.sim.cache_blocks:
                    positions.append(pos)
            return positions
        else:
            # For set-associative, return (set_id, block_index) tuples
            return [(set_id, block_idx) for block_idx in range(self.blocks_per_set)]
    
    def find_block_position(self, block: int) -> int | tuple[int, int] | None:
        """Find the cache position of a block, or None if not in cache.
        Returns position (int) for direct-mapped, or (set_id, block_index) tuple for set-associative.
        """
        if self.is_direct_mapped:
            for pos, cached_block in enumerate(self.cache_array):
                if cached_block == block:
                    return pos
            return None
        else:
            # For set-associative, search in the appropriate set
            set_id = self.get_set_id(block)
            for block_idx, cached_block in enumerate(self.cache_array[set_id]):
                if cached_block == block:
                    return (set_id, block_idx)
            return None
    
    def find_empty_position_in_set(self, set_id: int) -> int | tuple[int, int] | None:
        """Find an empty position in the set, or None if full.
        Returns position (int) for direct-mapped, or (set_id, block_index) tuple for set-associative.
        """
        if self.is_direct_mapped:
            positions = self.get_set_positions(set_id)
            for pos in positions:
                if self.cache_array[pos] is None:
                    return pos
            return None
        else:
            # For set-associative, search for None in the set
            for block_idx in range(self.blocks_per_set):
                if self.cache_array[set_id][block_idx] is None:
                    return (set_id, block_idx)
            return None
    
    def get_blocks_in_set(self, set_id: int) -> list[int]:
        """Get all blocks currently in a set."""
        if self.is_direct_mapped:
            positions = self.get_set_positions(set_id)
            blocks = []
            for pos in positions:
                if self.cache_array[pos] is not None:
                    blocks.append(self.cache_array[pos])
            return blocks
        else:
            # For set-associative, get all non-None blocks in the set
            return [block for block in self.cache_array[set_id] if block is not None]

    def evict_from_set(self, set_id: int) -> tuple[int, int | tuple[int, int]] | None:
        """Evict a block from the set. Returns (block, position) or None.
        Position is int for direct-mapped, (set_id, block_index) tuple for set-associative.
        """
        if self.sim.replacement_policy == "LRU":
            # Find the least recently used block in this set
            lru_list = self.lru_order.get(set_id, [])
            if lru_list:
                lru_block = lru_list[0]  # First in list is LRU
                pos = self.find_block_position(lru_block)
                if pos is not None:
                    return lru_block, pos
        
        elif self.sim.replacement_policy == "FIFO":
            # Find the first block added to this set
            fifo_list = self.fifo_order.get(set_id, [])
            if fifo_list:
                fifo_block = fifo_list[0]
                pos = self.find_block_position(fifo_block)
                if pos is not None:
                    return fifo_block, pos
        
        # Fallback: evict first non-empty position in set
        if self.is_direct_mapped:
            positions = self.get_set_positions(set_id)
            for pos in positions:
                if self.cache_array[pos] is not None:
                    return self.cache_array[pos], pos
        else:
            for block_idx in range(self.blocks_per_set):
                if self.cache_array[set_id][block_idx] is not None:
                    return self.cache_array[set_id][block_idx], (set_id, block_idx)
        
        return None

    def access_block(self, block: int) -> bool:
        """
        Access a memory block. Returns True if hit, False if miss.
        Non load-through: if block is in cache, stays; if not, may be loaded.
        """
        self.access_count += 1  # Increment total access count
        set_id = self.get_set_id(block)
        
        # For set-associative caches: increment age of all blocks by 1 before processing
        if not self.is_direct_mapped:
            for existing_block in list(self.block_ages.keys()):
                self.block_ages[existing_block] += 1
        
        # Check if block is in cache
        pos = self.find_block_position(block)
        if pos is not None:
            # Cache hit
            if self.sim.replacement_policy == "LRU":
                # Update LRU order: move to end (most recently used)
                lru_list = self.lru_order[set_id]
                if block in lru_list:
                    lru_list.remove(block)
                lru_list.append(block)
            
            # Reset age to 0 for set-associative caches on hit 
            if not self.is_direct_mapped:
                self.block_ages[block] = 0
            
            self.hit_count += 1
            pos_str = str(pos) if self.is_direct_mapped else f"set {pos[0]}, block {pos[1]}"
            self.access_trace.append(f"Block {block}: HIT (in cache {pos_str})")
            self._capture_snapshot(block, True, None)
            return True

        # Cache miss - need to load block
        evicted_block = None
        empty_pos = self.find_empty_position_in_set(set_id)
        
        if empty_pos is not None:
            # Set has space - load into empty position
            if self.is_direct_mapped:
                self.cache_array[empty_pos] = block
                pos_str = str(empty_pos)
            else:
                self.cache_array[empty_pos[0]][empty_pos[1]] = block
                pos_str = f"set {empty_pos[0]}, block {empty_pos[1]}"
            
            # Set age to 0 for newly loaded block (already incremented all others above)
            self.block_ages[block] = 0
            self.access_trace.append(f"Block {block}: MISS - loaded into {pos_str}")
        else:
            # Need to evict
            eviction_result = self.evict_from_set(set_id)
            if eviction_result:
                evicted_block, evict_pos = eviction_result
                
                # Remove from tracking
                if evicted_block in self.block_ages:
                    del self.block_ages[evicted_block]
                if self.sim.replacement_policy == "LRU" and evicted_block in self.lru_order[set_id]:
                    self.lru_order[set_id].remove(evicted_block)
                if self.sim.replacement_policy == "FIFO" and evicted_block in self.fifo_order[set_id]:
                    self.fifo_order[set_id].remove(evicted_block)
                
                # Load new block into evicted position
                if self.is_direct_mapped:
                    self.cache_array[evict_pos] = block
                    pos_str = str(evict_pos)
                else:
                    self.cache_array[evict_pos[0]][evict_pos[1]] = block
                    pos_str = f"set {evict_pos[0]}, block {evict_pos[1]}"
                
                # Set age to 0 for newly loaded block (already incremented all others above)
                self.block_ages[block] = 0
                self.access_trace.append(f"Block {block}: MISS - evicted block {evicted_block} from {pos_str}")
        
        # Update tracking for new block
        if self.sim.replacement_policy == "LRU":
            self.lru_order[set_id].append(block)
        if self.sim.replacement_policy == "FIFO":
            self.fifo_order[set_id].append(block)

        self.miss_count += 1
        self._capture_snapshot(block, False, evicted_block)
        return False
    
    def _capture_snapshot(self, accessed_block: int, is_hit: bool, evicted_block: int | None):
        """Capture the current cache state for animation."""
        # Create age information for visualization (for blocks that are in cache)
        block_age_info = []
        
        if self.is_direct_mapped:
            # For direct-mapped: iterate over 1D array
            for pos, block in enumerate(self.cache_array):
                if block is not None:
                    age = self.access_count - self.block_ages.get(block, self.access_count)
                    block_age_info.append({"position": pos, "block": block, "age": age})
            
            # Cache state as 1D position-indexed array
            cache_state = self.cache_array.copy()
            # Also provide non-None blocks for compatibility
            cache_blocks_list = [b for b in self.cache_array if b is not None]
        else:
            # For set-associative: iterate over 2D array
            for set_id, set_array in enumerate(self.cache_array):
                for block_idx, block in enumerate(set_array):
                    if block is not None:
                        # Use the actual age stored in block_ages (already incremented properly)
                        age = self.block_ages.get(block, 0)
                        block_age_info.append({"set": set_id, "block_index": block_idx, "block": block, "age": age})
            
            # Cache state as 2D array (deep copy)
            cache_state = [set_array.copy() for set_array in self.cache_array]
            # Also provide non-None blocks for compatibility
            cache_blocks_list = [block for set_array in self.cache_array for block in set_array if block is not None]
        
        snapshot = {
            "step": len(self.cache_snapshots) + 1,
            "accessed_block": accessed_block,
            "is_hit": is_hit,
            "evicted_block": evicted_block,
            "cache_state": cache_state,  # 1D array (direct-mapped) or 2D array (set-associative)
            "cache_state_sorted": sorted(cache_blocks_list),  # Non-None blocks sorted
            "block_ages": block_age_info,  # Age information for each block with position/set/block_index
            "is_direct_mapped": self.is_direct_mapped,  # Flag for UI to determine structure
            "hits": self.hit_count,
            "misses": self.miss_count
        }
        self.cache_snapshots.append(snapshot)


def generate_sequential_pattern(cache_blocks: int) -> Generator[int, None, None]:
    """
    Sequential pattern: 0 to 2n-1, repeated twice.
    Example (n=4): 0,1,2,3,4,5,6,7,0,1,2,3,4,5,6,7
    Total accesses: 4n
    """
    pattern = list(range(2 * cache_blocks))
    # Repeat the sequence two times
    for _ in range(2):
        yield from pattern


def generate_mid_repeat_pattern(cache_blocks: int) -> Generator[int, None, None]:
    """
    Mid-repeat pattern: Start at 0, repeat the sequence in the middle (1 to n-1) twice,
    continue to 2n-1. Then repeat the entire sequence two times.
    Example (n=4): 0,1,2,3,1,2,3,4,5,6,7, 0,1,2,3,1,2,3,4,5,6,7
    """
    # Build the base sequence: 0, [1 to n-1] twice, [n to 2n-1]
    n = cache_blocks
    base_sequence = [0] + list(range(1, n)) * 2 + list(range(n, 2 * n))
    
    # Repeat the entire sequence two times
    for _ in range(2):
        yield from base_sequence


def generate_random_pattern(length: int = 64) -> Generator[int, None, None]:
    """
    Random pattern: generates specified number of main memory blocks from range 0-1023.
    Default: 64 accesses.
    """
    # random.seed(42)  # Reproducible
    for _ in range(length):
        yield random.randint(0, 1023)


def generate_custom_pattern(pattern: list[int]) -> Generator[int, None, None]:
    """
    Custom pattern: user-defined sequence of memory blocks.
    """
    for block in pattern:
        yield block


def run_simulation(sim_id: int) -> bool:
    """
    Run cache simulation per CSC512C spec.
    - Memory: fixed 1024 blocks
    - Three patterns: sequential, mid_repeat, random
    """
    sim = get_simulation(sim_id)
    if not sim:
        return False

    simulator = CacheSimulator(sim)

    # Generate access pattern based on test_pattern
    if sim.test_pattern == "sequential":
        accesses = generate_sequential_pattern(sim.cache_blocks)
    elif sim.test_pattern == "mid_repeat":
        accesses = generate_mid_repeat_pattern(sim.cache_blocks)
    elif sim.test_pattern == "random":
        accesses = generate_random_pattern(sim.random_length)
    elif sim.test_pattern == "custom":
        if not sim.custom_pattern:
            # Default to sequential if no custom pattern provided
            accesses = generate_sequential_pattern(sim.cache_blocks)
        else:
            accesses = generate_custom_pattern(sim.custom_pattern)
    else:
        accesses = generate_sequential_pattern(sim.cache_blocks)

    # Execute all accesses
    for block in accesses:
        simulator.access_block(block)

    # Calculate metrics
    total = simulator.hit_count + simulator.miss_count
    sim.total_accesses = total
    sim.cache_hits = simulator.hit_count
    sim.cache_misses = simulator.miss_count
    sim.hit_rate = simulator.hit_count / total if total > 0 else 0.0
    sim.miss_rate = simulator.miss_count / total if total > 0 else 0.0
    
    # Average memory access time (AMAT) = hit_time + miss_rate * miss_penalty
    # Miss penalty = miss_penalty - hit_time
    sim.avg_memory_access_time = simulator.hit_time + sim.miss_rate * (simulator.miss_penalty - simulator.hit_time)
    sim.total_memory_access_time = (simulator.hit_count * simulator.hit_time) + (simulator.miss_count * simulator.miss_penalty)
    
    sim.trace_log = simulator.access_trace
    # Copy cache array (shallow copy for 1D, deep copy for 2D)
    if simulator.is_direct_mapped:
        sim.final_cache_memory = simulator.cache_array.copy()
    else:
        sim.final_cache_memory = [set_array.copy() for set_array in simulator.cache_array]
    sim.cache_snapshots = simulator.cache_snapshots  # Cache state at each step for animation
    sim.status = "done"

    # Persist results - update the simulation in the store
    store = _load_store()
    for i, stored_sim in enumerate(store):
        if stored_sim.id == sim_id:
            store[i] = sim
            break
    _save_store(store)

    return True