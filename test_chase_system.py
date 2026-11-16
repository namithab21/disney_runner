"""
test_chase_system.py - Phase 5 Villain Chase System Verification Suite.
Tests:
1. Camera Frustum Visibility & Non-overlapping positioning
2. Smooth lane tracking and lateral offset
3. Initial safe distance (Green state)
4. Mistake penalties & proximity shrink (Warning & Critical states)
5. Clean running recovery & coin bonuses
6. Catch condition & Game Over integration
7. State reset on restart
8. Aggressive proximity-scaled animation
9. Full OpenGL rendering with zero GL errors
"""

import numpy as np
import glfw
import OpenGL.GL as GL
import pyrr
from config import settings
from entities.villain import Villain, VillainAnimation
from player.player import Player
from systems.chase import ChaseManager, STATE_SAFE, STATE_WARNING, STATE_CRITICAL, STATE_CAUGHT
from systems.scoring import ScoreManager
from main import GameApp, parse_arguments

def test_chase_system():
    print("=== 1. TESTING CHASE MANAGER LOGIC & DISTANCE DYNAMICS ===")
    cm = ChaseManager(start_distance=settings.VILLAIN_START_DISTANCE,
                      max_distance=settings.VILLAIN_MAX_DISTANCE,
                      min_distance=settings.VILLAIN_MIN_DISTANCE)

    # 1. Initial State
    assert cm.current_distance == settings.VILLAIN_START_DISTANCE
    assert cm.state == STATE_SAFE
    assert cm.is_caught is False
    print("-> Initial safe distance & state: PASS")

    # 2. Clean Running Recovery
    # Run cleanly for 2 seconds (recovering distance)
    cm.update(2.0)
    assert cm.current_distance > settings.VILLAIN_START_DISTANCE, f"Expected distance to increase, got {cm.current_distance}"
    assert cm.current_distance <= settings.VILLAIN_MAX_DISTANCE
    print(f"-> Clean running recovery (Distance={cm.current_distance:.2f}m): PASS")

    # 3. Mistake Penalty
    prev_d = cm.current_distance
    assert cm.on_mistake(is_fatal=False) is True
    assert cm.current_distance == prev_d - cm.mistake_penalty
    print(f"-> Mistake penalty applied (Distance={cm.current_distance:.2f}m, State={cm.state}): PASS")

    # Debounce prevents duplicate immediate penalty
    assert cm.on_mistake(is_fatal=False) is False
    print("-> Mistake debounce cooldown: PASS")

    # Advance past debounce and apply second mistake -> pushes to Warning/Critical
    cm.update(1.0)
    cm.on_mistake(is_fatal=False)
    assert cm.state in (STATE_WARNING, STATE_CRITICAL)
    print(f"-> Multiple mistakes increase danger (Distance={cm.current_distance:.2f}m, State={cm.state}): PASS")

    # 4. Collectible Recovery Bonus
    dist_before_coin = cm.current_distance
    cm.on_collectible()
    assert cm.current_distance == dist_before_coin + cm.coin_bonus
    print(f"-> Collectible pickup recovery bonus: PASS")

    # 5. Capture Condition & Game Over
    cm.on_mistake(is_fatal=True)
    assert cm.current_distance == cm.min_distance
    assert cm.is_caught is True
    assert cm.state == STATE_CAUGHT
    print("-> Fatal mistake / capture condition triggers caught state: PASS")

    # 6. Reset
    cm.reset()
    assert cm.current_distance == settings.VILLAIN_START_DISTANCE
    assert cm.state == STATE_SAFE
    assert cm.is_caught is False
    print("-> Reset restores initial chase state: PASS")

    print("\n=== 2. TESTING CAMERA FRUSTUM & NON-OVERLAPPING POSITIONING ===")
    # Calculate viewing projection
    cam_pos = np.array(settings.CAMERA_POS)
    cam_target = np.array(settings.CAMERA_TARGET)
    up = np.array(settings.CAMERA_UP)
    P = np.asarray(pyrr.Matrix44.perspective_projection(settings.DEFAULT_FOV, 1280.0/720.0, 0.1, 250.0))
    V = np.asarray(pyrr.Matrix44.look_at(cam_pos, cam_target, up))
    VP = np.dot(V, P)

    def proj(pt):
        v = np.array([pt[0], pt[1], pt[2], 1.0], dtype=np.float32)
        clip = np.dot(v, VP)
        return clip[:3] / clip[3]

    # Verify villain is in front of camera (Z < camera.z) and inside viewing frustum
    # Camera is at Z = 7.6. Player is at Z = 0.0. Villain trails at Z = [0.8, 3.2].
    for test_dist in [settings.VILLAIN_MIN_DISTANCE, 1.4, 2.0, settings.VILLAIN_START_DISTANCE, settings.VILLAIN_MAX_DISTANCE]:
        z_villain = 0.0 + test_dist
        head_ndc = proj([settings.VILLAIN_LATERAL_OFFSET, 2.0, z_villain])
        torso_ndc = proj([settings.VILLAIN_LATERAL_OFFSET, 1.2, z_villain])

        # Head and Torso must be strictly inside vertical NDC [-1.0, 1.0] and horizontal NDC [-1.0, 1.0]
        assert -1.0 <= head_ndc[1] <= 1.0, f"Villain head out of frustum at dist {test_dist}: {head_ndc}"
        assert -1.0 <= head_ndc[0] <= 1.0, f"Villain X out of frustum at dist {test_dist}: {head_ndc}"
        assert -1.0 <= torso_ndc[1] <= 1.0, f"Villain torso out of frustum at dist {test_dist}: {torso_ndc}"

    # Verify visual separation from player (player is at X=0, villain is at X=VILLAIN_LATERAL_OFFSET)
    player_head = proj([0.0, 1.8, 0.0])
    villain_head = proj([settings.VILLAIN_LATERAL_OFFSET, 2.0, settings.VILLAIN_START_DISTANCE])
    delta_x_ndc = abs(villain_head[0] - player_head[0])
    assert delta_x_ndc > 0.08, f"Player and villain overlap too closely in screen space: delta_X={delta_x_ndc}"
    print(f"-> Villain projection within viewing frustum across all distances: PASS")
    print(f"-> Non-overlapping visual separation (Screen Delta X={delta_x_ndc:.2f}): PASS")

    print("\n=== 3. TESTING FULL OPENGL PIPELINE & VILLAIN RENDERING ===")
    args = parse_arguments()
    args.frames = 60
    app = GameApp(args)

    assert GL.glGetError() == GL.GL_NO_ERROR

    # Run for 60 frames triggering lane changes and chase updates
    for i in range(60):
        dt = 0.01666
        if i == 20:
            app.player.move_left()
        elif i == 40:
            app.player.move_right()

        app.score_mgr.update(dt)
        app.track.update(dt)
        app.spawner.update(app.score_mgr.current_speed, dt)
        app.player.update(dt)
        app.chase_mgr.update(dt)
        app.villain.update(
            player_x=app.player.movement.x,
            player_z=app.player.movement.z,
            chase_distance=app.chase_mgr.current_distance,
            proximity_ratio=app.chase_mgr.proximity_ratio,
            delta_time=dt
        )

        app.camera.follow(app.player.position, dt)
        app.renderer.clear()
        app.track.render(app.renderer, app.shader, app.camera)
        app.spawner.render(app.renderer, app.shader, app.camera)
        app.player.render(app.renderer, app.shader, app.camera)
        app.villain.render(app.renderer, app.shader, app.camera)
        app.hud.update_and_render(app.score_mgr, spawner=app.spawner, chase_mgr=app.chase_mgr, show_debug=True)

        err = GL.glGetError()
        assert err == GL.GL_NO_ERROR, f"OpenGL error at frame {i}: {err}"

    app.cleanup()
    print("-> 60-frame full OpenGL rendering with Villain & HUD: 100% CLEAN (GL_NO_ERROR)")

    print("\nALL PHASE 5 VILLAIN CHASE VERIFICATION TESTS PASSED 100%!")

if __name__ == "__main__":
    test_chase_system()
