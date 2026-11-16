"""
collision.py - 3D AABB Collision Detection System.
Evaluates spatial overlaps between the animated player bounding volume,
road obstacles, and magical collectibles.
"""

from typing import Tuple, List, Optional
import numpy as np
from player.player import Player
from entities.obstacle import Obstacle
from entities.collectible import Collectible
from entities.powerup import PowerUp


def check_aabb_overlap(
    box_a: Tuple[np.ndarray, np.ndarray],
    box_b: Tuple[np.ndarray, np.ndarray]
) -> bool:
    """
    Evaluates whether two 3D Axis-Aligned Bounding Boxes intersect.
    Returns True if overlapping on all 3 Cartesian axes.
    """
    min_a, max_a = box_a
    min_b, max_b = box_b

    overlap_x = (min_a[0] <= max_b[0]) and (max_a[0] >= min_b[0])
    overlap_y = (min_a[1] <= max_b[1]) and (max_a[1] >= min_b[1])
    overlap_z = (min_a[2] <= max_b[2]) and (max_a[2] >= min_b[2])

    return bool(overlap_x and overlap_y and overlap_z)


class CollisionSystem:
    """Orchestrates collision checks between the player and scene objects."""

    def __init__(self):
        pass

    def check_player_obstacles(self, player: Player, obstacles: List[Obstacle]) -> Optional[Obstacle]:
        """
        Tests player against all active obstacles.
        Returns the first obstacle collided with, or None if safe.
        """
        player_box = player.movement.get_bounding_box()
        player_z = player.movement.z

        for obs in obstacles:
            # Broad-phase spatial pruning along Z
            if abs(player_z - obs.z) > 2.0:
                continue

            obs_box = obs.get_bounding_box()
            if check_aabb_overlap(player_box, obs_box):
                return obs

        return None

    def check_player_collectibles(self, player: Player, collectibles: List[Collectible]) -> List[Collectible]:
        """
        Tests player against all active collectibles.
        Marks collected items and returns list of newly collected collectibles.
        """
        player_box = player.movement.get_bounding_box()
        player_z = player.movement.z
        collected: List[Collectible] = []

        for item in collectibles:
            if item.collected:
                continue

            # Broad-phase spatial pruning along Z
            if abs(player_z - item.z) > 2.0:
                continue

            item_box = item.get_bounding_box()
            if check_aabb_overlap(player_box, item_box):
                item.collected = True
                collected.append(item)

        return collected

    def check_player_powerups(self, player: Player, powerups: List[PowerUp]) -> List[PowerUp]:
        """
        Tests player against all active power-up items.
        Marks collected items and returns list of newly collected power-ups.
        """
        player_box = player.movement.get_bounding_box()
        player_z = player.movement.z
        collected: List[PowerUp] = []

        for p in powerups:
            if p.collected:
                continue

            # Broad-phase spatial pruning along Z
            if abs(player_z - p.z) > 2.0:
                continue

            p_box = p.get_bounding_box()
            if check_aabb_overlap(player_box, p_box):
                p.collected = True
                collected.append(p)

        return collected

    def apply_magnet_attraction(
        self,
        player_x: float,
        player_y: float,
        player_z: float,
        collectibles: List[Collectible],
        delta_time: float,
        radius: float = 14.0,
        speed: float = 25.0
    ) -> None:
        """
        Smoothly pulls nearby uncollected items across all 3 lanes toward the player.
        Uses smooth delta-time vector progression with zero teleportation.
        """
        if delta_time <= 0.0:
            return

        step = speed * delta_time
        for item in collectibles:
            if item.collected:
                continue

            dx = player_x - item.x
            dy = (player_y + 0.8) - item.y
            dz = player_z - item.z
            dist_sq = dx * dx + dy * dy + dz * dz

            if dist_sq <= radius * radius and dist_sq > 1e-4:
                dist = np.sqrt(dist_sq)
                # Normalize and move towards player smoothly
                ux = dx / dist
                uy = dy / dist
                uz = dz / dist
                move_dist = min(dist, step)
                item.x += ux * move_dist
                item.y += uy * move_dist
                item.z += uz * move_dist
