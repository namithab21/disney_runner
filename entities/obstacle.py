"""
obstacle.py - 3D Obstacle Entities and Procedural Geometry.
Provides three distinct obstacle types:
- GroundBarrier: Low hurdle that player must jump over.
- OverheadBarrier: Elevated clearance structure that player must slide under.
- FullBlocker: High obstruction spanning the entire lane that player must dodge.

World-aware: Obstacle materials, colors and hazard accents adapt to the active
Disney world configuration while preserving strict collision bounding dimensions.
"""

from enum import Enum
from typing import Tuple, Optional
import numpy as np
import pyrr
from config import settings
from engine.mesh import Mesh, VertexAttribute
from engine.shader import ShaderProgram
from engine.camera import Camera
from engine.renderer import Renderer
from entities.scenery import add_box, add_quad


class ObstacleType(str, Enum):
    GROUND_BARRIER = "ground_barrier"
    OVERHEAD_BARRIER = "overhead_barrier"
    FULL_BLOCKER = "full_blocker"


# Default World 0 (Cinderella) colors
_DEFAULT_OBS_PRIMARY = (0.42, 0.26, 0.15)
_DEFAULT_OBS_SECONDARY = (0.65, 0.42, 0.24)
_DEFAULT_OBS_STRIPE = (0.96, 0.86, 0.20)


