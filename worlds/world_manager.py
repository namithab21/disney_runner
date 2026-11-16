"""
world_manager.py - Central Disney World Manager.
Tracks active world, manages 60-second countdown timers, triggers transitions,
and notifies all dependent game systems when the world changes.
"""

from typing import Callable, List, Optional
from worlds.world_config import WorldConfig, get_world, get_all_worlds
from config import settings


class WorldManager:
    """
    Manages the active Disney world, automatic transitions, and world-change callbacks.

    Responsibilities:
    - Track current world index (cycles through 8 worlds).
    - Countdown world timer (pauses on game-over, pauses on pause).
    - Trigger transition when timer expires.
    - Notify subscriber callbacks on world change.
    - Provide current world config to all dependent systems.
    """

    def __init__(self, world_duration: float = None):
        # Duration each world is active (seconds); configurable for testing
        self.world_duration: float = (
            world_duration
            if world_duration is not None
            else getattr(settings, "WORLD_DURATION", 60.0)
        )

        self._current_index: int = 0
        self._world_timer: float = 0.0          # Seconds elapsed in this world
        self._total_worlds: int = len(get_all_worlds())

        # Subscriber callbacks invoked when world changes: fn(new_config: WorldConfig)
        self._on_change_callbacks: List[Callable[[WorldConfig], None]] = []

        # Paused flag: timer does not advance when True
        self._paused: bool = False

        # Transition request flag: set True when timer expires
        self._transition_requested: bool = False

        # Statistics
        self.total_transitions: int = 0

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------

    @property
    def current_world(self) -> WorldConfig:
        """Returns the active WorldConfig."""
        return get_world(self._current_index)

    @property
    def current_index(self) -> int:
        return self._current_index

    @property
    def world_timer(self) -> float:
        """Seconds elapsed in the current world (0 → world_duration)."""
        return self._world_timer

    @property
    def world_progress(self) -> float:
        """Normalized progress through current world (0.0 = just started, 1.0 = ending)."""
        if self.world_duration <= 0.0:
            return 1.0
        return min(1.0, self._world_timer / self.world_duration)

    @property
    def world_time_remaining(self) -> float:
        """Seconds remaining in the current world."""
        return max(0.0, self.world_duration - self._world_timer)

    @property
    def transition_requested(self) -> bool:
        return self._transition_requested

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------

    def subscribe(self, callback: Callable[[WorldConfig], None]) -> None:
        """Register a callback that fires every time the world changes."""
        self._on_change_callbacks.append(callback)

    def pause(self) -> None:
        """Pause the world timer (e.g. game paused or game over)."""
        self._paused = True

    def resume(self) -> None:
        """Resume the world timer."""
        self._paused = False

    def update(self, delta_time: float) -> bool:
        """
        Advance the world timer.
        Returns True if a world transition was triggered this frame.
        Does not advance when paused or game-over.
        """
        if self._paused or delta_time <= 0.0:
            return False

        self._world_timer += delta_time

        if self._world_timer >= self.world_duration and not self._transition_requested:
            self._transition_requested = True
            return True

        return False

    def advance_world(self) -> WorldConfig:
        """
        Advances to the next world. Called by the transition system when the
        fade/blend transition is complete. Resets the timer and fires callbacks.
        Returns the new WorldConfig.
        """
        self._current_index = (self._current_index + 1) % self._total_worlds
        self._world_timer = 0.0
        self._transition_requested = False
        self.total_transitions += 1

        new_config = self.current_world
        print(f"[WORLD] Transitioning to World {self._current_index}: {new_config.name}")

        for cb in self._on_change_callbacks:
            try:
                cb(new_config)
            except Exception as e:
                print(f"[WORLD] Warning: callback error during world change: {e}")

        return new_config

    def reset(self) -> None:
        """Resets world manager to initial state (World 0, timer = 0)."""
        self._current_index = 0
        self._world_timer = 0.0
        self._transition_requested = False
        self.total_transitions = 0
        self._paused = False

        # Notify subscribers of reset-to-world-0
        for cb in self._on_change_callbacks:
            try:
                cb(self.current_world)
            except Exception as e:
                print(f"[WORLD] Warning: callback error on reset: {e}")

    def jump_to_world(self, index: int) -> WorldConfig:
        """
        Directly jump to a specific world (for testing).
        Resets timer and fires change callbacks.
        """
        self._current_index = index % self._total_worlds
        self._world_timer = 0.0
        self._transition_requested = False

        new_config = self.current_world
        for cb in self._on_change_callbacks:
            try:
                cb(new_config)
            except Exception as e:
                pass
        return new_config

    def get_debug_stats(self) -> dict:
        """Returns diagnostic info for the HUD debug overlay."""
        return {
            "world_index": self._current_index,
            "world_name": self.current_world.name,
            "world_timer": round(self._world_timer, 1),
            "world_duration": self.world_duration,
            "time_remaining": round(self.world_time_remaining, 1),
            "total_transitions": self.total_transitions,
            "paused": self._paused,
        }
