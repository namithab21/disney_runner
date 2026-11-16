"""
spawning.py - Continuous Obstacle and Collectible Procedural Spawning Manager.
Generates fair, playable hazard patterns and coin trails ahead of the player,
guaranteeing continuous distance-based wave progression throughout gameplay.
"""

from typing import List, Optional, Dict, Any
import random
import numpy as np
from config import settings
from engine.shader import ShaderProgram
from engine.camera import Camera
from engine.renderer import Renderer
from entities.obstacle import Obstacle, ObstacleType
from entities.collectible import Collectible
from entities.powerup import PowerUp, PowerUpType


class SpawningManager:
    """
    Orchestrates continuous, distance-synchronized procedural generation of
    obstacles and collectibles with guaranteed fair-play routes and zero stalling.
    """

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.np_rng = np.random.default_rng(seed)

        self.obstacles: List[Obstacle] = []
        self.collectibles: List[Collectible] = []
        self.powerups: List[PowerUp] = []

        # Distance-based spawning state
        self.distance_traveled = 0.0
        self.next_spawn_distance = 0.0
        # Power-up distance scheduling (every 60 to 90 meters)
        self.next_powerup_distance = 65.0
        self.current_world_index = 0

        # Spawning horizon in -Z (where new objects are placed)
        self.spawn_horizon_z = -180.0

        # Inter-row spacing parameters (units between consecutive waves)
        self.min_row_spacing = 28.0
        self.max_row_spacing = 38.0

        # Debug statistics counters
        self.total_waves_spawned = 0
        self.total_obstacles_spawned = 0
        self.total_obstacles_removed = 0
        self.total_collectibles_spawned = 0
        self.total_collectibles_removed = 0
        self.total_powerups_spawned = 0
        self.total_powerups_removed = 0

        # Track obstacle type distribution for diagnostics
        self.obstacle_type_counts = {
            ObstacleType.GROUND_BARRIER: 0,
            ObstacleType.OVERHEAD_BARRIER: 0,
            ObstacleType.FULL_BLOCKER: 0
        }

        # Seed initial waves across the track ahead of player
        self._seed_initial_waves()

    def _seed_initial_waves(self) -> None:
        """
        Pre-populates obstacles and collectibles from near distance (Z = -45.0)
        out to the spawn horizon (Z = -180.0) at the start of the game.
        """
        current_z = -45.0
        while current_z >= self.spawn_horizon_z:
            self._spawn_wave(current_z)
            spacing = self.rng.uniform(self.min_row_spacing, self.max_row_spacing)
            current_z -= spacing

        # Set the next distance trigger to maintain continuous flow from the horizon
        self.next_spawn_distance = abs(current_z - self.spawn_horizon_z)

    def _spawn_wave(self, z_pos: float) -> None:
        """
        Generates a fair, playable row of hazards and/or collectibles at z_pos.
        Guarantees that at least one clear, passable route always exists.
        """
        self.total_waves_spawned += 1
        lanes = [-1, 0, 1]
        pattern_roll = self.rng.random()

        if pattern_roll < 0.35:
            # -------------------------------------------------------------
            # Pattern A: Single Obstacle (2 completely open lanes)
            # -------------------------------------------------------------
            chosen_lane = self.rng.choice(lanes)
            obs_type = self.rng.choice([
                ObstacleType.GROUND_BARRIER,
                ObstacleType.OVERHEAD_BARRIER,
                ObstacleType.FULL_BLOCKER
            ])
            self._add_obstacle(obs_type, chosen_lane, z_pos)

            # Spawn a coin trail down one of the open lanes
            open_lanes = [l for l in lanes if l != chosen_lane]
            coin_lane = self.rng.choice(open_lanes)
            self._spawn_coin_trail(coin_lane, z_pos, count=3)

            # If ground barrier, also add an arc of bonus coins leaping over it
            if obs_type == ObstacleType.GROUND_BARRIER:
                self._spawn_coin_arc(chosen_lane, z_pos)

        elif pattern_roll < 0.70:
            # -------------------------------------------------------------
            # Pattern B: Double Obstacle (1 open lane + 1 jump/slide lane)
            # -------------------------------------------------------------
            chosen_lanes = self.rng.sample(lanes, 2)
            lane_a, lane_b = chosen_lanes[0], chosen_lanes[1]

            # At most ONE full blocker in any wave to ensure fair escape routes
            obs_a = self.rng.choice([
                ObstacleType.FULL_BLOCKER,
                ObstacleType.GROUND_BARRIER,
                ObstacleType.OVERHEAD_BARRIER
            ])
            if obs_a == ObstacleType.FULL_BLOCKER:
                obs_b = self.rng.choice([ObstacleType.GROUND_BARRIER, ObstacleType.OVERHEAD_BARRIER])
            else:
                obs_b = self.rng.choice([ObstacleType.GROUND_BARRIER, ObstacleType.OVERHEAD_BARRIER])

            self._add_obstacle(obs_a, lane_a, z_pos)
            self._add_obstacle(obs_b, lane_b, z_pos)

            # Coin trail down the 1 remaining guaranteed open lane
            free_lane = [l for l in lanes if l not in chosen_lanes][0]
            self._spawn_coin_trail(free_lane, z_pos, count=4)

        elif pattern_roll < 0.85:
            # -------------------------------------------------------------
            # Pattern C: Triple Skill Challenge (All 3 lanes have hazards, ALL PASSABLE)
            # -------------------------------------------------------------
            # ZERO full blockers! All lanes require jumping or sliding.
            for lane in lanes:
                obs_type = self.rng.choice([ObstacleType.GROUND_BARRIER, ObstacleType.OVERHEAD_BARRIER])
                self._add_obstacle(obs_type, lane, z_pos)
                if obs_type == ObstacleType.GROUND_BARRIER and self.rng.random() < 0.5:
                    self._spawn_coin_arc(lane, z_pos)

        else:
            # -------------------------------------------------------------
            # Pattern D: Peaceful Coin Runway (Pure collectibles across lanes)
            # -------------------------------------------------------------
            coin_lane = self.rng.choice(lanes)
            self._spawn_coin_trail(coin_lane, z_pos, count=5)

    def _add_obstacle(self, obs_type: ObstacleType, lane: int, z: float) -> None:
        """Helper to instantiate and track a new obstacle."""
        obs = Obstacle(obs_type, lane, z)
        self.obstacles.append(obs)
        self.total_obstacles_spawned += 1
        self.obstacle_type_counts[obs_type] += 1

    def _spawn_coin_trail(self, lane: int, center_z: float, count: int = 3) -> None:
        """Spawns a straight line of coins in a designated lane."""
        spacing = 3.2
        start_z = center_z - ((count - 1) * spacing / 2.0)
        for i in range(count):
            coin_z = start_z + i * spacing
            coin = Collectible(lane=lane, z=coin_z, base_y=0.90)
            self.collectibles.append(coin)
            self.total_collectibles_spawned += 1

    def _spawn_coin_arc(self, lane: int, barrier_z: float) -> None:
        """Spawns an arching trail of coins jumping over a ground barrier."""
        for offset_z, y_val in [(-2.8, 1.10), (0.0, 1.75), (2.8, 1.10)]:
            coin = Collectible(lane=lane, z=barrier_z + offset_z, base_y=y_val)
            self.collectibles.append(coin)
            self.total_collectibles_spawned += 1

    def update(self, speed: float, delta_time: float) -> None:
        """
        Updates positions of all active objects, prunes off-screen objects,
        and generates new waves based on continuous distance progression.
        """
        if delta_time <= 0.0:
            return

        # -------------------------------------------------------------
        # 1. Update Existing Obstacles & Collectibles
        # -------------------------------------------------------------
        for obs in self.obstacles:
            obs.update(speed, delta_time)

        for item in self.collectibles:
            item.update(speed, delta_time)

        for p in self.powerups:
            p.update(speed, delta_time)

        # -------------------------------------------------------------
        # 2. Recycle / Prune Off-Screen Objects
        # -------------------------------------------------------------
        surviving_obstacles = []
        for obs in self.obstacles:
            if obs.is_past_player():
                self.total_obstacles_removed += 1
            else:
                surviving_obstacles.append(obs)
        self.obstacles = surviving_obstacles

        surviving_collectibles = []
        for item in self.collectibles:
            if item.is_past_player() or item.collected:
                self.total_collectibles_removed += 1
            else:
                surviving_collectibles.append(item)
        self.collectibles = surviving_collectibles

        surviving_powerups = []
        for p in self.powerups:
            if p.is_past_player() or p.collected:
                self.total_powerups_removed += 1
            else:
                surviving_powerups.append(p)
        self.powerups = surviving_powerups

        # -------------------------------------------------------------
        # 3. Continuous Distance-Based Spawning Ahead of Player
        # -------------------------------------------------------------
        self.distance_traveled += speed * delta_time

        # Trigger new waves whenever the distance traveled crosses the next spawn threshold
        while self.distance_traveled >= self.next_spawn_distance:
            # Calculate spawn offset for micro-step precision
            overshoot = self.distance_traveled - self.next_spawn_distance
            spawn_z = self.spawn_horizon_z - overshoot

            self._spawn_wave(spawn_z)

            # Schedule the next wave distance
            spacing = self.rng.uniform(self.min_row_spacing, self.max_row_spacing)
            self.next_spawn_distance += spacing

        # Trigger power-up spawning (every 60 to 90 meters)
        while self.distance_traveled >= self.next_powerup_distance:
            overshoot_p = self.distance_traveled - self.next_powerup_distance
            # Offset from spawn horizon between obstacle rows
            spawn_pz = self.spawn_horizon_z - overshoot_p - 14.0
            self._spawn_powerup(spawn_pz)
            p_interval = self.rng.uniform(60.0, 90.0)
            self.next_powerup_distance += p_interval

    def _spawn_powerup(self, z_pos: float) -> None:
        """
        Spawns a power-up on a safe, reachable lane that does not overlap obstacles.
        Distribution: Shield 30%, Magnet 30%, Double Score 25%, World Ability Orb 15%.
        """
        # Find obstacle lanes at this Z position (+/- 4.0m)
        occupied_lanes = set()
        for obs in self.obstacles:
            if abs(obs.z - z_pos) < 5.0:
                occupied_lanes.add(obs.lane)

        available_lanes = [l for l in [-1, 0, 1] if l not in occupied_lanes]
        if not available_lanes:
            available_lanes = [-1, 0, 1]  # Fallback

        chosen_lane = self.rng.choice(available_lanes)

        # Roll calibrated distribution: 30%, 30%, 25%, 15%
        roll = self.rng.random()
        if roll < 0.30:
            p_type = PowerUpType.MAGIC_SHIELD
        elif roll < 0.60:
            p_type = PowerUpType.TREASURE_MAGNET
        elif roll < 0.85:
            p_type = PowerUpType.DOUBLE_SCORE
        else:
            p_type = PowerUpType.WORLD_ABILITY

        powerup = PowerUp(
            powerup_type=p_type,
            lane=chosen_lane,
            z=z_pos,
            world_index=self.current_world_index,
            base_y=0.95
        )
        self.powerups.append(powerup)
        self.total_powerups_spawned += 1

    @property
    def distance_until_next_spawn(self) -> float:
        """Returns distance in meters until the next obstacle wave is spawned."""
        return max(0.0, self.next_spawn_distance - self.distance_traveled)

    def get_debug_stats(self) -> Dict[str, Any]:
        """Returns diagnostic statistics for monitoring spawning health."""
        return {
            "distance_traveled": round(self.distance_traveled, 1),
            "waves_spawned": self.total_waves_spawned,
            "active_obstacles": len(self.obstacles),
            "obstacles_spawned": self.total_obstacles_spawned,
            "obstacles_removed": self.total_obstacles_removed,
            "distance_until_next_spawn": round(self.distance_until_next_spawn, 2),
            "active_collectibles": len(self.collectibles),
            "collectibles_spawned": self.total_collectibles_spawned,
            "collectibles_removed": self.total_collectibles_removed,
            "type_counts": dict(self.obstacle_type_counts)
        }

    def render(self, renderer: Renderer, shader: ShaderProgram, camera: Camera) -> None:
        """Renders all active obstacles, collectibles, and power-ups."""
        for obs in self.obstacles:
            obs.render(renderer, shader, camera)

        for item in self.collectibles:
            item.render(renderer, shader, camera)

        for p in self.powerups:
            p.render(renderer, shader, camera)

    def reset(self, seed: Optional[int] = None) -> None:
        """Clears all objects and restarts procedural generation."""
        if seed is not None:
            self.rng = random.Random(seed)
            self.np_rng = np.random.default_rng(seed)

        self.obstacles.clear()
        self.collectibles.clear()
        self.powerups.clear()
        self.distance_traveled = 0.0
        self.next_spawn_distance = 0.0
        self.next_powerup_distance = 65.0
        self.total_waves_spawned = 0
        self.total_obstacles_spawned = 0
        self.total_obstacles_removed = 0
        self.total_collectibles_spawned = 0
        self.total_collectibles_removed = 0
        self.total_powerups_spawned = 0
        self.total_powerups_removed = 0
        for k in self.obstacle_type_counts:
            self.obstacle_type_counts[k] = 0

        self._seed_initial_waves()
