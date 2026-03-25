"""
backend/simulation.py
---------------------
Cache simulation engine implementing CSC512C spec:
- Fixed 1024 memory blocks
- Three test patterns: sequential, mid_repeat, random
- Non load-through read policy
- Computes: hit rate, miss rate, avg/total access time

Authors:
    - Kimberly Klaire H. Gamboa
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
        self.replacement_order: dict[int, list[int]] = {}  # Track block order per set for replacement policy
        self.access_trace: list[str] = []
        self.cache_snapshots: list[dict] = []
        self.hit_count = 0
        self.miss_count = 0
        self.access_count = 0

        # Calculate timing: hit_time and miss_penalty
        self.hit_time = sim.cache_access_time
        self.miss_penalty = sim.cache_access_time + (sim.block_size * sim.memory_access_time) + sim.cache_access_time
        sim.miss_penalty = self.miss_penalty
        
        # Initialize cache structure
        num_sets = self.get_num_sets()
        self.blocks_per_set = min(sim.associativity, sim.cache_blocks) if sim.associativity > 1 else sim.associativity
        self.is_direct_mapped = (sim.associativity == 1)
        
        if self.is_direct_mapped:
            self.cache_array: list[int | None] | list[list[int | None]] = [None] * sim.cache_blocks
        else:
            self.cache_array = [[None] * self.blocks_per_set for _ in range(num_sets)]
        
        # Capture initial empty state as step 0
        self._capture_snapshot()
        
        # Initialize replacement policy tracking
        for set_id in range(num_sets):
            self.replacement_order[set_id] = []

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
        """Get cache array positions for a given set."""
        if self.is_direct_mapped:
            positions = []
            for block_idx in range(self.sim.associativity):
                pos = set_id * self.sim.associativity + block_idx
                if pos < self.sim.cache_blocks:
                    positions.append(pos)
            return positions
        else:
            return [(set_id, block_idx) for block_idx in range(self.blocks_per_set)]
    
    def find_block_position(self, block: int) -> int | tuple[int, int] | None:
        """Find the cache position of a block, or None if not in cache."""
        if self.is_direct_mapped:
            for pos, cached_block in enumerate(self.cache_array):
                if cached_block == block:
                    return pos
            return None
        else:
            set_id = self.get_set_id(block)
            for block_idx, cached_block in enumerate(self.cache_array[set_id]):
                if cached_block == block:
                    return (set_id, block_idx)
            return None
    
    def find_empty_position_in_set(self, set_id: int) -> int | tuple[int, int] | None:
        """Find an empty position in the set, or None if full."""
        if self.is_direct_mapped:
            positions = self.get_set_positions(set_id)
            for pos in positions:
                if self.cache_array[pos] is None:
                    return pos
            return None
        else:
            for block_idx in range(self.blocks_per_set):
                if self.cache_array[set_id][block_idx] is None:
                    return (set_id, block_idx)
            return None
    
    def get_blocks_in_set(self, set_id: int) -> list[int]:
        """Get all blocks currently in a set."""
        if self.is_direct_mapped:
            positions = self.get_set_positions(set_id)
            return [self.cache_array[pos] for pos in positions if self.cache_array[pos] is not None]
        else:
            return [block for block in self.cache_array[set_id] if block is not None]

    def evict_from_set(self, set_id: int) -> tuple[int, int | tuple[int, int]] | None:
        """Evict a block from the set based on replacement policy. Returns (block, position) or None."""
        order_list = self.replacement_order.get(set_id, [])
        if order_list:
            # First block in list is the victim (least recently used)
            victim_block = order_list[0]
            pos = self.find_block_position(victim_block)
            if pos is not None:
                return victim_block, pos
        
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
        """Access a memory block. Returns True if hit, False if miss."""
        self.access_count += 1
        set_id = self.get_set_id(block)
        
        # Increment age of all blocks on every access
        for existing_block in list(self.block_ages.keys()):
            self.block_ages[existing_block] += 1
        
        # Check if block is in cache
        pos = self.find_block_position(block)
        if pos is not None:
            # Cache hit - update LRU order and reset age
            order_list = self.replacement_order[set_id]
            if block in order_list:
                order_list.remove(block)
            order_list.append(block)
            
            self.block_ages[block] = 0
            
            self.hit_count += 1
            pos_str = str(pos) if self.is_direct_mapped else f"set {pos[0]}, block {pos[1]}"
            self.access_trace.append(f"Block {block}: HIT (in cache {pos_str})")
            self._capture_snapshot(block, True, None)
            return True

        # Cache miss - load block
        evicted_block = None
        empty_pos = self.find_empty_position_in_set(set_id)
        
        if empty_pos is not None:
            # Load into empty position
            if self.is_direct_mapped:
                self.cache_array[empty_pos] = block
                pos_str = str(empty_pos)
            else:
                self.cache_array[empty_pos[0]][empty_pos[1]] = block
                pos_str = f"set {empty_pos[0]}, block {empty_pos[1]}"
            
            self.block_ages[block] = 0
            self.access_trace.append(f"Block {block}: MISS - loaded into {pos_str}")
        else:
            # Evict and replace
            eviction_result = self.evict_from_set(set_id)
            if eviction_result:
                evicted_block, evict_pos = eviction_result
                
                # Remove evicted block from tracking
                if evicted_block in self.block_ages:
                    del self.block_ages[evicted_block]
                if evicted_block in self.replacement_order[set_id]:
                    self.replacement_order[set_id].remove(evicted_block)
                
                # Load new block
                if self.is_direct_mapped:
                    self.cache_array[evict_pos] = block
                    pos_str = str(evict_pos)
                else:
                    self.cache_array[evict_pos[0]][evict_pos[1]] = block
                    pos_str = f"set {evict_pos[0]}, block {evict_pos[1]}"
                
                self.block_ages[block] = 0
                self.access_trace.append(f"Block {block}: MISS - evicted block {evicted_block} from {pos_str}")
        
        # Update tracking for new block
        self.replacement_order[set_id].append(block)

        self.miss_count += 1
        self._capture_snapshot(block, False, evicted_block)
        return False
    
    def _capture_snapshot(self, accessed_block: int | None = None, is_hit: bool | None = None, evicted_block: int | None = None):
        """Capture the current cache state for animation.
        
        If called without arguments, captures the initial empty state (step 0).
        Otherwise, captures the state after a memory access.
        """
        block_age_info = []
        
        if self.is_direct_mapped:
            for pos, block in enumerate(self.cache_array):
                if block is not None:
                    age = self.block_ages.get(block, 0)
                    block_age_info.append({"position": pos, "block": block, "age": age})
            
            cache_state = self.cache_array.copy()
        else:
            for set_id, set_array in enumerate(self.cache_array):
                for block_idx, block in enumerate(set_array):
                    if block is not None:
                        age = self.block_ages.get(block, 0)
                        block_age_info.append({"set": set_id, "block_index": block_idx, "block": block, "age": age})
            
            cache_state = [set_array.copy() for set_array in self.cache_array]
        
        snapshot = {
            "step": len(self.cache_snapshots),
            "accessed_block": accessed_block,
            "is_hit": is_hit,
            "evicted_block": evicted_block,
            "cache_state": cache_state,
            "block_ages": block_age_info,
            "is_direct_mapped": self.is_direct_mapped,
            "hits": self.hit_count,
            "misses": self.miss_count
        }
        self.cache_snapshots.append(snapshot)


def generate_sequential_pattern(cache_blocks: int) -> Generator[int, None, None]:
    """Sequential pattern: 0 to 2n-1, repeated twice."""
    pattern = list(range(2 * cache_blocks))
    for _ in range(2):
        yield from pattern


def generate_mid_repeat_pattern(cache_blocks: int) -> Generator[int, None, None]:
    """Mid-repeat pattern: 0, [1 to n-1] twice, [n to 2n-1], repeated twice."""
    n = cache_blocks
    base_sequence = [0] + list(range(1, n)) * 2 + list(range(n, 2 * n))
    for _ in range(2):
        yield from base_sequence


def generate_random_pattern(length: int = 64) -> Generator[int, None, None]:
    """Random pattern: generates memory blocks from range 0-1023."""
    for _ in range(length):
        yield random.randint(0, 1023)


def generate_custom_pattern(pattern: list[int]) -> Generator[int, None, None]:
    """
    Custom pattern: user-defined sequence of memory blocks.
    """
    for block in pattern:
        yield block


def run_simulation(sim_id: int) -> bool:
    """Run cache simulation per CSC512C spec."""
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
        accesses = generate_custom_pattern(sim.custom_pattern) if sim.custom_pattern else generate_sequential_pattern(sim.cache_blocks)
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
    
    # AMAT = hit_time + miss_rate * miss_penalty
    sim.avg_memory_access_time = (sim.hit_rate * simulator.hit_time) + (sim.miss_rate * simulator.miss_penalty)
    
    # Total access time
    hit_time_total = sim.cache_hits * sim.block_size * sim.cache_access_time
    miss_time_total = (sim.cache_access_time + sim.memory_access_time * sim.block_size + sim.cache_access_time * sim.block_size) * sim.cache_misses
    sim.total_memory_access_time = hit_time_total + miss_time_total
    
    sim.trace_log = simulator.access_trace
    sim.final_cache_memory = simulator.cache_array.copy() if simulator.is_direct_mapped else [s.copy() for s in simulator.cache_array]
    sim.cache_snapshots = simulator.cache_snapshots

    # Persist results
    store = _load_store()
    for i, stored_sim in enumerate(store):
        if stored_sim.id == sim_id:
            store[i] = sim
            break
    _save_store(store)

    return True