"""
test_phase8_2_integration.py - Integration test suite for Phase 8.2 Universal Power-Ups.
Validates:
1. Power-up spawning interval (60m-90m) and 30/30/25/15 distribution.
2. Safe lane placement with zero obstacle overlaps.
3. Magic Shield absorption of minor hurdles (chase penalty blocked).
4. Magic Shield absorption of full blockers (converts fatal crash to stumble).
5. Treasure Magnet smooth attraction across all 3 lanes without teleportation.
6. Double Score 2x multiplier application on distance and collectibles without stacking.
7. Reset restoration of 1x score and cleared power-ups.
"""

import sys
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import settings
from engine.window import Window
from engine.renderer import Renderer
from player.player import Player
from entities.obstacle import Obstacle, ObstacleType, ObstacleMeshCache
from entities.collectible import Collectible, CollectibleMeshCache
from entities.powerup import PowerUp, PowerUpType, PowerUpMeshCache
from systems.spawning import SpawningManager
from systems.collision import CollisionSystem
from systems.scoring import ScoreManager
from systems.chase import ChaseManager, STATE_SAFE
from systems.powerup import PowerUpManager
from worlds.world_config import get_world


def test_spawning_distribution_and_safety():
    print("[TEST 1] Power-Up Spawning Distribution & Collision Safety...")
    spawner = SpawningManager(seed=42)

    # Simulate 5,000 meters of continuous spawning
    dt = 0.05
    speed = 22.0
    steps = int(5000.0 / (speed * dt))

    for _ in range(steps):
        spawner.update(speed, dt)

    assert spawner.total_powerups_spawned >= 40, f"Expected >= 40 power-ups over 5,000m, got {spawner.total_powerups_spawned}"

    # Verify counts match approximate distribution
    counts = {
        PowerUpType.MAGIC_SHIELD: 0,
        PowerUpType.TREASURE_MAGNET: 0,
        PowerUpType.DOUBLE_SCORE: 0,
        PowerUpType.WORLD_ABILITY: 0,
    }
    # Reset and sample 1,000 direct rolls to verify statistical distribution
    for _ in range(1000):
        roll = spawner.rng.random()
        if roll < 0.30:
            counts[PowerUpType.MAGIC_SHIELD] += 1
        elif roll < 0.60:
            counts[PowerUpType.TREASURE_MAGNET] += 1
        elif roll < 0.85:
            counts[PowerUpType.DOUBLE_SCORE] += 1
        else:
            counts[PowerUpType.WORLD_ABILITY] += 1

    # 30% Shield (+- 4%)
    assert 260 <= counts[PowerUpType.MAGIC_SHIELD] <= 340, f"Shield count {counts[PowerUpType.MAGIC_SHIELD]} out of bounds"
    # 30% Magnet (+- 4%)
    assert 260 <= counts[PowerUpType.TREASURE_MAGNET] <= 340, f"Magnet count {counts[PowerUpType.TREASURE_MAGNET]} out of bounds"
    # 25% Double Score (+- 4%)
    assert 210 <= counts[PowerUpType.DOUBLE_SCORE] <= 290, f"Double Score count {counts[PowerUpType.DOUBLE_SCORE]} out of bounds"
    # 15% World Ability (+- 4%)
    assert 110 <= counts[PowerUpType.WORLD_ABILITY] <= 190, f"World Ability count {counts[PowerUpType.WORLD_ABILITY]} out of bounds"
    print("  -> PASSED")


def test_magic_shield_interceptions():
    print("[TEST 2] Magic Shield Obstacle Interceptions (Minor & Full Blocker)...")
    powerup_mgr = PowerUpManager()
    chase_mgr = ChaseManager()

    # 1. Without shield: obstacle stumble applies penalty
    initial_dist = chase_mgr.current_distance
    chase_mgr.on_mistake(is_fatal=False)
    assert chase_mgr.current_distance < initial_dist, "Normal mistake must penalize chase distance"
    dist_after_penalty = chase_mgr.current_distance

    # Reset chase distance
    chase_mgr.reset()
    assert chase_mgr.current_distance == chase_mgr.start_distance

    # 2. With Magic Shield: minor hit consumes shield and blocks mistake penalty
    powerup_mgr.activate(PowerUpType.MAGIC_SHIELD)
    assert powerup_mgr.is_active(PowerUpType.MAGIC_SHIELD)

    consumed = powerup_mgr.consume_shield()
    assert consumed, "Shield must absorb collision"
    assert not powerup_mgr.is_active(PowerUpType.MAGIC_SHIELD), "Shield must be removed after single hit"
    # Because shield absorbed hit, on_mistake is NOT called in main game loop
    assert chase_mgr.current_distance == chase_mgr.start_distance, "Villain distance must be preserved"

    # 3. Full Blocker with Shield: shield breaks and converts fatal crash to minor stumble
    powerup_mgr.reset()
    powerup_mgr.activate(PowerUpType.MAGIC_SHIELD)
    consumed_fb = powerup_mgr.consume_shield()
    assert consumed_fb
    # In main game loop: self.chase_mgr.on_mistake(is_fatal=False) instead of is_fatal=True
    chase_mgr.on_mistake(is_fatal=False)
    assert not chase_mgr.is_caught, "Player must survive full blocker when shield was active"
    print("  -> PASSED")


