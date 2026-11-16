"""
test_spawning_120s.py - Automated 120-Second Continuous Spawning Stress Test.
Verifies that obstacles and collectibles spawn continuously throughout 120 seconds
of simulated gameplay (7,200 frames, ~2,640 meters traveled) with zero stalls.
"""

import glfw
from systems.spawning import SpawningManager
from entities.obstacle import ObstacleType, ObstacleMeshCache
from entities.collectible import CollectibleMeshCache

def run_test():
    glfw.init()
    glfw.window_hint(glfw.VISIBLE, False)
    w = glfw.create_window(64, 64, "test", None, None)
    glfw.make_context_current(w)

    spawner = SpawningManager(seed=123)
    stats_start = spawner.get_debug_stats()
    print("Initial stats:", stats_start)

    # 120 seconds of continuous running at 22.0 units/sec (traveling 2,640 units!)
    for sec in range(1, 121):
        for _ in range(60):
            spawner.update(speed=22.0, delta_time=1.0 / 60.0)

        # Assertions every 10 seconds
        if sec % 10 == 0:
            stats = spawner.get_debug_stats()
            print(
                f"Sec {sec:3d} (Dist: {stats['distance_traveled']:5.0f}m): "
                f"Active Obs={stats['active_obstacles']:2d}, "
                f"Total Waves={stats['waves_spawned']:3d}, "
                f"Obs Removed={stats['obstacles_removed']:3d}, "
                f"Active Coins={stats['active_collectibles']:2d}, "
                f"Coins Spawned={stats['collectibles_spawned']:3d}, "
                f"Next in={stats['distance_until_next_spawn']:4.1f}m"
            )

            # Continuous spawning assertions
            assert stats["active_obstacles"] > 0, f"Obstacle count reached zero at sec {sec}!"
            assert stats["active_collectibles"] > 0, f"Collectible count reached zero at sec {sec}!"
            assert stats["waves_spawned"] >= (sec * 0.5), f"Waves stopped incrementing at sec {sec}!"

    stats_end = spawner.get_debug_stats()
    print("\nFinal 120s Stats:", stats_end)

    # Verify all 3 obstacle types were spawned substantially:
    type_counts = stats_end["type_counts"]
    for obs_type, count in type_counts.items():
        print(f"Type {obs_type.value}: {count} spawned")
        assert count >= 15, f"Expected at least 15 of {obs_type}, got {count}"

    ObstacleMeshCache.get().delete()
    CollectibleMeshCache.get().delete()
    glfw.destroy_window(w)
    glfw.terminate()

    print("\n120-SECOND CONTINUOUS SPAWNING VERIFICATION: 100% SUCCESS!")

if __name__ == "__main__":
    run_test()
