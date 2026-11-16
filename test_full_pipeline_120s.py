"""
test_full_pipeline_120s.py - Full OpenGL Rendering & Spawning Simulation for 120 Seconds.
Executes 7,200 full frames with OpenGL draw calls, track, player, HUD, obstacles, and collectibles.
"""

import OpenGL.GL as GL
from main import GameApp, parse_arguments

def run_120s_simulation():
    args = parse_arguments()
    args.seed = 42
    app = GameApp(args)

    print("=== STARTING 120-SECOND FULL OPENGL & SPAWNING TEST ===")
    
    # 120 seconds of continuous simulated execution (7,200 frames)
    for sec in range(1, 121):
        for _ in range(60):
            dt = 1.0 / 60.0
            spd = 22.0 + min(10.0, sec * 0.08)
            
            app.track.speed = spd
            app.track.update(dt)
            app.spawner.update(spd, dt)
            app.player.update(dt)

            # Render full frame
            app.renderer.clear()
            app.track.render(app.renderer, app.shader, app.camera)
            app.spawner.render(app.renderer, app.shader, app.camera)
            app.player.render(app.renderer, app.shader, app.camera)
            app.hud.update_and_render(app.score_mgr, spawner=app.spawner, show_debug=True)

        if sec % 20 == 0:
            err = GL.glGetError()
            assert err == GL.GL_NO_ERROR, f"OpenGL error at sec {sec}: {err}"
            st = app.spawner.get_debug_stats()
            print(
                f"Sec {sec:3d}: Active Obs={st['active_obstacles']:2d}, "
                f"Waves={st['waves_spawned']:3d}, "
                f"Obs Removed={st['obstacles_removed']:3d}, "
                f"Active Coins={st['active_collectibles']:2d}, "
                f"Coins Spawned={st['collectibles_spawned']:3d}"
            )
            assert st["active_obstacles"] > 0, f"Obstacle count dropped to zero at sec {sec}!"
            assert st["waves_spawned"] > 10

    final_stats = app.spawner.get_debug_stats()
    print("\nFinal Stats after 120s:", final_stats)
    
    err = GL.glGetError()
    assert err == GL.GL_NO_ERROR, f"Final OpenGL error check: {err}"
    
    app.cleanup()
    print("\n120-SECOND FULL OPENGL & GAMEPLAY TEST: 100% SUCCESS!")

if __name__ == "__main__":
    run_120s_simulation()