def create_ground_barrier_mesh(
    primary: Tuple[float, float, float] = _DEFAULT_OBS_PRIMARY,
    secondary: Tuple[float, float, float] = _DEFAULT_OBS_SECONDARY,
    stripe: Tuple[float, float, float] = _DEFAULT_OBS_STRIPE,
    style: str = "kingdom"
) -> Mesh:
    """
    Builds a 3D hurdle barrier.
    Height <= 0.65 units. Player jumps over it to clear.
    Style adapts geometry for each of the 8 Disney worlds.
    """
    vertices: list[float] = []

    wood_dark = list(primary)
    wood_plank = list(secondary)
    metal_iron = [c * 0.7 for c in primary]
    stripe_accent = list(stripe)
    stripe_dark = [0.15, 0.15, 0.18]

    if style == "forest":  # Snow White: Fallen enchanted birch log & thorn roots
        # Main mossy birch trunk
        add_box(vertices, [-0.90, 0.0, -0.22], [0.90, 0.48, 0.22], wood_plank)
        # Bark end rings
        add_box(vertices, [-0.92, 0.05, -0.18], [-0.88, 0.45, 0.18], wood_dark)
        add_box(vertices, [ 0.88, 0.05, -0.18], [ 0.92, 0.45, 0.18], wood_dark)
        # Moss & fungus caps on log (height <= 0.62)
        add_box(vertices, [-0.45, 0.48, -0.15], [-0.15, 0.58, 0.15], stripe_accent)
        add_box(vertices, [ 0.20, 0.48, -0.12], [ 0.50, 0.56, 0.12], [0.22, 0.55, 0.20])
        # Root anchors
        add_box(vertices, [-0.85, 0.0, -0.35], [-0.60, 0.18, 0.35], wood_dark)
        add_box(vertices, [ 0.60, 0.0, -0.35], [ 0.85, 0.18, 0.35], wood_dark)

    elif style == "desert":  # Aladdin: Rolling brass urns and market sacks
        # Large brass central urn
        add_box(vertices, [-0.30, 0.0, -0.25], [0.30, 0.55, 0.25], stripe_accent)
        add_box(vertices, [-0.22, 0.55, -0.18], [0.22, 0.63, 0.18], metal_iron)
        # Flanking spiced grain sacks
        add_box(vertices, [-0.88, 0.0, -0.28], [-0.28, 0.42, 0.28], wood_plank)
        add_box(vertices, [ 0.28, 0.0, -0.28], [ 0.88, 0.42, 0.28], wood_dark)
        # Sack rope ties
        add_box(vertices, [-0.70, 0.32, -0.29], [-0.45, 0.36, 0.29], [0.95, 0.90, 0.60])
        add_box(vertices, [ 0.45, 0.32, -0.29], [ 0.70, 0.36, 0.29], [0.95, 0.90, 0.60])

    elif style == "lanterns":  # Tangled: Festival flower crates & beer barrels
        # Wooden festival flower box
        add_box(vertices, [-0.85, 0.0, -0.20], [0.85, 0.42, 0.20], wood_dark)
        # Floral garland on top (Y: 0.42 to 0.62)
        add_box(vertices, [-0.80, 0.42, -0.15], [0.80, 0.55, 0.15], wood_plank)
        add_box(vertices, [-0.70, 0.55, -0.10], [-0.30, 0.63, 0.10], stripe_accent)
        add_box(vertices, [ 0.30, 0.55, -0.10], [ 0.70, 0.63, 0.10], stripe_accent)
        # Iron corner corner-bands
        add_box(vertices, [-0.88, 0.0, -0.22], [-0.78, 0.44, 0.22], metal_iron)
        add_box(vertices, [ 0.78, 0.0, -0.22], [ 0.88, 0.44, 0.22], metal_iron)

    elif style == "savanna":  # Lion King: Weathered fallen acacia branch hurdle
        add_box(vertices, [-0.90, 0.0, -0.18], [0.90, 0.44, 0.18], wood_dark)
        # Broken branch forks
        add_box(vertices, [-0.60, 0.44, -0.10], [-0.35, 0.64, 0.10], wood_plank)
        add_box(vertices, [ 0.25, 0.44, -0.10], [ 0.55, 0.62, 0.10], wood_plank)
        # Dry savanna grass tufts at base
        add_box(vertices, [-0.85, 0.0, -0.30], [-0.55, 0.25, 0.30], stripe_accent)
        add_box(vertices, [ 0.55, 0.0, -0.30], [ 0.85, 0.25, 0.30], stripe_accent)

    elif style == "underwater":  # Little Mermaid: Coral urchin & brain coral hurdle
        # Brain coral central dome
        add_box(vertices, [-0.45, 0.0, -0.30], [0.45, 0.52, 0.30], wood_plank)
        add_box(vertices, [-0.35, 0.52, -0.22], [0.35, 0.62, 0.22], stripe_accent)
        # Sea-urchin clusters flanking
        add_box(vertices, [-0.88, 0.0, -0.25], [-0.42, 0.44, 0.25], wood_dark)
        add_box(vertices, [ 0.42, 0.0, -0.25], [ 0.88, 0.44, 0.25], wood_dark)
        # Coral spine highlights
        add_box(vertices, [-0.75, 0.44, -0.08], [-0.55, 0.64, 0.08], stripe_accent)
        add_box(vertices, [ 0.55, 0.44, -0.08], [ 0.75, 0.64, 0.08], stripe_accent)

    elif style == "neverland":  # Peter Pan: Pirate grog barrels & coiled ropes
        # Twin wooden grog barrels
        add_box(vertices, [-0.78, 0.0, -0.24], [-0.12, 0.58, 0.24], wood_dark)
        add_box(vertices, [ 0.12, 0.0, -0.24], [ 0.78, 0.58, 0.24], wood_dark)
        # Barrel brass hoops
        add_box(vertices, [-0.80, 0.12, -0.25], [-0.10, 0.20, 0.25], stripe_accent)
        add_box(vertices, [-0.80, 0.40, -0.25], [-0.10, 0.48, 0.25], stripe_accent)
        add_box(vertices, [ 0.10, 0.12, -0.25], [ 0.80, 0.20, 0.25], stripe_accent)
        add_box(vertices, [ 0.10, 0.40, -0.25], [ 0.80, 0.48, 0.25], stripe_accent)
        # Coiled ship rope connecting them
        add_box(vertices, [-0.20, 0.0, -0.20], [0.20, 0.26, 0.20], wood_plank)

    elif style == "snow":  # Frozen: Jagged crystalline ice ridge hurdle
        # Jagged ice ridge teeth
        add_box(vertices, [-0.88, 0.0, -0.20], [-0.50, 0.64, 0.20], wood_plank)
        add_box(vertices, [-0.52, 0.0, -0.18], [-0.12, 0.52, 0.18], wood_dark)
        add_box(vertices, [-0.15, 0.0, -0.22], [ 0.25, 0.62, 0.22], stripe_accent)
        add_box(vertices, [ 0.22, 0.0, -0.18], [ 0.58, 0.50, 0.18], wood_dark)
        add_box(vertices, [ 0.55, 0.0, -0.20], [ 0.88, 0.63, 0.20], wood_plank)
        # Glacial snow base shelf
        add_box(vertices, [-0.92, 0.0, -0.32], [0.92, 0.18, 0.32], [0.90, 0.95, 1.0])

    else:  # Default Cinderella: Hedge hurdle with royal roses
        # Sturdy Side Posts (X = -0.80 and +0.80)
        add_box(vertices, [-0.88, 0.0, -0.15], [-0.72, 0.65, 0.15], wood_dark)
        add_box(vertices, [ 0.72, 0.0, -0.15], [ 0.88, 0.65, 0.15], wood_dark)
        # Base Feet / Support Triangles
        add_box(vertices, [-0.92, 0.0, -0.35], [-0.68, 0.12, 0.35], metal_iron)
        add_box(vertices, [ 0.68, 0.0, -0.35], [ 0.92, 0.12, 0.35], metal_iron)
        # Horizontal Barrier Planks (Y: 0.15 to 0.62)
        add_box(vertices, [-0.75, 0.18, -0.08], [0.75, 0.38, 0.08], wood_plank)
        add_box(vertices, [-0.75, 0.42, -0.08], [0.75, 0.62, 0.08], wood_plank)
        # Alternating Hazard Stripes on Upper Plank
        num_stripes = 6
        w_step = 1.40 / num_stripes
        for i in range(num_stripes):
            c = stripe_accent if i % 2 == 0 else stripe_dark
            x_start = -0.70 + i * w_step
            x_end = x_start + w_step
            add_quad(
                vertices,
                [x_start, 0.43, -0.085],
                [x_end,   0.43, -0.085],
                [x_end,   0.61, -0.085],
                [x_start, 0.61, -0.085],
                c,
                [0.0, 0.0, -1.0]
            )

    arr = np.array(vertices, dtype=np.float32)
    attrs = [
        VertexAttribute(location=0, size=3),
        VertexAttribute(location=1, size=3),
        VertexAttribute(location=2, size=3)
    ]
    return Mesh(vertices=arr, attributes=attrs)


