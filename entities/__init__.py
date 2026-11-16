"""
entities package - Game entities, 3D primitives, obstacles, collectibles, and villains.
"""

from entities.cube import CubeEntity, create_cube_mesh
from entities.scenery import add_quad, add_box, add_tree, add_guardrail
from entities.obstacle import Obstacle, ObstacleType, ObstacleMeshCache
from entities.collectible import Collectible, CollectibleMeshCache
from entities.powerup import PowerUp, PowerUpType, PowerUpMeshCache
from entities.villain import Villain, VillainAnimation

__all__ = [
    "CubeEntity",
    "create_cube_mesh",
    "add_quad",
    "add_box",
    "add_tree",
    "add_guardrail",
    "Obstacle",
    "ObstacleType",
    "ObstacleMeshCache",
    "Collectible",
    "CollectibleMeshCache",
    "PowerUp",
    "PowerUpType",
    "PowerUpMeshCache",
    "Villain",
    "VillainAnimation"
]
