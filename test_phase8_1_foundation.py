"""
test_phase8_1_foundation.py - Unit test suite for Phase 8.1 Power-Up Foundation.
Validates:
1. PowerUpType enum and attributes.
2. PowerUp entity instantiations, bounding box, kinematics, and coordinate conventions.
3. Procedural 3D mesh creation for all 4 types (Shield, Magnet, Double Score, World Orb).
4. PowerUpMeshCache singleton behavior, mesh retrieval, and clean GPU disposal.
5. PowerUpManager lifecycle: activation, duration countdown, debounce, and reset.
"""

import sys
from pathlib import Path
import numpy as np

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import settings
from engine.window import Window
from engine.renderer import Renderer
from entities.powerup import (
    PowerUpType, PowerUp, PowerUpMeshCache,
    create_shield_mesh, create_magnet_mesh,
    create_double_score_mesh, create_world_orb_mesh
)
from systems.powerup import PowerUpManager, ActivePowerUp
from worlds.world_config import get_world


def test_powerup_entity_and_kinematics():
    print("[TEST 1] PowerUp Entity Kinematics and Bounding Box...")
    # Test lane coordinates: lane 0 -> x=0.0, lane -1 -> x=-2.4, lane 1 -> x=2.4
    p_center = PowerUp(PowerUpType.MAGIC_SHIELD, lane=0, z=-50.0, base_y=0.95)
    assert abs(p_center.x - 0.0) < 1e-4, f"Center lane X should be 0.0, got {p_center.x}"
    assert abs(p_center.z - (-50.0)) < 1e-4

    p_left = PowerUp(PowerUpType.TREASURE_MAGNET, lane=-1, z=-60.0, base_y=0.95)
    assert abs(p_left.x - (-settings.LANE_WIDTH)) < 1e-4, f"Left lane X should be {-settings.LANE_WIDTH}, got {p_left.x}"

    p_right = PowerUp(PowerUpType.DOUBLE_SCORE, lane=1, z=-70.0, base_y=0.95)
    assert abs(p_right.x - settings.LANE_WIDTH) < 1e-4, f"Right lane X should be {settings.LANE_WIDTH}, got {p_right.x}"

    # Test update movement along +Z
    initial_z = p_center.z
    p_center.update(speed=20.0, delta_time=0.5)
    expected_z = initial_z + (20.0 * 0.5)
    assert abs(p_center.z - expected_z) < 1e-4, f"Z movement mismatch: {p_center.z} vs {expected_z}"

    # Test bounding box dimensions
    min_pt, max_pt = p_center.get_bounding_box()
    assert min_pt[0] < p_center.x < max_pt[0]
    assert min_pt[1] < p_center.y < max_pt[1]
    assert min_pt[2] < p_center.z < max_pt[2]

    # Test recycling boundary
    p_center.z = 10.0
    assert not p_center.is_past_player(threshold_z=15.0)
    p_center.z = 15.5
    assert p_center.is_past_player(threshold_z=15.0)
    print("  -> PASSED")