def create_overhead_barrier_mesh(
    primary: Tuple[float, float, float] = _DEFAULT_OBS_PRIMARY,
    secondary: Tuple[float, float, float] = _DEFAULT_OBS_SECONDARY,
    stripe: Tuple[float, float, float] = _DEFAULT_OBS_STRIPE,
    style: str = "kingdom"
) -> Mesh:
    """
    Builds an elevated overhead barrier archway.
    Ground clearance = 1.02 units. Barrier beam sits from Y = 1.05 to 2.30.
    Player slides underneath (sliding height = 0.85m) to clear.
    Style adapts geometry for each of the 8 Disney worlds.
    """
    vertices: list[float] = []

    frame_metal = [c * 1.1 for c in primary]
    bar_primary = list(secondary)
    bar_accent = list(stripe)
    stripe_dark = [0.15, 0.15, 0.18]
    cw = 0.10

    # Two Tall Vertical Columns (X = -1.05 and +1.05, Y: 0.0 to 2.45)
    add_box(vertices, [-1.05 - cw, 0.0, -0.15], [-1.05 + cw, 2.45, 0.15], frame_metal)
    add_box(vertices, [ 1.05 - cw, 0.0, -0.15], [ 1.05 + cw, 2.45, 0.15], frame_metal)

    # Foundation blocks
    foundation_color = [c * 0.8 for c in primary]
    add_box(vertices, [-1.22, 0.0, -0.25], [-0.88, 0.25, 0.25], foundation_color)
    add_box(vertices, [ 0.88, 0.0, -0.25], [ 1.22, 0.25, 0.25], foundation_color)

    # Top Heavy Support Beam (Y: 2.15 to 2.45)
    add_box(vertices, [-1.15, 2.15, -0.18], [1.15, 2.45, 0.18], frame_metal)

    if style == "forest":  # Snow White: Low-hanging enchanted tree branches & vines
        # Branch canopy (Y: 1.06 to 2.15)
        add_box(vertices, [-0.98, 1.06, -0.20], [0.98, 1.95, 0.20], bar_primary)
        # Hanging twisted liana vines (bottom clearance = 1.05)
        add_box(vertices, [-0.60, 1.05, -0.05], [-0.50, 1.70, 0.05], bar_accent)
        add_box(vertices, [ 0.40, 1.05, -0.05], [ 0.50, 1.70, 0.05], bar_accent)

    elif style == "desert":  # Aladdin: Bazaar canvas market awnings
        # Hanging striped canvas awning (Y: 1.08 to 2.12)
        add_box(vertices, [-0.98, 1.08, -0.28], [0.98, 2.10, 0.28], bar_primary)
        # Tassels along rim
        add_box(vertices, [-0.90, 1.05, -0.29], [0.90, 1.15, 0.29], bar_accent)

    elif style == "lanterns":  # Tangled: Hanging festival lantern cables
        add_box(vertices, [-0.98, 1.12, -0.12], [0.98, 2.05, 0.12], bar_primary)
        # Hanging yellow festival lanterns (clearance = 1.06)
        add_box(vertices, [-0.65, 1.06, -0.08], [-0.45, 1.35, 0.08], bar_accent)
        add_box(vertices, [ 0.45, 1.06, -0.08], [ 0.65, 1.35, 0.08], bar_accent)

    elif style == "savanna":  # Lion King: Low savanna rock arch formation
        add_box(vertices, [-0.98, 1.06, -0.25], [0.98, 2.10, 0.25], bar_primary)
        # Weathered rock shelves
        add_box(vertices, [-0.75, 1.08, -0.28], [-0.25, 1.45, 0.28], bar_accent)
        add_box(vertices, [ 0.25, 1.08, -0.28], [ 0.75, 1.45, 0.28], bar_accent)

    elif style == "underwater":  # Little Mermaid: Branching staghorn coral arch
        add_box(vertices, [-0.98, 1.08, -0.18], [0.98, 2.05, 0.18], bar_primary)
        # Spreading coral branches
        add_box(vertices, [-0.80, 1.05, -0.10], [-0.55, 1.60, 0.10], bar_accent)
        add_box(vertices, [ 0.55, 1.05, -0.10], [ 0.80, 1.60, 0.10], bar_accent)

    elif style == "neverland":  # Peter Pan: Pirate ship yardarm mast & rigging ropes
        add_box(vertices, [-0.98, 1.10, -0.15], [0.98, 1.95, 0.15], bar_primary)
        # Hanging ship rigging lines (clearance = 1.05)
        add_box(vertices, [-0.70, 1.05, -0.05], [-0.60, 1.80, 0.05], bar_accent)
        add_box(vertices, [ 0.60, 1.05, -0.05], [ 0.70, 1.80, 0.05], bar_accent)

    elif style == "snow":  # Frozen: Hanging icicle stalactite formation
        add_box(vertices, [-0.98, 1.25, -0.18], [0.98, 2.10, 0.18], bar_primary)
        # Pointed icicles hanging down (clearance = 1.05)
        for ic_x in [-0.75, -0.45, -0.15, 0.15, 0.45, 0.75]:
            add_box(vertices, [ic_x - 0.06, 1.05, -0.06], [ic_x + 0.06, 1.35, 0.06], bar_accent)

    else:  # Default Cinderella: Palace archway with blue tapestries
        # Lower Hanging Overhead Hazard Barrier (Y: 1.05 to 2.10)
        add_box(vertices, [-0.98, 1.05, -0.12], [0.98, 2.05, 0.12], bar_primary)
        num_chevrons = 8
        c_step = 1.90 / num_chevrons
        for i in range(num_chevrons):
            c = bar_accent if i % 2 == 0 else stripe_dark
            x0 = -0.95 + i * c_step
            x1 = x0 + c_step
            add_quad(
                vertices,
                [x0, 1.08, -0.125],
                [x1, 1.08, -0.125],
                [x1, 2.02, -0.125],
                [x0, 2.02, -0.125],
                c,
                [0.0, 0.0, -1.0]
            )
        # Warning Clearance Hanging Markers
        add_box(vertices, [-0.60, 0.95, -0.05], [-0.40, 1.05, 0.05], bar_accent)
        add_box(vertices, [ 0.40, 0.95, -0.05], [ 0.60, 1.05, 0.05], bar_accent)

    arr = np.array(vertices, dtype=np.float32)
    attrs = [
        VertexAttribute(location=0, size=3),
        VertexAttribute(location=1, size=3),
        VertexAttribute(location=2, size=3)
    ]
    return Mesh(vertices=arr, attributes=attrs)


