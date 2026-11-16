"""
world_config.py - Data-driven Disney World Configuration System.
Defines all eight Disney-inspired worlds as pure configuration objects.
No game logic lives here — only theme data consumed by other systems.
"""

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass(frozen=True)
class WorldConfig:
    """Immutable configuration for a single Disney story world."""

    # Identity
    index: int                   # 0-based index (0 = Cinderella, ..., 7 = Frozen)
    name: str                    # Display name ("Cinderella")
    subtitle: str                # Story subtitle ("A Cinderella Story")

    # Environment Colours  (R, G, B as 0.0–1.0 floats)
    sky_color: Tuple[float, float, float, float]   # (R, G, B, A)
    ground_color: Tuple[float, float, float]        # Grass / terrain tint
    road_color_side: Tuple[float, float, float]     # Outer lane asphalt tint
    road_color_center: Tuple[float, float, float]   # Center lane asphalt tint
    sidewalk_color: Tuple[float, float, float]      # Sidewalk / curb surface tint
    fog_color: Tuple[float, float, float]           # Atmospheric fog (matches sky)

    # Lighting
    light_pos: Tuple[float, float, float]           # World-space sun/light position
    light_color: Tuple[float, float, float]         # Sunlight color

    # Fog parameters
    fog_start: float
    fog_end: float

    # Scenery style tag (used by RoadSegment to pick decoration style)
    # Options: "kingdom", "forest", "desert", "lanterns", "savanna",
    #          "underwater", "neverland", "snow"
    scenery_style: str

    # Foliage / tree tint override for roadside trees
    foliage_tint: Tuple[float, float, float]

    # Runner character
    runner_name: str
    runner_jacket: Tuple[float, float, float]
    runner_pants: Tuple[float, float, float]
    runner_shoes: Tuple[float, float, float]
    runner_hair: Tuple[float, float, float]
    runner_skin: Tuple[float, float, float]
    runner_accent: Tuple[float, float, float]       # Headband / trim accent

    # Villain character
    villain_name: str
    villain_gown: Tuple[float, float, float]
    villain_accent: Tuple[float, float, float]      # Collar / trim / brooch
    villain_hair: Tuple[float, float, float]
    villain_skin: Tuple[float, float, float]

    # Collectible
    collectible_name: str                           # e.g. "Glass Slipper"
    collectible_color_primary: Tuple[float, float, float]
    collectible_color_secondary: Tuple[float, float, float]
    collectible_color_highlight: Tuple[float, float, float]

    # Obstacle theme tint (applied to procedural geometry)
    obstacle_primary: Tuple[float, float, float]
    obstacle_secondary: Tuple[float, float, float]
    obstacle_stripe: Tuple[float, float, float]

    # HUD accent color (border / badge highlight)
    hud_accent: Tuple[int, int, int]                # 0–255 RGB for Pillow

    # World-Specific Ability Metadata (Phase 8.3)
    ability_name: str = "World Ability"
    ability_duration: float = 10.0
    ability_type: str = "generic"                   # Ability key identifier
    ability_color: Tuple[int, int, int] = (255, 255, 255)


# =============================================================================
# WORLD DEFINITIONS
# =============================================================================

