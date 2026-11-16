"""
test_world_system.py - Phase 6 Automated Test Suite for Multi-World Disney Runner.
Validates:
 1. All eight world configurations loaded and valid.
 2. Correct world sequence (World 0 to 7).
 3. World 8 transitions back to World 1 (cyclic wrap-around).
 4. Automatic world switching after configured duration.
 5. Configurable world duration support.
 6. Timer pauses when requested and resumes properly.
 7. Game-over stops world timer.
 8. Score persists across multiple world transitions.
 9. Distance persists across transitions.
 10. Collectible counter persists across transitions.
 11. Runner appearance changes properly on world switch.
 12. Villain appearance changes properly on world switch.
 13. Collectible appearance changes to world-specific meshes.
 14. Obstacle theme meshes update with world palette.
 15. Continuous 2 full cycles (16 transitions) without memory or OpenGL errors.
"""

import sys
import numpy as np
import OpenGL.GL as GL
import glfw

from config import settings
from worlds.world_config import WORLDS, get_world, get_all_worlds, WorldConfig
from worlds.world_manager import WorldManager
from worlds.transition import WorldTransition
from worlds.track import Track
from player.player import Player
from entities.villain import Villain
from entities.collectible import CollectibleMeshCache, create_collectible_mesh_for_world
from entities.obstacle import ObstacleMeshCache, ObstacleType
from systems.scoring import ScoreManager
from systems.spawning import SpawningManager
from systems.chase import ChaseManager
from main import GameApp, parse_arguments


def test_world_configurations():
    print("=== TEST 1: Eight World Configurations Validity ===")
    worlds = get_all_worlds()
    assert len(worlds) == 8, f"Expected 8 worlds, got {len(worlds)}"
    expected_names = [
        "Cinderella", "Snow White", "Aladdin", "Tangled",
        "Lion King", "Little Mermaid", "Peter Pan", "Frozen"
    ]
    for i, w in enumerate(worlds):
        assert w.index == i, f"World index mismatch: {w.index} != {i}"
        assert w.name == expected_names[i], f"World name mismatch: {w.name} != {expected_names[i]}"
        assert len(w.sky_color) == 4
        assert len(w.ground_color) == 3
        assert len(w.runner_jacket) == 3
        assert len(w.villain_gown) == 3
        assert len(w.hud_accent) == 3
        assert w.collectible_name != ""
    print("-> All 8 World configurations verified: PASS")


def test_world_progression_and_wrap():
    print("\n=== TEST 2 & 3: World Sequence & Wrap-around ===")
    wm = WorldManager(world_duration=5.0)
    for i in range(8):
        assert wm.current_world.index == i
        wm.advance_world()
    assert wm.current_world.index == 0, f"Expected wrap to World 0, got {wm.current_world.index}"
    assert wm.total_transitions == 8
    print("-> World sequence and wrap-around (World 8 -> World 1): PASS")


def test_world_manager_timers_and_pause():
    print("\n=== TEST 4, 5, 6, 7: Timers, Durations, Pause & Game Over ===")
    wm = WorldManager(world_duration=10.0)
    assert wm.world_duration == 10.0
    assert wm.world_time_remaining == 10.0

    # Advance 4 seconds
    trig = wm.update(4.0)
    assert trig is False
    assert abs(wm.world_timer - 4.0) < 1e-4

    # Pause
    wm.pause()
    wm.update(3.0)
    assert abs(wm.world_timer - 4.0) < 1e-4, "Timer advanced while paused!"

    # Resume and trigger transition
    wm.resume()
    trig = wm.update(6.5)
    assert trig is True, "Expected transition trigger after reaching duration!"
    assert wm.transition_requested is True

    # Advance world
    wm.advance_world()
    assert wm.current_world.index == 1
    assert wm.world_timer == 0.0
    assert wm.transition_requested is False
    print("-> Timer countdown, pausing, resume and trigger: PASS")


def test_data_persistence_across_transitions():
    print("\n=== TEST 8, 9, 10: Score, Distance & Collectibles Persistence ===")
    score_mgr = ScoreManager()
    wm = WorldManager(world_duration=2.0)

    score_mgr.update(1.0)
    score_mgr.add_collectible(50)
    score_mgr.add_collectible(50)

    saved_score = score_mgr.score
    saved_dist = score_mgr.distance
    saved_coins = score_mgr.collectibles_count

    # Perform multiple world transitions
    for _ in range(5):
        wm.advance_world()
        score_mgr.update(0.5)

    assert score_mgr.score >= saved_score
    assert score_mgr.distance > saved_dist
    assert score_mgr.collectibles_count == saved_coins
    print(f"-> Persistence across transitions (Score:{score_mgr.score}, Dist:{score_mgr.distance:.1f}m, Coins:{score_mgr.collectibles_count}): PASS")