def create_full_blocker_mesh(
    primary: Tuple[float, float, float] = _DEFAULT_OBS_PRIMARY,
    secondary: Tuple[float, float, float] = _DEFAULT_OBS_SECONDARY,
    stripe: Tuple[float, float, float] = _DEFAULT_OBS_STRIPE,
    style: str = "kingdom"
) -> Mesh:
    """
    Builds a large stacked obstacle completely blocking an entire lane.
    Height = 2.4 units, spanning ground to top across full lane width.
    Player must switch lanes to avoid.
    Style adapts geometry for each of the 8 Disney worlds.
    """
    vertices: list[float] = []

    crate_wood1 = list(primary)
    crate_wood2 = list(secondary)
    crate_band = [c * 0.6 for c in primary]
    placard_color = list(stripe)
    danger_red = [0.88, 0.22, 0.22]

    if style == "forest":  # Snow White: Giant enchanted mushroom cluster blocker
        # Main thick mushroom stem
        add_box(vertices, [-0.55, 0.0, -0.40], [0.55, 1.40, 0.40], [0.88, 0.85, 0.78])
        # Gigantic red polka-dot toadstool cap
        add_box(vertices, [-0.95, 1.40, -0.45], [0.95, 2.38, 0.45], [0.85, 0.12, 0.12])
        # White spots on mushroom cap
        add_box(vertices, [-0.70, 1.80, -0.46], [-0.40, 2.10, 0.46], [1.0, 1.0, 1.0])
        add_box(vertices, [ 0.40, 1.80, -0.46], [ 0.70, 2.10, 0.46], [1.0, 1.0, 1.0])
        # Under-cap gills
        add_box(vertices, [-0.90, 1.30, -0.42], [0.90, 1.40, 0.42], [0.92, 0.90, 0.80])

    elif style == "desert":  # Aladdin: Merchant fruit & carpet carts
        # Wooden market stall cart body
        add_box(vertices, [-0.95, 0.35, -0.42], [0.95, 1.45, 0.42], crate_wood1)
        # Giant wooden spoke wheels
        add_box(vertices, [-0.96, 0.0, -0.35], [-0.94, 0.75, 0.35], crate_band)
        add_box(vertices, [ 0.94, 0.0, -0.35], [ 0.96, 0.75, 0.35], crate_band)
        # Stacked rolled Persian carpets & melon crates on top
        add_box(vertices, [-0.85, 1.45, -0.38], [0.85, 2.35, 0.38], crate_wood2)
        add_box(vertices, [-0.75, 1.65, -0.40], [0.75, 1.85, 0.40], placard_color)

    elif style == "lanterns":  # Tangled: Royal guard barricades with sun crest
        add_box(vertices, [-0.95, 0.0, -0.35], [0.95, 1.85, 0.35], crate_wood1)
        add_box(vertices, [-0.95, 1.85, -0.25], [0.95, 2.38, 0.25], crate_wood2)
        # Royal sun crest on front
        add_box(vertices, [-0.40, 0.75, -0.36], [0.40, 1.55, 0.36], placard_color)

    elif style == "savanna":  # Lion King: Dense thorn thicket bush
        # Layered dense briar bush (full width & height)
        add_box(vertices, [-0.95, 0.0, -0.42], [0.95, 1.35, 0.42], crate_wood1)
        add_box(vertices, [-0.90, 1.25, -0.38], [0.90, 2.38, 0.38], crate_wood2)
        # Jagged dry thorn accents
        add_box(vertices, [-0.85, 0.50, -0.44], [-0.55, 1.90, 0.44], crate_band)
        add_box(vertices, [ 0.55, 0.50, -0.44], [ 0.85, 1.90, 0.44], crate_band)

    elif style == "underwater":  # Little Mermaid: Sunken ship cargo crates & anchor
        # Main barnacle-encrusted shipping crates
        add_box(vertices, [-0.95, 0.0, -0.44], [0.95, 1.30, 0.44], crate_wood1)
        add_box(vertices, [-0.80, 1.30, -0.38], [0.80, 2.35, 0.38], crate_wood2)
        # Heavy iron anchor chains
        add_box(vertices, [-0.30, 0.40, -0.46], [0.30, 1.90, 0.46], crate_band)

    elif style == "neverland":  # Peter Pan: Treasure chests & iron cannon barricade
        # Stacked pirate chests
        add_box(vertices, [-0.95, 0.0, -0.42], [0.95, 1.20, 0.42], crate_wood1)
        add_box(vertices, [-0.85, 1.20, -0.38], [0.85, 2.10, 0.38], crate_wood2)
        # Heavy cast-iron pirate cannon on top
        add_box(vertices, [-0.35, 1.80, -0.45], [0.35, 2.38, 0.45], crate_band)

    elif style == "snow":  # Frozen: Towering glacier snowbank wall
        # Glacial blue ice block base
        add_box(vertices, [-0.95, 0.0, -0.45], [0.95, 1.50, 0.45], crate_wood1)
        # Snow drift crest spanning to top (Y=2.40)
        add_box(vertices, [-0.95, 1.45, -0.42], [0.95, 2.40, 0.42], [0.92, 0.96, 1.0])
        # Frost crystal fissures
        add_box(vertices, [-0.60, 0.30, -0.46], [-0.30, 1.90, 0.46], placard_color)
        add_box(vertices, [ 0.30, 0.30, -0.46], [ 0.60, 1.90, 0.46], placard_color)

    else:  # Default Cinderella: Royal carriage luggage trunks
        # Bottom Base Crate (spanning entire lane width X: -0.95 to 0.95, Y: 0.0 to 1.15)
        add_box(vertices, [-0.95, 0.0, -0.45], [0.95, 1.15, 0.45], crate_wood1)
        # Metal Reinforcement Bands on Bottom Crate
        add_box(vertices, [-0.96, 0.0, -0.46], [-0.85, 1.16, 0.46], crate_band)
        add_box(vertices, [ 0.85, 0.0, -0.46], [ 0.96, 1.16, 0.46], crate_band)
        add_box(vertices, [-0.96, 0.50, -0.46], [ 0.96, 0.65, 0.46], crate_band)
        # Upper Left Crate (Y: 1.15 to 2.35, X: -0.92 to 0.05)
        add_box(vertices, [-0.92, 1.15, -0.42], [0.05, 2.35, 0.42], crate_wood2)
        add_box(vertices, [-0.93, 1.15, -0.43], [-0.80, 2.36, 0.43], crate_band)
        add_box(vertices, [-0.08, 1.15, -0.43], [ 0.06, 2.36, 0.43], crate_band)
        # Upper Right Crate (Y: 1.15 to 2.10, X: 0.08 to 0.92)
        add_box(vertices, [0.08, 1.15, -0.38], [0.92, 2.10, 0.38], crate_wood1)
        # Danger Placard on Front Face (-Z facing runner)
        add_quad(
            vertices,
            [-0.40, 0.35, -0.455],
            [ 0.40, 0.35, -0.455],
            [ 0.40, 0.80, -0.455],
            [-0.40, 0.80, -0.455],
            placard_color,
            [0.0, 0.0, -1.0]
        )
        add_quad(
            vertices,
            [-0.35, 0.40, -0.458],
            [ 0.35, 0.40, -0.458],
            [ 0.35, 0.75, -0.458],
            [-0.35, 0.75, -0.458],
            danger_red,
            [0.0, 0.0, -1.0]
        )

    arr = np.array(vertices, dtype=np.float32)
    attrs = [
        VertexAttribute(location=0, size=3),
        VertexAttribute(location=1, size=3),
        VertexAttribute(location=2, size=3)
    ]
    return Mesh(vertices=arr, attributes=attrs)


