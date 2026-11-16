"""
powerup.py - Power-Up Lifecycle Manager and State Coordinator.
Phase 8.1: Defines ActivePowerUp state tracking and the PowerUpManager lifecycle.
Provides hooks for activation, duration countdown, expiration, and collision
interception, ready for full gameplay integration in subsequent subphases.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from entities.powerup import PowerUpType, PowerUp


@dataclass
class ActivePowerUp:
    """Represents a currently active power-up effect."""
    powerup_type: PowerUpType
    name: str
    duration: float
    max_duration: float
    world_index: int = 0
    charges: int = 1
    icon_color: Tuple[int, int, int] = (255, 255, 255)

    @property
    def progress_ratio(self) -> float:
        """Remaining duration as a 0.0 to 1.0 fraction."""
        if self.max_duration <= 0.0:
            return 0.0
        return max(0.0, min(1.0, self.duration / self.max_duration))

    @property
    def is_critical(self) -> bool:
        """True when fewer than 3 seconds remain."""
        return self.duration <= 3.0


class PowerUpManager:
    """
    Manages active power-ups, remaining durations, activation, expiration,
    and queries for scoring, chase, and HUD systems.
    """

    # Baseline durations (in seconds)
    DURATION_SHIELD = 15.0
    DURATION_MAGNET = 12.0
    DURATION_DOUBLE_SCORE = 15.0

    def __init__(self):
        self.active_powerups: Dict[str, ActivePowerUp] = {}
        # Cooldown timer after a shield absorbs a hit to prevent multi-frame consumption
        self.shield_hit_debounce = 0.0

    def is_active(self, powerup_type: PowerUpType) -> bool:
        """Returns True if the specified power-up is currently active."""
        return powerup_type.value in self.active_powerups

    def get_active(self, powerup_type: PowerUpType) -> Optional[ActivePowerUp]:
        """Returns the ActivePowerUp instance if active, else None."""
        return self.active_powerups.get(powerup_type.value)

    def activate(
        self,
        powerup_type: PowerUpType,
        world_index: int = 0,
        world_config: Optional[Any] = None
    ) -> ActivePowerUp:
        """
        Activates a power-up. If already active, refreshes the duration
        to prevent invalid or compounded stacking.
        """
        key = powerup_type.value

        if powerup_type == PowerUpType.MAGIC_SHIELD:
            name = "Magic Shield"
            duration = self.DURATION_SHIELD
            icon_color = (65, 160, 255)
            charges = 1

        elif powerup_type == PowerUpType.TREASURE_MAGNET:
            name = "Treasure Magnet"
            duration = self.DURATION_MAGNET
            icon_color = (255, 205, 40)
            charges = 1

        elif powerup_type == PowerUpType.DOUBLE_SCORE:
            name = "Double Score (2X)"
            duration = self.DURATION_DOUBLE_SCORE
            icon_color = (255, 90, 90)
            charges = 1

        elif powerup_type == PowerUpType.WORLD_ABILITY:
            name = getattr(world_config, "ability_name", "World Ability") if world_config else "World Ability"
            duration = getattr(world_config, "ability_duration", 10.0) if world_config else 10.0
            icon_color = getattr(world_config, "ability_color", (200, 100, 255)) if world_config else (200, 100, 255)
            ab_type = getattr(world_config, "ability_type", "") if world_config else ""
            # Set charges based on ability archetype
            if ab_type in ("glass_slipper_grace", "frost_barrier"):
                charges = 2  # Absorbs up to 2 collisions
            else:
                charges = 1
        else:
            name = "Power-Up"
            duration = 10.0
            icon_color = (255, 255, 255)
            charges = 1

        active = ActivePowerUp(
            powerup_type=powerup_type,
            name=name,
            duration=duration,
            max_duration=duration,
            world_index=world_index,
            charges=charges,
            icon_color=icon_color
        )
        self.active_powerups[key] = active
        return active

    def update(self, delta_time: float) -> List[str]:
        """
        Ticks down all active durations.
        Returns a list of expired power-up keys for clean notification.
        """
        if delta_time <= 0.0:
            return []

        if self.shield_hit_debounce > 0.0:
            self.shield_hit_debounce = max(0.0, self.shield_hit_debounce - delta_time)

        expired_keys: List[str] = []

        for key, active in list(self.active_powerups.items()):
            active.duration -= delta_time
            if active.duration <= 0.0:
                expired_keys.append(key)
                del self.active_powerups[key]

        return expired_keys

    def consume_shield(self) -> bool:
        """
        Consumes one charge of an active shield or protective world ability (Glass Slipper Grace / Frost Barrier).
        Returns True if a shield charge was consumed, False if none active or in debounce.
        """
        if self.shield_hit_debounce > 0.0:
            return False

        # First check Magic Shield
        key = PowerUpType.MAGIC_SHIELD.value
        if key in self.active_powerups:
            active = self.active_powerups[key]
            active.charges -= 1
            self.shield_hit_debounce = 0.85  # 850ms collision forgiveness debounce
            if active.charges <= 0:
                del self.active_powerups[key]
            return True

        # Next check World Ability protective barriers (Cinderella or Frozen)
        w_key = PowerUpType.WORLD_ABILITY.value
        if w_key in self.active_powerups:
            active = self.active_powerups[w_key]
            # Cinderella or Frozen barrier
            if active.charges > 0:
                active.charges -= 1
                self.shield_hit_debounce = 0.85
                if active.charges <= 0:
                    del self.active_powerups[w_key]
                return True

        return False

    def get_active_display_list(self) -> List[Dict[str, Any]]:
        """Supplies structured data for HUD power-up status cluster."""
        items = []
        for active in self.active_powerups.values():
            items.append({
                "type": active.powerup_type.value,
                "name": active.name,
                "time_left": max(0.0, active.duration),
                "ratio": active.progress_ratio,
                "is_critical": active.is_critical,
                "color": active.icon_color
            })
        return items

    def reset(self) -> None:
        """Clears all active power-ups and resets debounce."""
        self.active_powerups.clear()
        self.shield_hit_debounce = 0.0