WORLDS: List[WorldConfig] = [

    # -------------------------------------------------------------------------
    # World 0 — CINDERELLA
    # -------------------------------------------------------------------------
    WorldConfig(
        index=0,
        name="Cinderella",
        subtitle="Run Through the Kingdom!",
        sky_color=(0.42, 0.65, 0.88, 1.0),
        ground_color=(0.22, 0.52, 0.25),
        road_color_side=(0.20, 0.21, 0.24),
        road_color_center=(0.24, 0.25, 0.29),
        sidewalk_color=(0.58, 0.58, 0.60),
        fog_color=(0.42, 0.65, 0.88),
        light_pos=(15.0, 35.0, 20.0),
        light_color=(1.0, 0.98, 0.92),
        fog_start=70.0,
        fog_end=210.0,
        scenery_style="kingdom",
        foliage_tint=(0.14, 0.50, 0.22),
        runner_name="Cinderella",
        runner_jacket=(0.18, 0.46, 0.88),
        runner_pants=(0.16, 0.18, 0.24),
        runner_shoes=(0.88, 0.20, 0.22),
        runner_hair=(0.52, 0.38, 0.28),
        runner_skin=(0.92, 0.78, 0.66),
        runner_accent=(0.88, 0.22, 0.22),
        villain_name="Evil Stepmother",
        villain_gown=(0.38, 0.08, 0.14),
        villain_accent=(0.95, 0.82, 0.22),
        villain_hair=(0.75, 0.75, 0.80),
        villain_skin=(0.88, 0.80, 0.78),
        collectible_name="Glass Slipper",
        collectible_color_primary=(0.68, 0.90, 1.00),
        collectible_color_secondary=(0.42, 0.72, 0.95),
        collectible_color_highlight=(1.00, 1.00, 1.00),
        obstacle_primary=(0.42, 0.26, 0.15),
        obstacle_secondary=(0.65, 0.42, 0.24),
        obstacle_stripe=(0.96, 0.86, 0.20),
        hud_accent=(65, 140, 240),
        ability_name="Glass Slipper Grace",
        ability_duration=12.0,
        ability_type="glass_slipper_grace",
        ability_color=(120, 210, 255),
    ),

    # -------------------------------------------------------------------------
    # World 1 — SNOW WHITE
    # -------------------------------------------------------------------------
    WorldConfig(
        index=1,
        name="Snow White",
        subtitle="Flee Through the Enchanted Forest!",
        sky_color=(0.18, 0.28, 0.20, 1.0),
        ground_color=(0.12, 0.35, 0.14),
        road_color_side=(0.16, 0.19, 0.16),
        road_color_center=(0.20, 0.23, 0.20),
        sidewalk_color=(0.30, 0.42, 0.30),
        fog_color=(0.18, 0.28, 0.20),
        light_pos=(5.0, 20.0, 15.0),
        light_color=(0.75, 0.90, 0.80),
        fog_start=55.0,
        fog_end=170.0,
        scenery_style="forest",
        foliage_tint=(0.10, 0.38, 0.14),
        runner_name="Snow White",
        runner_jacket=(0.68, 0.10, 0.12),
        runner_pants=(0.90, 0.90, 0.95),
        runner_shoes=(0.14, 0.12, 0.22),
        runner_hair=(0.08, 0.06, 0.08),
        runner_skin=(0.94, 0.86, 0.82),
        runner_accent=(0.95, 0.90, 0.95),
        villain_name="Evil Queen",
        villain_gown=(0.22, 0.05, 0.28),
        villain_accent=(0.85, 0.75, 0.10),
        villain_hair=(0.08, 0.06, 0.08),
        villain_skin=(0.90, 0.85, 0.82),
        collectible_name="Magic Apple",
        collectible_color_primary=(0.90, 0.12, 0.12),
        collectible_color_secondary=(0.68, 0.08, 0.08),
        collectible_color_highlight=(1.00, 0.70, 0.60),
        obstacle_primary=(0.22, 0.38, 0.18),
        obstacle_secondary=(0.30, 0.50, 0.24),
        obstacle_stripe=(0.85, 0.75, 0.10),
        hud_accent=(90, 180, 80),
        ability_name="Enchanted Apple Surge",
        ability_duration=10.0,
        ability_type="apple_surge",
        ability_color=(255, 60, 60),
    ),

    # -------------------------------------------------------------------------
    # World 2 — ALADDIN
    # -------------------------------------------------------------------------
    WorldConfig(
        index=2,
        name="Aladdin",
        subtitle="Race Through Agrabah!",
        sky_color=(0.88, 0.60, 0.22, 1.0),
        ground_color=(0.72, 0.56, 0.28),
        road_color_side=(0.55, 0.42, 0.22),
        road_color_center=(0.62, 0.48, 0.28),
        sidewalk_color=(0.72, 0.60, 0.38),
        fog_color=(0.88, 0.60, 0.22),
        light_pos=(25.0, 40.0, 10.0),
        light_color=(1.0, 0.95, 0.75),
        fog_start=80.0,
        fog_end=220.0,
        scenery_style="desert",
        foliage_tint=(0.55, 0.52, 0.18),
        runner_name="Aladdin",
        runner_jacket=(0.68, 0.52, 0.18),
        runner_pants=(0.90, 0.85, 0.72),
        runner_shoes=(0.30, 0.22, 0.12),
        runner_hair=(0.10, 0.08, 0.06),
        runner_skin=(0.72, 0.52, 0.32),
        runner_accent=(0.50, 0.12, 0.60),
        villain_name="Jafar",
        villain_gown=(0.08, 0.06, 0.08),
        villain_accent=(0.88, 0.75, 0.10),
        villain_hair=(0.06, 0.04, 0.04),
        villain_skin=(0.62, 0.48, 0.38),
        collectible_name="Magic Lamp",
        collectible_color_primary=(0.95, 0.80, 0.22),
        collectible_color_secondary=(0.78, 0.60, 0.12),
        collectible_color_highlight=(1.00, 0.95, 0.65),
        obstacle_primary=(0.68, 0.52, 0.28),
        obstacle_secondary=(0.82, 0.68, 0.40),
        obstacle_stripe=(0.50, 0.12, 0.60),
        hud_accent=(220, 165, 40),
        ability_name="Magic Carpet Flight",
        ability_duration=6.0,
        ability_type="carpet_flight",
        ability_color=(255, 190, 40),
    ),

    # -------------------------------------------------------------------------
    # World 3 — TANGLED
    # -------------------------------------------------------------------------
    WorldConfig(
        index=3,
        name="Tangled",
        subtitle="Run Through the Lantern Festival!",
        sky_color=(0.52, 0.38, 0.72, 1.0),
        ground_color=(0.38, 0.55, 0.28),
        road_color_side=(0.32, 0.26, 0.42),
        road_color_center=(0.38, 0.30, 0.50),
        sidewalk_color=(0.52, 0.48, 0.60),
        fog_color=(0.52, 0.38, 0.72),
        light_pos=(10.0, 30.0, 25.0),
        light_color=(1.0, 0.95, 0.80),
        fog_start=65.0,
        fog_end=195.0,
        scenery_style="lanterns",
        foliage_tint=(0.22, 0.52, 0.18),
        runner_name="Rapunzel",
        runner_jacket=(0.68, 0.48, 0.80),
        runner_pants=(0.52, 0.38, 0.62),
        runner_shoes=(0.38, 0.28, 0.48),
        runner_hair=(0.92, 0.82, 0.22),
        runner_skin=(0.95, 0.82, 0.70),
        runner_accent=(0.95, 0.82, 0.22),
        villain_name="Mother Gothel",
        villain_gown=(0.28, 0.12, 0.18),
        villain_accent=(0.72, 0.60, 0.30),
        villain_hair=(0.12, 0.08, 0.08),
        villain_skin=(0.80, 0.70, 0.65),
        collectible_name="Sun Symbol",
        collectible_color_primary=(1.00, 0.88, 0.22),
        collectible_color_secondary=(0.95, 0.72, 0.10),
        collectible_color_highlight=(1.00, 1.00, 0.80),
        obstacle_primary=(0.42, 0.32, 0.55),
        obstacle_secondary=(0.60, 0.48, 0.70),
        obstacle_stripe=(0.95, 0.82, 0.22),
        hud_accent=(180, 120, 240),
        ability_name="Golden Sun Radiance",
        ability_duration=12.0,
        ability_type="sun_radiance",
        ability_color=(255, 230, 70),
    ),

    # -------------------------------------------------------------------------
    # World 4 — LION KING
    # -------------------------------------------------------------------------
    WorldConfig(
        index=4,
        name="Lion King",
        subtitle="Charge Across the Savanna!",
        sky_color=(0.90, 0.60, 0.22, 1.0),
        ground_color=(0.62, 0.48, 0.18),
        road_color_side=(0.48, 0.38, 0.18),
        road_color_center=(0.55, 0.44, 0.22),
        sidewalk_color=(0.65, 0.52, 0.28),
        fog_color=(0.90, 0.60, 0.22),
        light_pos=(30.0, 45.0, 5.0),
        light_color=(1.0, 0.90, 0.72),
        fog_start=80.0,
        fog_end=230.0,
        scenery_style="savanna",
        foliage_tint=(0.52, 0.48, 0.12),
        runner_name="Simba",
        runner_jacket=(0.88, 0.70, 0.30),
        runner_pants=(0.72, 0.52, 0.18),
        runner_shoes=(0.48, 0.32, 0.12),
        runner_hair=(0.72, 0.52, 0.18),
        runner_skin=(0.88, 0.72, 0.42),
        runner_accent=(0.90, 0.68, 0.18),
        villain_name="Scar",
        villain_gown=(0.22, 0.18, 0.08),
        villain_accent=(0.68, 0.55, 0.12),
        villain_hair=(0.12, 0.10, 0.08),
        villain_skin=(0.55, 0.45, 0.28),
        collectible_name="Lion Token",
        collectible_color_primary=(0.90, 0.72, 0.22),
        collectible_color_secondary=(0.72, 0.52, 0.12),
        collectible_color_highlight=(1.00, 0.90, 0.60),
        obstacle_primary=(0.55, 0.42, 0.18),
        obstacle_secondary=(0.70, 0.55, 0.28),
        obstacle_stripe=(0.90, 0.68, 0.18),
        hud_accent=(220, 140, 40),
        ability_name="Roar of the Pride",
        ability_duration=6.0,
        ability_type="roar_pride",
        ability_color=(255, 140, 30),
    ),

    # -------------------------------------------------------------------------
    # World 5 — LITTLE MERMAID
    # -------------------------------------------------------------------------
    WorldConfig(
        index=5,
        name="Little Mermaid",
        subtitle="Swim Through the Coral Kingdom!",
        sky_color=(0.08, 0.38, 0.72, 1.0),
        ground_color=(0.12, 0.42, 0.65),
        road_color_side=(0.10, 0.30, 0.52),
        road_color_center=(0.12, 0.35, 0.60),
        sidewalk_color=(0.18, 0.50, 0.70),
        fog_color=(0.08, 0.38, 0.72),
        light_pos=(0.0, 20.0, 30.0),
        light_color=(0.72, 0.90, 1.00),
        fog_start=50.0,
        fog_end=160.0,
        scenery_style="underwater",
        foliage_tint=(0.12, 0.60, 0.65),
        runner_name="Ariel",
        runner_jacket=(0.68, 0.10, 0.22),
        runner_pants=(0.12, 0.65, 0.68),
        runner_shoes=(0.12, 0.65, 0.68),
        runner_hair=(0.80, 0.12, 0.12),
        runner_skin=(0.95, 0.82, 0.72),
        runner_accent=(0.80, 0.12, 0.12),
        villain_name="Ursula",
        villain_gown=(0.22, 0.10, 0.28),
        villain_accent=(0.70, 0.65, 0.78),
        villain_hair=(0.90, 0.88, 0.95),
        villain_skin=(0.60, 0.55, 0.72),
        collectible_name="Seashell",
        collectible_color_primary=(0.95, 0.80, 0.70),
        collectible_color_secondary=(0.90, 0.65, 0.55),
        collectible_color_highlight=(1.00, 0.95, 0.90),
        obstacle_primary=(0.18, 0.42, 0.65),
        obstacle_secondary=(0.25, 0.60, 0.80),
        obstacle_stripe=(0.90, 0.60, 0.72),
        hud_accent=(40, 160, 220),
        ability_name="Ocean Current Surge",
        ability_duration=10.0,
        ability_type="ocean_surge",
        ability_color=(40, 220, 240),
    ),

    # -------------------------------------------------------------------------
    # World 6 — PETER PAN
    # -------------------------------------------------------------------------
    WorldConfig(
        index=6,
        name="Peter Pan",
        subtitle="Fly Over Neverland!",
        sky_color=(0.22, 0.52, 0.42, 1.0),
        ground_color=(0.18, 0.46, 0.22),
        road_color_side=(0.18, 0.28, 0.22),
        road_color_center=(0.22, 0.32, 0.26),
        sidewalk_color=(0.30, 0.46, 0.35),
        fog_color=(0.22, 0.52, 0.42),
        light_pos=(10.0, 38.0, 18.0),
        light_color=(0.90, 0.95, 0.80),
        fog_start=65.0,
        fog_end=195.0,
        scenery_style="neverland",
        foliage_tint=(0.12, 0.46, 0.20),
        runner_name="Peter Pan",
        runner_jacket=(0.18, 0.52, 0.22),
        runner_pants=(0.18, 0.52, 0.22),
        runner_shoes=(0.30, 0.22, 0.12),
        runner_hair=(0.72, 0.60, 0.28),
        runner_skin=(0.90, 0.78, 0.60),
        runner_accent=(0.95, 0.90, 0.22),
        villain_name="Captain Hook",
        villain_gown=(0.60, 0.08, 0.08),
        villain_accent=(0.95, 0.82, 0.22),
        villain_hair=(0.52, 0.42, 0.72),
        villain_skin=(0.80, 0.68, 0.58),
        collectible_name="Pixie Dust",
        collectible_color_primary=(1.00, 0.95, 0.60),
        collectible_color_secondary=(0.95, 0.88, 0.40),
        collectible_color_highlight=(1.00, 1.00, 0.90),
        obstacle_primary=(0.42, 0.28, 0.12),
        obstacle_secondary=(0.55, 0.38, 0.18),
        obstacle_stripe=(0.95, 0.82, 0.22),
        hud_accent=(80, 200, 120),
        ability_name="Pixie Dust Flight",
        ability_duration=7.0,
        ability_type="pixie_flight",
        ability_color=(120, 255, 140),
    ),

    # -------------------------------------------------------------------------
    # World 7 — FROZEN
    # -------------------------------------------------------------------------
    WorldConfig(
        index=7,
        name="Frozen",
        subtitle="Sprint Through the Ice Kingdom!",
        sky_color=(0.72, 0.88, 0.98, 1.0),
        ground_color=(0.82, 0.90, 0.95),
        road_color_side=(0.65, 0.78, 0.88),
        road_color_center=(0.72, 0.84, 0.92),
        sidewalk_color=(0.85, 0.92, 0.96),
        fog_color=(0.72, 0.88, 0.98),
        light_pos=(5.0, 40.0, 20.0),
        light_color=(0.85, 0.92, 1.00),
        fog_start=60.0,
        fog_end=190.0,
        scenery_style="snow",
        foliage_tint=(0.70, 0.84, 0.92),
        runner_name="Anna",
        runner_jacket=(0.18, 0.42, 0.72),
        runner_pants=(0.55, 0.38, 0.22),
        runner_shoes=(0.32, 0.22, 0.14),
        runner_hair=(0.68, 0.48, 0.22),
        runner_skin=(0.95, 0.84, 0.74),
        runner_accent=(0.80, 0.22, 0.28),
        villain_name="Hans",
        villain_gown=(0.85, 0.88, 0.92),
        villain_accent=(0.15, 0.25, 0.45),
        villain_hair=(0.72, 0.58, 0.28),
        villain_skin=(0.88, 0.78, 0.68),
        collectible_name="Snowflake",
        collectible_color_primary=(0.88, 0.95, 1.00),
        collectible_color_secondary=(0.65, 0.82, 0.95),
        collectible_color_highlight=(1.00, 1.00, 1.00),
        obstacle_primary=(0.65, 0.78, 0.90),
        obstacle_secondary=(0.80, 0.90, 0.95),
        obstacle_stripe=(0.88, 0.95, 1.00),
        hud_accent=(140, 200, 240),
        ability_name="Frost Barrier Aegis",
        ability_duration=14.0,
        ability_type="frost_barrier",
        ability_color=(160, 225, 255),
    ),
]


def get_world(index: int) -> WorldConfig:
    """Returns the WorldConfig at the given index (wraps around)."""
    return WORLDS[index % len(WORLDS)]


def get_all_worlds() -> List[WorldConfig]:
    """Returns the complete ordered list of all world configurations."""
    return WORLDS