class ObstacleMeshCache:
    """Singleton cache maintaining reusable GPU meshes for each obstacle type and world theme."""
    _instance = None

    def __init__(self):
        self.ground_mesh: Optional[Mesh] = None
        self.overhead_mesh: Optional[Mesh] = None
        self.blocker_mesh: Optional[Mesh] = None
        self.current_theme: Optional[Tuple] = None

    @classmethod
    def get(cls) -> "ObstacleMeshCache":
        if cls._instance is None:
            cls._instance = ObstacleMeshCache()
            cls._instance.init_meshes()
        return cls._instance

    def init_meshes(
        self,
        primary: Tuple[float, float, float] = _DEFAULT_OBS_PRIMARY,
        secondary: Tuple[float, float, float] = _DEFAULT_OBS_SECONDARY,
        stripe: Tuple[float, float, float] = _DEFAULT_OBS_STRIPE,
        style: str = "kingdom"
    ) -> None:
        if self.ground_mesh is None:
            self.ground_mesh = create_ground_barrier_mesh(primary, secondary, stripe, style=style)
        if self.overhead_mesh is None:
            self.overhead_mesh = create_overhead_barrier_mesh(primary, secondary, stripe, style=style)
        if self.blocker_mesh is None:
            self.blocker_mesh = create_full_blocker_mesh(primary, secondary, stripe, style=style)
        self.current_theme = (primary, secondary, stripe, style)

    def refresh_for_world(self, world_config) -> None:
        """Re-skins obstacle meshes to match the active Disney world theme and scenery style."""
        style = getattr(world_config, "scenery_style", "kingdom")
        theme = (world_config.obstacle_primary, world_config.obstacle_secondary, world_config.obstacle_stripe, style)
        if self.current_theme == theme:
            return

        if self.ground_mesh:
            self.ground_mesh.delete()
        if self.overhead_mesh:
            self.overhead_mesh.delete()
        if self.blocker_mesh:
            self.blocker_mesh.delete()

        self.ground_mesh = create_ground_barrier_mesh(world_config.obstacle_primary, world_config.obstacle_secondary, world_config.obstacle_stripe, style=style)
        self.overhead_mesh = create_overhead_barrier_mesh(world_config.obstacle_primary, world_config.obstacle_secondary, world_config.obstacle_stripe, style=style)
        self.blocker_mesh = create_full_blocker_mesh(world_config.obstacle_primary, world_config.obstacle_secondary, world_config.obstacle_stripe, style=style)
        self.current_theme = theme
        print(f"[OBSTACLES] Re-skinned with {style} hazards for world: {world_config.name}")

    def get_mesh(self, obstacle_type: ObstacleType) -> Mesh:
        if obstacle_type == ObstacleType.GROUND_BARRIER:
            return self.ground_mesh
        elif obstacle_type == ObstacleType.OVERHEAD_BARRIER:
            return self.overhead_mesh
        elif obstacle_type == ObstacleType.FULL_BLOCKER:
            return self.blocker_mesh
        raise ValueError(f"Unknown obstacle type: {obstacle_type}")

    def delete(self) -> None:
        if self.ground_mesh:
            self.ground_mesh.delete()
            self.ground_mesh = None
        if self.overhead_mesh:
            self.overhead_mesh.delete()
            self.overhead_mesh = None
        if self.blocker_mesh:
            self.blocker_mesh.delete()
            self.blocker_mesh = None
        self.current_theme = None
        ObstacleMeshCache._instance = None


