"""
systems package - Collision, spawning, scoring, and chase systems.
"""

from systems.collision import CollisionSystem, check_aabb_overlap
from systems.scoring import ScoreManager
from systems.spawning import SpawningManager
from systems.chase import ChaseManager, STATE_SAFE, STATE_WARNING, STATE_CRITICAL, STATE_CAUGHT
from systems.powerup import PowerUpManager, ActivePowerUp

__all__ = [
    "CollisionSystem",
    "check_aabb_overlap",
    "ScoreManager",
    "SpawningManager",
    "ChaseManager",
    "PowerUpManager",
    "ActivePowerUp",
    "STATE_SAFE",
    "STATE_WARNING",
    "STATE_CRITICAL",
    "STATE_CAUGHT"
]