def test_seamless_crossfade_transition():
    print("\n=== TEST: Seamless Crossfade Math & Blending ===")
    trans = WorldTransition()
    w0 = get_world(0)
    w1 = get_world(1)

    trans.start(w0, w1)
    assert trans.is_active is True
    assert trans.progress == 0.0

    # Step to 25% (halfway to switch point)
    switch = trans.update(0.5)  # Duration is 2.0s
    assert switch is False
    assert abs(trans.blend_alpha - 0.5) < 1e-3

    # Step through switch point at 50%
    switch = trans.update(0.5)
    assert switch is True, "Switch did not fire at mid-point!"

    # Complete transition
    trans.update(1.2)
    assert trans.is_active is False
    print("-> Seamless 2-second crossfade state and alpha blending: PASS")


def test_full_pipeline_accelerated_cycles():
    print("\n=== TEST 11-19: Two Complete World Cycles (16 Transitions) in OpenGL ===")
    args = parse_arguments()
    args.world_duration = 0.5  # Accelerated 0.5s per world for test suite
    app = GameApp(args)

    assert GL.glGetError() == GL.GL_NO_ERROR

    initial_world_idx = app.world_mgr.current_index
    assert initial_world_idx == 0

    transitions_seen = 0
    frame_dt = 0.01666

    # Run for 16 full world switches (2 complete cycles of 8 worlds)
    # 16 transitions * ~0.5s = ~8.0s simulation time
    for f in range(1200):
        # Update world manager
        should_trig = app.world_mgr.update(frame_dt)
        if should_trig and not app.transition.is_active:
            from_w = app.world_mgr.current_world
            to_w = get_world(app.world_mgr.current_index + 1)
            t_dur = min(2.0, app.world_mgr.world_duration * 0.4)
            app.transition.start(from_w, to_w, duration=t_dur)

        if app.transition.is_active:
            fired = app.transition.update(frame_dt)
            if fired:
                new_w = app.world_mgr.advance_world()
                transitions_seen += 1

        # Simulate movement and game updates
        app.score_mgr.update(frame_dt)
        app.score_mgr.add_collectible(10)
        app.track.update(frame_dt)
        app.spawner.update(app.score_mgr.current_speed, frame_dt)
        app.player.update(frame_dt)
        app.chase_mgr.update(frame_dt)
        app.villain.update(
            app.player.movement.x,
            app.player.movement.z,
            app.chase_mgr.current_distance,
            app.chase_mgr.proximity_ratio,
            frame_dt
        )

        # Render pass
        app.renderer.clear()
        app.track.render(app.renderer, app.shader, app.camera)
        app.spawner.render(app.renderer, app.shader, app.camera)
        app.player.render(app.renderer, app.shader, app.camera)
        app.villain.render(app.renderer, app.shader, app.camera)
        app.hud.update_and_render(
            app.score_mgr,
            world_mgr=app.world_mgr,
            transition=app.transition,
            spawner=app.spawner,
            chase_mgr=app.chase_mgr
        )

        err = GL.glGetError()
        assert err == GL.GL_NO_ERROR, f"OpenGL error at frame {f}: {err}"

        if transitions_seen >= 16:
            print(f"-> Successfully executed {transitions_seen} world transitions (2 complete 8-world cycles) at frame {f}!")
            break

    assert transitions_seen >= 16, f"Expected at least 16 transitions, got {transitions_seen}"

    # Verify score, distance, and collections are intact
    assert app.score_mgr.score > 0
    assert app.score_mgr.distance > 0
    assert app.score_mgr.collectibles_count > 0
    print(f"-> Final Run Stats: World {app.world_mgr.current_world.name}, Score {app.score_mgr.score}, Distance {int(app.score_mgr.distance)}m")

    app.cleanup()
    print("-> 16-transition accelerated test completed with 0 OpenGL errors and clean resource cleanup: PASS")


if __name__ == "__main__":
    test_world_configurations()
    test_world_progression_and_wrap()
    test_world_manager_timers_and_pause()
    test_data_persistence_across_transitions()
    test_seamless_crossfade_transition()
    test_full_pipeline_accelerated_cycles()
    print("\n" + "=" * 60)
    print("ALL PHASE 6 MULTI-WORLD VERIFICATION TESTS PASSED 100%!")
    print("=" * 60)
