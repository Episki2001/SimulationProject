"""
backend/data.py
---------------
Cache simulation backend for the CSC512C Cache Simulation Project.
Stores cache simulations with parameters like size, block size, and replacement policy.
Persists to browser localStorage via NiceGUI. Each user has their own storage.

Authors:
    - Kimberly Klaire H. Gamboa
    - Andre Emmanuel S. Garcia
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class CacheSimulation:
    """Represents a single cache simulation run."""
    id: int
    name: str
    
    # Cache configuration 
    cache_blocks: int    # number of cache blocks (min 4, power-of-2)
    block_size: int      # cache line size in words (min 2, power-of-2)
    associativity: int   # 1=direct-mapped, N=N-way set-associative
    replacement_policy: str 
    test_pattern: str    # "sequential", "mid_repeat", "random", or "custom"
    custom_pattern: list[int] = field(default_factory=list)  # user-defined access pattern
    random_length: int = 64  # number of accesses for random pattern
    
    # Timing configuration
    cache_access_time: int = 1  # ns per block (cache hit time)
    memory_access_time: int = 10  # ns per word (memory fetch time)
    miss_penalty: int = 0  # ns (total time for cache miss: cache_access + block_size*memory_access + cache_access)
    
    # Fixed per spec
    # Memory blocks: 1024 (fixed)
    # Read policy: non load-through (fixed)
    
    # Results
    total_accesses: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    hit_rate: float = 0.0
    miss_rate: float = 0.0
    avg_memory_access_time: float = 0.0
    total_memory_access_time: float = 0.0
    trace_log: list[str] = field(default_factory=list)  # step-by-step trace
    final_cache_memory: list[int] = field(default_factory=list)  # blocks in cache at end
    cache_snapshots: list[dict] = field(default_factory=list)  # cache state at each step for animation
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @classmethod
    def from_dict(cls, data: dict) -> CacheSimulation:
        """Create a CacheSimulation from a dict (loaded from JSON)."""
        return cls(**data)


# Storage using browser localStorage via NiceGUI
from nicegui import app

STORAGE_KEY = "cache_simulations"


def _load_store() -> list[CacheSimulation]:
    """Load cache simulations from browser storage."""
    try:
        data = app.storage.user.get(STORAGE_KEY, [])
        if data:
            return [CacheSimulation.from_dict(item) for item in data]
    except (KeyError, TypeError, AttributeError):
        pass
    return []


def _save_store(store: list[CacheSimulation]) -> None:
    """Persist cache simulations to browser localStorage."""
    app.storage.user[STORAGE_KEY] = [asdict(item) for item in store]


def get_all_simulations() -> list[CacheSimulation]:
    """Return all cache simulations."""
    return _load_store()


def get_simulation(sim_id: int) -> CacheSimulation | None:
    """Return a cache simulation by ID, or None if not found."""
    store = _load_store()
    return next((s for s in store if s.id == sim_id), None)


def add_simulation(
    name: str,
    cache_blocks: int = 4,
    block_size: int = 2,
    associativity: int = 1,
    replacement_policy: str = "LRU",
    test_pattern: str = "sequential",
    custom_pattern: list[int] = None,
    random_length: int = 64,
    cache_access_time: int = 1,
    memory_access_time: int = 10
) -> CacheSimulation:
    """Create and run a cache simulation."""
    store = _load_store()
    new_id = max((s.id for s in store), default=0) + 1
    sim = CacheSimulation(
        id=new_id,
        name=name,
        cache_blocks=cache_blocks,
        block_size=block_size,
        associativity=associativity,
        replacement_policy=replacement_policy,
        test_pattern=test_pattern,
        custom_pattern=custom_pattern or [],
        random_length=random_length,
        cache_access_time=cache_access_time,
        memory_access_time=memory_access_time
    )
    store.append(sim)
    _save_store(store)
    
    from backend.simulation import run_simulation
    run_simulation(new_id)
    
    return get_simulation(new_id)


def delete_simulation(sim_id: int) -> bool:
    """Delete a cache simulation by ID. Returns True if deleted."""
    store = _load_store()
    before = len(store)
    store = [s for s in store if s.id != sim_id]
    if len(store) < before:
        _save_store(store)
        return True
    return False


def delete_all_simulations() -> int:
    """Delete all cache simulations. Returns number of simulations deleted."""
    store = _load_store()
    count = len(store)
    _save_store([])
    return count


def get_stats() -> dict:
    """Get simulation statistics."""
    store = _load_store()
    return {"total": len(store)}
