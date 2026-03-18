"""
backend/data.py
---------------
Cache simulation backend for the CSC512C Cache Simulation Project.
Stores cache simulations with parameters like size, block size, and replacement policy.
Persists to browser localStorage via NiceGUI. Each user has their own storage.

Authors:
    - Kimberly Claire H. Gamboa
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
    status: str          # "pending" | "running" | "done" | "error"
    
    # Cache configuration (per spec)
    cache_blocks: int    # number of cache blocks (min 4, power-of-2)
    block_size: int      # cache line size in words (min 2, power-of-2)
    associativity: int   # 1=direct-mapped, N=N-way set-associative
    replacement_policy: str  # "LRU" or "FIFO"
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
    result_value: float | None = None

    @classmethod
    def from_dict(cls, data: dict) -> CacheSimulation:
        """Create a CacheSimulation from a dict (loaded from JSON)."""
        return cls(**data)


# Storage setup - now using browser localStorage via NiceGUI
from nicegui import app

STORAGE_KEY = "cache_simulations"


def _load_store() -> list[CacheSimulation]:
    """Load cache simulations from browser storage, or return empty list if none exist."""
    try:
        data = app.storage.user.get(STORAGE_KEY, [])
        if data:
            return [CacheSimulation.from_dict(item) for item in data]
    except (KeyError, TypeError, AttributeError):
        pass
    # Default: empty store (no seed data)
    return []


def _save_store(store: list[CacheSimulation]) -> None:
    """Persist cache simulations to browser localStorage."""
    app.storage.user[STORAGE_KEY] = [asdict(item) for item in store]


# In-memory store (persisted to browser localStorage)
_store: list[CacheSimulation] = []


# ---------------------------------------------------------------------------
# CRUD helpers
# ---------------------------------------------------------------------------

def get_all_simulations() -> list[CacheSimulation]:
    """Return every cache simulation in the store."""
    global _store
    _store = _load_store()  # Load from browser storage
    return list(_store)


def get_simulation(sim_id: int) -> CacheSimulation | None:
    """Return a single cache simulation by id, or None."""
    global _store
    _store = _load_store()  # Load from browser storage
    return next((s for s in _store if s.id == sim_id), None)


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
    """Create and automatically run a cache simulation per spec."""
    global _store
    _store = _load_store()  # Load from browser storage
    new_id = max((s.id for s in _store), default=0) + 1
    sim = CacheSimulation(
        new_id, name, "running",
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
    _store.append(sim)
    _save_store(_store)
    
    # Import here to avoid circular dependency
    from backend.simulation import run_simulation
    run_simulation(new_id)
    
    # Return the updated simulation from the store (not the local copy)
    return get_simulation(new_id)


def delete_simulation(sim_id: int) -> bool:
    """Remove a cache simulation; returns True if it existed."""
    global _store
    _store = _load_store()  # Load from browser storage
    before = len(_store)
    _store = [s for s in _store if s.id != sim_id]
    if len(_store) < before:
        _save_store(_store)
        return True
    return False


def get_stats() -> dict:
    """Aggregate counts by status."""
    global _store
    _store = _load_store()  # Load from browser storage
    counts: dict[str, int] = {}
    for sim in _store:
        counts[sim.status] = counts.get(sim.status, 0) + 1
    return counts
