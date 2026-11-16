"""
main.py - Disney: Run Through the Stories (Phase 6 Entry Point).
Integrates:
- Reusable 8-world data-driven Disney World Engine (Cinderella, Snow White, Aladdin,
  Tangled, Lion King, Little Mermaid, Peter Pan, Frozen).
- Seamless 2-second crossfade world transitions with dynamic environment palette blending.
- World-specific 3D procedural characters (Runner and Villain).
- World-specific 3D collectibles (Glass Slipper, Magic Apple, Magic Lamp, Sun Symbol,
  Lion Token, Seashell, Pixie Dust, Snowflake).
- World-themed procedural obstacle materials and roadside scenery.
- Dynamic villain chase system with proximity states and HUD meter.
- Modern 2D HUD with world progress timer and world-introduction banners.
"""

import sys
import argparse
from pathlib import Path
import glfw

# Ensure project root is in Python sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import settings
from engine.window import Window
from engine.renderer import Renderer
from engine.shader import ShaderProgram
from engine.camera import Camera
from worlds.track import Track
from worlds.world_config import get_world
from worlds.world_manager import WorldManager
from worlds.transition import WorldTransition
from player.player import Player
from entities.villain import Villain
from entities.obstacle import ObstacleMeshCache, ObstacleType
from entities.collectible import CollectibleMeshCache
from systems.collision import CollisionSystem
from systems.scoring import ScoreManager
from systems.spawning import SpawningManager
from systems.chase import ChaseManager, STATE_CAUGHT
from systems.powerup import PowerUpManager, PowerUpType
from entities.powerup import PowerUpMeshCache
from ui.hud import HUD


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments for interactive or automated execution."""
    parser = argparse.ArgumentParser(description="Disney - Run Through the Stories (Phase 6)")
    parser.add_argument(
        "--frames",
        type=int,
        default=None,
        help="Run for a specific number of frames then exit (useful for automated testing)"
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Run for a specific duration in seconds then exit"
    )
    parser.add_argument(
        "--world-duration",
        type=float,
        default=None,
        help="Duration in seconds per world (defaults to 60.0)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed for deterministic obstacle/collectible spawning"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=True,
        help="Enable HUD debug statistics overlay and logging"
    )
    return parser.parse_args()


class GameApp:
    """Coordinates gameplay loop, multi-world transitions, spawning, HUD, and input."""

    def __init__(self, args: argparse.Namespace):
        self.args = args

        # 1. Window & Context
        self.window = Window(
            width=settings.WINDOW_WIDTH,
            height=settings.WINDOW_HEIGHT,
            title="Disney - Run Through the Stories [Phase 6: Multi-World Engine]",
            vsync=settings.VSYNC
        )

        # 2. Camera
        self.camera = Camera(
            position=settings.CAMERA_POS,
            target=settings.CAMERA_TARGET,
            up=settings.CAMERA_UP,
            fov=settings.DEFAULT_FOV,
            aspect_ratio=self.window.width / self.window.height,
            near=settings.NEAR_CLIP,
            far=settings.FAR_CLIP,
            offset=settings.CAMERA_OFFSET,
            smooth_speed=settings.CAMERA_SMOOTH_SPEED
        )

        # 3. Renderer & Shaders
        self.renderer = Renderer(clear_color=settings.SKY_COLOR)
        vertex_path = settings.SHADERS_DIR / "cube_vertex.glsl"
        fragment_path = settings.SHADERS_DIR / "cube_fragment.glsl"
        self.shader = ShaderProgram(vertex_path, fragment_path)

        # 4. Multi-World Management System
        w_dur = self.args.world_duration if self.args.world_duration is not None else getattr(settings, "WORLD_DURATION", 60.0)
        self.world_mgr = WorldManager(world_duration=w_dur)
        self.transition = WorldTransition()

        # 5. Endless Road Track
        self.track = Track(
            num_segments=settings.NUM_SEGMENTS,
            segment_length=settings.SEGMENT_LENGTH,
            speed=settings.ROAD_SPEED
        )

        # 6. Animated 3D Characters (Player & Villain)
        self.player = Player()
        self.villain = Villain()
        self.chase_mgr = ChaseManager()

        # 7. Gameplay Systems
        self.score_mgr = ScoreManager(base_speed=settings.ROAD_SPEED)
        self.spawner = SpawningManager(seed=self.args.seed)
        self.collision_sys = CollisionSystem()
        self.powerup_mgr = PowerUpManager()

        # Initialize caches for active world
        initial_world = self.world_mgr.current_world
        CollectibleMeshCache.get().init_mesh(initial_world.index, initial_world)
        PowerUpMeshCache.get().init_meshes(initial_world.index, initial_world)
        ObstacleMeshCache.get().init_meshes(
            initial_world.obstacle_primary,
            initial_world.obstacle_secondary,
            initial_world.obstacle_stripe
        )

        # Register World Change Callback across all systems
        self.world_mgr.subscribe(self._on_world_changed)

        # 8. Modern 2D Heads-Up Display
        self.hud = HUD(self.window.width, self.window.height)
        self.show_debug = getattr(self.args, "debug", True)

        # Register Callbacks
        self.window.add_resize_callback(self._on_resize)
        glfw.set_key_callback(self.window.window, self._key_callback)

    def _on_resize(self, width: int, height: int) -> None:
        self.camera.set_aspect_ratio(width, height)
        self.hud.on_resize(width, height)

    def _on_world_changed(self, new_world) -> None:
        """Propagate world change to all graphics and gameplay components."""
        self.track.apply_world_config(new_world)
        self.player.apply_world_config(new_world)
        self.villain.apply_world_config(new_world)
        self.spawner.current_world_index = new_world.index
        CollectibleMeshCache.get().refresh_for_world(new_world.index, new_world)
        PowerUpMeshCache.get().refresh_for_world(new_world.index, new_world)
        ObstacleMeshCache.get().refresh_for_world(new_world)

        # Update existing spawned collectible meshes in-place
        new_col_mesh = CollectibleMeshCache.get().get_mesh()
        for item in self.spawner.collectibles:
            item.mesh = new_col_mesh

    def _key_callback(self, window, key: int, scancode: int, action: int, mods: int) -> None:
        if action == glfw.PRESS:
            if key == glfw.KEY_ESCAPE:
                glfw.set_window_should_close(window, True)
                return
            elif key == glfw.KEY_F3:
                self.show_debug = not self.show_debug
                print(f"HUD Debug Overlay: {'ON' if self.show_debug else 'OFF'}")
                return

            if self.score_mgr.is_game_over:
                if key in (glfw.KEY_SPACE, glfw.KEY_R):
                    self.restart()
                return

            if key in (glfw.KEY_A, glfw.KEY_LEFT):
                self.player.move_left()
            elif key in (glfw.KEY_D, glfw.KEY_RIGHT):
                self.player.move_right()
            elif key in (glfw.KEY_W, glfw.KEY_UP, glfw.KEY_SPACE):
                self.player.jump()
            elif key in (glfw.KEY_S, glfw.KEY_DOWN):
                self.player.slide()

    def restart(self) -> None:
        print("Restarting game run...")
        self.score_mgr.reset()
        self.chase_mgr.reset()
        self.world_mgr.reset()
        self.powerup_mgr.reset()
        self.transition.abort()
        self.spawner.reset(seed=self.args.seed)
        self.player.movement.current_lane = settings.PLAYER_START_LANE
        self.player.movement.x = 0.0
        self.player.movement.target_x = 0.0
        self.player.movement.y = 0.0
        self.player.movement.velocity_y = 0.0
        self.player.movement.is_grounded = True
        self.player.movement.state = "running"
        self.player.movement.slide_timer = 0.0
        self.villain.x = settings.VILLAIN_LATERAL_OFFSET
        self.villain.z = self.chase_mgr.current_distance

    def run(self) -> int:
        print("=" * 60)
        print("Disney: Run Through the Stories - Phase 6 Multi-World Engine")
        print("=" * 60)
        print("Controls:")
        print("  [A] / [Left Arrow]   : Move Left (Lane -1)")
        print("  [D] / [Right Arrow]  : Move Right (Lane +1)")
        print("  [W] / [Up] / [Space] : Jump (Over Ground Barriers)")
        print("  [S] / [Down Arrow]   : Slide (Under Overhead Barriers)")
        print("  [F3]                 : Toggle Debug Telemetry Overlay")
        print("  [Space] / [R]        : Restart after Game Over")
        print("  [ESC]                : Exit application")
        print("=" * 60)

        frame_count = 0
        elapsed_total = 0.0
        last_debug_log = 0.0

        try:
            while not self.window.should_close():
                dt = self.window.update_delta_time()
                elapsed_total += dt
                frame_count += 1

                # ---------------------------------------------------------
                # 1. World Management & Seamless Transitions
                # ---------------------------------------------------------
                if not self.score_mgr.is_game_over:
                    # Update active world timer (triggers transition when expired)
                    should_transition = self.world_mgr.update(dt)
                    if should_transition and not self.transition.is_active:
                        from_w = self.world_mgr.current_world
                        to_w = get_world(self.world_mgr.current_index + 1)
                        t_dur = min(2.0, self.world_mgr.world_duration * 0.4)
                        self.transition.start(from_w, to_w, duration=t_dur)

                    # Update active transition crossfade
                    if self.transition.is_active:
                        switch_fired = self.transition.update(dt)
                        if switch_fired:
                            # Advance the world mid-transition
                            self.world_mgr.advance_world()

                # ---------------------------------------------------------
                # 2. Gameplay Updates (Physics, Movement, Spawning, Chase)
                # ---------------------------------------------------------
                if not self.score_mgr.is_game_over:
                    self.score_mgr.update(dt)
                    current_speed = self.score_mgr.current_speed

                    self.track.speed = current_speed
                    self.track.update(dt)
                    self.spawner.update(current_speed, dt)

                    self.player.update(dt)

                    chase_state = self.chase_mgr.update(dt)
                    if chase_state == STATE_CAUGHT:
                        villain_name = self.world_mgr.current_world.villain_name.upper()
                        print(f"Caught by {villain_name}!")
                        self.score_mgr.trigger_game_over(reason=f"CAUGHT BY {villain_name}!")
                        self.world_mgr.pause()

                    self.villain.update(
                        player_x=self.player.movement.x,
                        player_z=self.player.movement.z,
                        chase_distance=self.chase_mgr.current_distance,
                        proximity_ratio=self.chase_mgr.proximity_ratio,
                        delta_time=dt
                    )

                    # Periodic diagnostic logging
                    if self.show_debug and (elapsed_total - last_debug_log >= 5.0):
                        last_debug_log = elapsed_total
                        st = self.spawner.get_debug_stats()
                        c_st = self.chase_mgr.get_debug_stats()
                        w_st = self.world_mgr.get_debug_stats()
                        print(f"[STATUS] T:{elapsed_total:3.0f}s | W{w_st['world_index']+1}:{w_st['world_name']} "
                              f"({w_st['time_remaining']:.0f}s left) | Score:{self.score_mgr.score} | "
                              f"Pursuit:{c_st['chase_distance']:.2f}m ({c_st['state'].upper()})")

                    # PowerUp Manager Update (Timers, Active Multipliers, Debounce)
                    expired_powerups = self.powerup_mgr.update(dt)
                    if "double_score" in expired_powerups or "world_ability" in expired_powerups:
                        if not self.powerup_mgr.is_active(PowerUpType.DOUBLE_SCORE) and not (
                            self.powerup_mgr.is_active(PowerUpType.WORLD_ABILITY) and
                            getattr(self.world_mgr.current_world, "ability_type", "") == "ocean_surge"
                        ):
                            self.score_mgr.reset_multiplier()

                    # Check Active World Ability Continous Effects
                    active_w = self.powerup_mgr.get_active(PowerUpType.WORLD_ABILITY)
                    active_w_type = getattr(self.world_mgr.current_world, "ability_type", "") if active_w else ""

                    # Ability 0: Glass Slipper Grace (Villain recovery: +1.2m/s pushback)
                    if active_w and active_w_type == "glass_slipper_grace":
                        self.chase_mgr.push_back(1.2 * dt)

                    # Ability 1 & 5: Magnet Surges (Snow White Apple Surge or Ariel Ocean Current)
                    is_magnet_active = (
                        self.powerup_mgr.is_active(PowerUpType.TREASURE_MAGNET) or
                        (active_w and active_w_type in ("apple_surge", "ocean_surge"))
                    )
                    if is_magnet_active:
                        mag_radius = 18.0 if active_w_type in ("apple_surge", "ocean_surge") else 14.0
                        self.collision_sys.apply_magnet_attraction(
                            self.player.movement.x,
                            self.player.movement.y,
                            self.player.movement.z,
                            self.spawner.collectibles,
                            dt,
                            radius=mag_radius,
                            speed=28.0 if active_w_type else 25.0
                        )

                    # Ability 3: Tangled Golden Sun Radiance (Pushes villain back by +0.8m/s)
                    if active_w and active_w_type == "sun_radiance":
                        self.chase_mgr.push_back(0.8 * dt)

                    # Collision Detection: Obstacles
                    hit_obstacle = self.collision_sys.check_player_obstacles(
                        self.player, self.spawner.obstacles
                    )
                    if hit_obstacle is not None:
                        # Flight / Sprint Immunitites:
                        # Aladdin (Magic Carpet Flight): Immune to ground hurdles & overhead barriers
                        if active_w and active_w_type == "carpet_flight" and hit_obstacle.obstacle_type in (
                            ObstacleType.GROUND_BARRIER, ObstacleType.OVERHEAD_BARRIER
                        ):
                            print(f"[ALADDIN] Magic Carpet sailed cleanly over {hit_obstacle.obstacle_type.value}!")
                            hit_obstacle = None

                        # Peter Pan (Pixie Dust Flight): Immune to ground hurdles
                        elif active_w and active_w_type == "pixie_flight" and hit_obstacle.obstacle_type == ObstacleType.GROUND_BARRIER:
                            print(f"[PETER PAN] Pixie Dust glided safely over {hit_obstacle.obstacle_type.value}!")
                            hit_obstacle = None

                        # Simba (Roar of the Pride): Smashes right through ground hurdles
                        elif active_w and active_w_type == "roar_pride" and hit_obstacle.obstacle_type == ObstacleType.GROUND_BARRIER:
                            print(f"[SIMBA] Roar of the Pride smashed through {hit_obstacle.obstacle_type.value}!")
                            hit_obstacle = None

                        # Tangled (Golden Sun Radiance): Absorbs stumbles without penalty
                        elif active_w and active_w_type == "sun_radiance" and hit_obstacle.obstacle_type != ObstacleType.FULL_BLOCKER:
                            print(f"[TANGLED] Golden Sun Radiance shielded Rapunzel from {hit_obstacle.obstacle_type.value}!")
                            hit_obstacle = None

                        # Universal Magic Shield / Cinderella / Frozen Frost Barrier Aegis
                        elif self.powerup_mgr.is_active(PowerUpType.MAGIC_SHIELD) or (
                            active_w and active_w_type in ("glass_slipper_grace", "frost_barrier")
                        ):
                            consumed = self.powerup_mgr.consume_shield()
                            if consumed:
                                shield_name = "Frost Barrier" if active_w_type == "frost_barrier" else (
                                    "Glass Slipper Grace" if active_w_type == "glass_slipper_grace" else "Magic Shield"
                                )
                                print(f"[{shield_name.upper()}] Absorbed collision on {hit_obstacle.obstacle_type.value}!")
                                if hit_obstacle.obstacle_type == ObstacleType.FULL_BLOCKER:
                                    self.chase_mgr.on_mistake(is_fatal=False)
                                    print(f"[{shield_name.upper()}] Broke Full Blocker! Player stumbled but survived!")
                                hit_obstacle = None

                    if hit_obstacle is not None:
                        if hit_obstacle.obstacle_type == ObstacleType.FULL_BLOCKER:
                            print(f"Crashed into full blocker at Z={hit_obstacle.z:.1f}!")
                            self.chase_mgr.on_mistake(is_fatal=True)
                            self.score_mgr.trigger_game_over(reason="CRASHED INTO FULL BLOCKER!")
                            self.world_mgr.pause()
                        else:
                            penalized = self.chase_mgr.on_mistake(is_fatal=False)
                            if penalized:
                                print(f"[MISTAKE] Stumbled on {hit_obstacle.obstacle_type.value}! Villain closes in!")
                            if self.chase_mgr.is_caught:
                                villain_name = self.world_mgr.current_world.villain_name.upper()
                                self.score_mgr.trigger_game_over(reason=f"CAUGHT BY {villain_name}!")
                                self.world_mgr.pause()

                    # Collision Detection: Collectibles
                    collected_items = self.collision_sys.check_player_collectibles(
                        self.player, self.spawner.collectibles
                    )
                    for _ in collected_items:
                        # Snow White Apple Surge transforms coins to +150 bonus apples!
                        coin_val = 150 if (active_w and active_w_type == "apple_surge") else 50
                        self.score_mgr.add_collectible(value=coin_val)
                        self.chase_mgr.on_collectible()

                    # Collision Detection: Power-Ups
                    collected_powerups = self.collision_sys.check_player_powerups(
                        self.player, self.spawner.powerups
                    )
                    for p in collected_powerups:
                        active = self.powerup_mgr.activate(
                            p.powerup_type,
                            world_index=self.world_mgr.current_index,
                            world_config=self.world_mgr.current_world
                        )
                        print(f"[POWERUP] Collected {active.name}! (Duration: {active.duration:.1f}s)")
                        if p.powerup_type == PowerUpType.DOUBLE_SCORE:
                            self.score_mgr.set_multiplier(2.0)
                        elif p.powerup_type == PowerUpType.WORLD_ABILITY:
                            ab_k = getattr(self.world_mgr.current_world, "ability_type", "")
                            if ab_k == "ocean_surge":
                                self.score_mgr.set_multiplier(2.0)
                            elif ab_k == "sun_radiance":
                                self.chase_mgr.push_back(3.0)  # Immediate burst pushback

                # ---------------------------------------------------------
                # 3. Third-Person Camera Tracking
                # ---------------------------------------------------------
                self.camera.follow(self.player.position, dt)

                # ---------------------------------------------------------
                # 4. Environment Lighting & Sky Atmosphere
                # ---------------------------------------------------------
                if self.transition.is_active:
                    sky_c = self.transition.get_blended_sky()
                    fog_c = list(self.transition.get_blended_fog())
                    light_c = list(self.transition.get_blended_light())
                else:
                    curr_w = self.world_mgr.current_world
                    sky_c = curr_w.sky_color
                    fog_c = list(curr_w.fog_color)
                    light_c = list(curr_w.light_color)

                self.renderer.set_clear_color(*sky_c)
                self.renderer.clear()

                # ---------------------------------------------------------
                # 5. 3D Rendering Passes
                # ---------------------------------------------------------
                # Pass A: 3D Environment Track
                self.track.render(self.renderer, self.shader, self.camera)

                # Pass B: 3D Obstacles & Collectibles
                self.spawner.render(self.renderer, self.shader, self.camera)

                # Pass C: 3D Animated Player Character
                self.player.render(self.renderer, self.shader, self.camera)

                # Pass D: 3D Animated Villain Character
                self.villain.render(self.renderer, self.shader, self.camera)

                # Pass E: 2D Heads-Up Display & World Transition Banners
                self.hud.update_and_render(
                    self.score_mgr,
                    world_mgr=self.world_mgr,
                    transition=self.transition,
                    spawner=self.spawner,
                    chase_mgr=self.chase_mgr,
                    powerup_mgr=self.powerup_mgr,
                    show_debug=self.show_debug
                )

                # ---------------------------------------------------------
                # 6. Swap Buffers & Poll Events
                # ---------------------------------------------------------
                self.window.swap_buffers()
                self.window.poll_events()

                if self.args.frames is not None and frame_count >= self.args.frames:
                    print(f"Reached automated test limit of {frame_count} frames. Exiting cleanly.")
                    break
                if self.args.duration is not None and elapsed_total >= self.args.duration:
                    print(f"Reached automated test duration of {elapsed_total:.2f} seconds. Exiting cleanly.")
                    break

        except Exception as e:
            print(f"Fatal error during execution: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1

        finally:
            self.cleanup()

        return 0

    def cleanup(self) -> None:
        print("Cleaning up GPU resources and shutting down...")
        if self.villain is not None:
            self.villain.delete()
        if self.player is not None:
            self.player.delete()
        if self.track is not None:
            self.track.delete()
        if self.hud is not None:
            self.hud.delete()
        ObstacleMeshCache.get().delete()
        CollectibleMeshCache.get().delete()
        PowerUpMeshCache.get().delete()
        if self.shader is not None:
            self.shader.delete()
        if self.window is not None:
            self.window.close()
        print("Clean shutdown complete.")


def main() -> int:
    args = parse_arguments()
    app = GameApp(args)
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
