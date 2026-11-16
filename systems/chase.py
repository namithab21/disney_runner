"""
chase.py - Villain Chase System and Dynamic Proximity Manager.
Manages trailing chase distance, mistake penalties, clean running recovery,
collectible bonuses, proximity states (Safe, Warning, Critical), and capture game over.
"""

from typing import Tuple, Dict, Any
import numpy as np
from config import settings

STATE_SAFE = "safe"
STATE_WARNING = "warning"
STATE_CRITICAL = "critical"
STATE_CAUGHT = "caught"


class ChaseManager:
    """Tracks and calculates the dynamic pursuit distance between player and villain."""

    def __init__(
        self,
        start_distance: float = settings.VILLAIN_START_DISTANCE,
        max_distance: float = settings.VILLAIN_MAX_DISTANCE,
        min_distance: float = settings.VILLAIN_MIN_DISTANCE
    ):
        self.start_distance = start_distance
        self.max_distance = max_distance
        self.min_distance = min_distance

        self.warning_distance = settings.VILLAIN_WARNING_DISTANCE
        self.critical_distance = settings.VILLAIN_CRITICAL_DISTANCE

        self.recovery_rate = settings.VILLAIN_RECOVERY_RATE
        self.coin_bonus = settings.VILLAIN_COIN_BONUS
        self.mistake_penalty = settings.VILLAIN_MISTAKE_PENALTY

        self.current_distance = self.start_distance
        self.is_caught = False

        # Cooldown timer to prevent duplicate penalties from a single obstacle pass
        self.mistake_cooldown = 0.0

        # Statistics
        self.total_mistakes = 0
        self.total_recoveries = 0

    def update(self, delta_time: float) -> str:
        """
        Updates chase distance over time.
        When running cleanly, player gradually pulls away from the villain.
        Returns the current proximity state: SAFE, WARNING, CRITICAL, or CAUGHT.
        """
        if delta_time <= 0.0 or self.is_caught:
            return STATE_CAUGHT if self.is_caught else STATE_SAFE

        # Cooldown countdown
        if self.mistake_cooldown > 0.0:
            self.mistake_cooldown = max(0.0, self.mistake_cooldown - delta_time)

        # Successful clean running: villain gradually falls behind
        if self.mistake_cooldown <= 0.0 and self.current_distance < self.max_distance:
            self.current_distance = min(
                self.max_distance,
                self.current_distance + (self.recovery_rate * delta_time)
            )

        # Evaluate caught condition
        if self.current_distance <= self.min_distance:
            self.current_distance = self.min_distance
            self.is_caught = True
            return STATE_CAUGHT

        # Evaluate proximity tier
        if self.current_distance > self.warning_distance:
            return STATE_SAFE
        elif self.current_distance > self.critical_distance:
            return STATE_WARNING
        else:
            return STATE_CRITICAL

    def on_mistake(self, is_fatal: bool = False) -> bool:
        """
        Applies proximity penalty when player stumbles on an obstacle.
        If is_fatal (e.g. crashing directly into a full blocker), catches player immediately.
        Returns True if penalty was applied, False if currently in debounce cooldown.
        """
        if self.is_caught:
            return False

        if is_fatal:
            self.current_distance = self.min_distance
            self.is_caught = True
            self.total_mistakes += 1
            return True

        if self.mistake_cooldown > 0.0:
            return False

        # Apply hurdle stumble penalty
        self.mistake_cooldown = 0.75  # 750ms debounce
        self.total_mistakes += 1
        self.current_distance -= self.mistake_penalty

        if self.current_distance <= self.min_distance:
            self.current_distance = self.min_distance
            self.is_caught = True

        return True

    def push_back(self, meters: float) -> None:
        """Pushes the chasing villain farther behind (positive recovery)."""
        if not self.is_caught:
            self.current_distance = min(self.max_distance, self.current_distance + max(0.0, meters))

    def on_collectible(self) -> None:
        """Small recovery bonus when player collects a coin."""
        if not self.is_caught and self.current_distance < self.max_distance:
            self.current_distance = min(
                self.max_distance,
                self.current_distance + self.coin_bonus
            )
            self.total_recoveries += 1

    @property
    def proximity_ratio(self) -> float:
        """
        Returns normalized proximity ratio from 0.0 (Safe / furthest)
        to 1.0 (Critical / caught).
        """
        span = self.max_distance - self.min_distance
        if span <= 0.0:
            return 1.0
        ratio = (self.max_distance - self.current_distance) / span
        return float(np.clip(ratio, 0.0, 1.0))

    @property
    def state(self) -> str:
        """Returns the current proximity state string."""
        if self.is_caught:
            return STATE_CAUGHT
        elif self.current_distance > self.warning_distance:
            return STATE_SAFE
        elif self.current_distance > self.critical_distance:
            return STATE_WARNING
        else:
            return STATE_CRITICAL

    def reset(self) -> None:
        """Resets the chase state upon game restart."""
        self.current_distance = self.start_distance
        self.is_caught = False
        self.mistake_cooldown = 0.0
        self.total_mistakes = 0
        self.total_recoveries = 0

    def get_debug_stats(self) -> Dict[str, Any]:
        """Diagnostic state details for debug overlays."""
        return {
            "chase_distance": round(self.current_distance, 2),
            "state": self.state,
            "proximity_ratio": round(self.proximity_ratio, 2),
            "total_mistakes": self.total_mistakes,
            "total_recoveries": self.total_recoveries
        }