class Obstacle:
    """3D Obstacle base entity for lane hazards."""

    def __init__(self, obstacle_type: ObstacleType, lane: int, z: float):
        self.obstacle_type = obstacle_type
        self.lane = max(-1, min(1, lane))
        self.x = float(self.lane * settings.LANE_WIDTH)
        self.z = float(z)

    def update(self, speed: float, delta_time: float) -> None:
        """Moves obstacle towards the camera along +Z."""
        self.z += speed * delta_time

    def is_past_player(self, threshold_z: float = 15.0) -> bool:
        """Returns True if obstacle has moved completely behind player and camera."""
        return self.z > threshold_z

    def get_bounding_box(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculates axis-aligned bounding box (min_corner, max_corner) in world space.
        Includes calibrated forgiveness margins to ensure fair, rewarding gameplay.
        """
        if self.obstacle_type == ObstacleType.GROUND_BARRIER:
            hw = 0.85
            hd = 0.20
            min_pt = np.array([self.x - hw, 0.0, self.z - hd], dtype=np.float32)
            max_pt = np.array([self.x + hw, 0.65, self.z + hd], dtype=np.float32)
            return min_pt, max_pt

        elif self.obstacle_type == ObstacleType.OVERHEAD_BARRIER:
            hw = 0.85
            hd = 0.22
            min_pt = np.array([self.x - hw, 1.02, self.z - hd], dtype=np.float32)
            max_pt = np.array([self.x + hw, 2.30, self.z + hd], dtype=np.float32)
            return min_pt, max_pt

        elif self.obstacle_type == ObstacleType.FULL_BLOCKER:
            hw = 0.90
            hd = 0.40
            min_pt = np.array([self.x - hw, 0.0, self.z - hd], dtype=np.float32)
            max_pt = np.array([self.x + hw, 2.40, self.z + hd], dtype=np.float32)
            return min_pt, max_pt

        return (
            np.array([self.x - 0.5, 0.0, self.z - 0.5], dtype=np.float32),
            np.array([self.x + 0.5, 2.0, self.z + 0.5], dtype=np.float32)
        )

    def get_model_matrix(self) -> pyrr.Matrix44:
        """Computes world translation matrix for this obstacle."""
        return pyrr.Matrix44.from_translation([self.x, 0.0, self.z])

    def render(self, renderer: Renderer, shader: ShaderProgram, camera: Camera) -> None:
        """Renders the obstacle mesh using the current cached themed mesh."""
        mesh = ObstacleMeshCache.get().get_mesh(self.obstacle_type)
        if mesh:
            renderer.render(mesh, shader, self.get_model_matrix(), camera)