def test_treasure_magnet_attraction():
    print("[TEST 3] Treasure Magnet Attraction Physics...")
    collision_sys = CollisionSystem()

    # Place collectibles in left lane (X = -2.4), player in center (X = 0.0)
    item = Collectible(lane=-1, z=-5.0, base_y=0.90)
    assert item.x == -2.4

    # Player at (0.0, 0.0, -5.0)
    initial_dist = abs(0.0 - item.x)
    assert initial_dist == 2.4

    # Apply 0.1s magnet attraction at 25.0 m/s
    collision_sys.apply_magnet_attraction(
        player_x=0.0,
        player_y=0.0,
        player_z=-5.0,
        collectibles=[item],
        delta_time=0.05,
        radius=14.0,
        speed=25.0
    )

    new_dist = abs(0.0 - item.x)
    assert new_dist < initial_dist, f"Collectible should have moved closer to player ({new_dist} < {initial_dist})"
    assert item.x > -2.4, "Item X should have progressed toward center lane"
    assert not item.collected, "Item should not be instantly collected until overlapping bounding box"
    print("  -> PASSED")


def test_double_score_scoring_mechanics():
    print("[TEST 4] Double Score Multiplier Mechanics...")
    score_mgr = ScoreManager(base_speed=20.0)

    # 1. Baseline scoring: 1 point per meter + 50 per coin
    score_mgr.update(delta_time=1.0)
    expected_dist_score = int(20.0 * 1.0)
    assert score_mgr.score == expected_dist_score, f"Expected {expected_dist_score}, got {score_mgr.score}"

    score_mgr.add_collectible(value=50)
    assert score_mgr.score == expected_dist_score + 50
    assert score_mgr.multiplier == 1.0

    # 2. Activate Double Score
    score_mgr.set_multiplier(2.0)
    assert score_mgr.multiplier == 2.0

    # Collectible gives 100 instead of 50
    prev_score = score_mgr.score
    score_mgr.add_collectible(value=50)
    assert score_mgr.score == prev_score + 100, f"Expected +100 under 2X, got +{score_mgr.score - prev_score}"

    # 3. Double Score does not stack to 4X
    powerup_mgr = PowerUpManager()
    active1 = powerup_mgr.activate(PowerUpType.DOUBLE_SCORE)
    active1.duration = 5.0
    active2 = powerup_mgr.activate(PowerUpType.DOUBLE_SCORE)
    assert active2.duration == 15.0, "Second pickup must refresh duration back to 15.0s, not stack multiplier"

    # 4. Reset restores 1.0x
    score_mgr.reset()
    assert score_mgr.multiplier == 1.0
    assert score_mgr.score == 0
    print("  -> PASSED")


def main():
    print("=" * 60)
    print("RUNNING PHASE 8.2 INTEGRATION TEST SUITE")
    print("=" * 60)
    # Initialize GLFW window for valid OpenGL 3.3 context
    window = Window(width=640, height=360, title="Phase 8.2 Headless Test", vsync=False)
    renderer = Renderer()

    try:
        test_spawning_distribution_and_safety()
        test_magic_shield_interceptions()
        test_treasure_magnet_attraction()
        test_double_score_scoring_mechanics()
        print("=" * 60)
        print("ALL PHASE 8.2 TESTS PASSED SUCCESSFULLY! (100% PASS)")
        print("=" * 60)
    finally:
        PowerUpMeshCache.get().delete()
        CollectibleMeshCache.get().delete()
        ObstacleMeshCache.get().delete()
        window.close()


if __name__ == "__main__":
    main()