def test_powerup_manager_lifecycle():
    print("[TEST 2] PowerUpManager Lifecycle & Countdown...")
    mgr = PowerUpManager()

    # Verify initially empty
    assert not mgr.is_active(PowerUpType.MAGIC_SHIELD)
    assert not mgr.is_active(PowerUpType.TREASURE_MAGNET)
    assert not mgr.is_active(PowerUpType.DOUBLE_SCORE)

    # 1. Activate Shield
    active_shield = mgr.activate(PowerUpType.MAGIC_SHIELD)
    assert mgr.is_active(PowerUpType.MAGIC_SHIELD)
    assert active_shield.duration == 15.0
    assert active_shield.charges == 1
    assert not active_shield.is_critical

    # 2. Advance time 5 seconds
    expired = mgr.update(5.0)
    assert len(expired) == 0
    assert abs(active_shield.duration - 10.0) < 1e-4
    assert not active_shield.is_critical

    # 3. Advance to critical (< 3.0s)
    mgr.update(7.5)
    assert abs(active_shield.duration - 2.5) < 1e-4
    assert active_shield.is_critical

    # 4. Consume shield charge
    consumed = mgr.consume_shield()
    assert consumed, "Shield should be successfully consumed"
    assert not mgr.is_active(PowerUpType.MAGIC_SHIELD), "Shield should be removed when charges reach 0"

    # 5. Debounce test
    active_shield2 = mgr.activate(PowerUpType.MAGIC_SHIELD)
    consumed2 = mgr.consume_shield()
    assert not consumed2, "Immediate consumption should fail during debounce window"

    # 6. Expiration test with Magnet
    active_mag = mgr.activate(PowerUpType.TREASURE_MAGNET)
    assert mgr.is_active(PowerUpType.TREASURE_MAGNET)
    expired = mgr.update(13.0)
    assert PowerUpType.TREASURE_MAGNET.value in expired
    assert not mgr.is_active(PowerUpType.TREASURE_MAGNET)

    # 7. World Ability activation with WorldConfig
    world3 = get_world(3)
    active_w = mgr.activate(PowerUpType.WORLD_ABILITY, world_index=3, world_config=world3)
    assert active_w.world_index == 3
    assert mgr.is_active(PowerUpType.WORLD_ABILITY)

    # 8. Reset
    mgr.reset()
    assert len(mgr.active_powerups) == 0
    assert mgr.shield_hit_debounce == 0.0
    print("  -> PASSED")


def test_opengl_procedural_meshes_and_cache():
    print("[TEST 3] OpenGL Procedural Meshes & PowerUpMeshCache in GLFW Context...")
    window = Window(width=640, height=360, title="Phase 8.1 Headless Test", vsync=False)
    renderer = Renderer()

    cache = PowerUpMeshCache.get()
    cache.init_meshes(world_index=0, world_config=get_world(0))

    # Verify all meshes were created and have non-zero geometry
    shield_mesh = cache.get_mesh(PowerUpType.MAGIC_SHIELD)
    assert shield_mesh is not None
    assert shield_mesh.vertex_count > 0, "Shield mesh should have vertices"

    magnet_mesh = cache.get_mesh(PowerUpType.TREASURE_MAGNET)
    assert magnet_mesh is not None
    assert magnet_mesh.vertex_count > 0, "Magnet mesh should have vertices"

    double_mesh = cache.get_mesh(PowerUpType.DOUBLE_SCORE)
    assert double_mesh is not None
    assert double_mesh.vertex_count > 0, "Double score mesh should have vertices"

    orb_mesh = cache.get_mesh(PowerUpType.WORLD_ABILITY)
    assert orb_mesh is not None
    assert orb_mesh.vertex_count > 0, "World orb mesh should have vertices"

    # Verify world transition refresh on the orb mesh
    old_orb = cache.world_orb_mesh
    cache.refresh_for_world(world_index=4, world_config=get_world(4))
    new_orb = cache.get_mesh(PowerUpType.WORLD_ABILITY)
    assert new_orb is not None
    assert cache._world_index == 4

    # Verify entity render call does not raise errors
    from engine.camera import Camera
    from engine.shader import ShaderProgram

    camera = Camera(aspect_ratio=640/360)
    vertex_path = settings.SHADERS_DIR / "cube_vertex.glsl"
    fragment_path = settings.SHADERS_DIR / "cube_fragment.glsl"
    shader = ShaderProgram(vertex_path, fragment_path)

    p = PowerUp(PowerUpType.MAGIC_SHIELD, lane=0, z=-20.0)
    p.render(renderer, shader, camera)

    # Clean shutdown
    cache.delete()
    shader.delete()
    window.close()
    print("  -> PASSED")


def main():
    print("=" * 60)
    print("RUNNING PHASE 8.1 POWER-UP FOUNDATION TESTS")
    print("=" * 60)
    test_powerup_entity_and_kinematics()
    test_powerup_manager_lifecycle()
    test_opengl_procedural_meshes_and_cache()
    print("=" * 60)
    print("ALL PHASE 8.1 TESTS PASSED SUCCESSFULLY! (100% PASS)")
    print("=" * 60)


if __name__ == "__main__":
    main()
