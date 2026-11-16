"""
collectible.py - World-Aware 3D Collectible Entity and Procedural Mesh.
Supports eight distinct collectible appearances driven by WorldConfig:
  Cinderella: Glass Slipper  | Snow White: Magic Apple
  Aladdin:    Magic Lamp     | Tangled:    Sun Symbol
  Lion King:  Lion Token     | Little Mermaid: Seashell
  Peter Pan:  Pixie Dust     | Frozen:     Snowflake
"""

from typing import Tuple, List, Optional
import numpy as np
import pyrr
from config import settings
from engine.mesh import Mesh, VertexAttribute
from engine.shader import ShaderProgram
from engine.camera import Camera
from engine.renderer import Renderer
from entities.scenery import add_box, add_quad


# ---------------------------------------------------------------------------
# Mesh factory helpers
# ---------------------------------------------------------------------------

def _attrs() -> List:
    return [
        VertexAttribute(location=0, size=3),
        VertexAttribute(location=1, size=3),
        VertexAttribute(location=2, size=3),
    ]


def _make_mesh(vertices: list) -> Mesh:
    return Mesh(vertices=np.array(vertices, dtype=np.float32), attributes=_attrs())


# ---------------------------------------------------------------------------
# World collectible mesh creators
# ---------------------------------------------------------------------------

def create_coin_mesh(
    primary=(1.0, 0.88, 0.22),
    secondary=(0.85, 0.65, 0.12),
    highlight=(1.0, 0.98, 0.65),
    num_segments: int = 12,
    radius: float = 0.35,
    thickness: float = 0.08
) -> Mesh:
    """Gold coin disc (default / fallback collectible)."""
    vertices: list = []
    half_t  = thickness / 2.0
    angles  = np.linspace(0, 2 * np.pi, num_segments, endpoint=False)

    for i in range(num_segments):
        a1, a2 = angles[i], angles[(i + 1) % num_segments]
        x1, y1 = radius * np.cos(a1), radius * np.sin(a1)
        x2, y2 = radius * np.cos(a2), radius * np.sin(a2)

        c_front = list(highlight) if i % 3 == 0 else list(primary)
        vertices.extend([0.0, 0.0, half_t,  *c_front, 0.0, 0.0, 1.0,
                         x1,  y1,  half_t,  *c_front, 0.0, 0.0, 1.0,
                         x2,  y2,  half_t,  *c_front, 0.0, 0.0, 1.0])

        c_back = list(secondary) if i % 2 == 0 else list(primary)
        vertices.extend([0.0, 0.0, -half_t, *c_back, 0.0, 0.0, -1.0,
                         x2,  y2,  -half_t, *c_back, 0.0, 0.0, -1.0,
                         x1,  y1,  -half_t, *c_back, 0.0, 0.0, -1.0])

        mid_a = (a1 + a2) / 2.0
        nx, ny = np.cos(mid_a), np.sin(mid_a)
        rim = [0.95, 0.76, 0.18]
        vertices.extend([x1, y1,  half_t, *rim, nx, ny, 0.0,
                         x1, y1, -half_t, *rim, nx, ny, 0.0,
                         x2, y2, -half_t, *rim, nx, ny, 0.0,
                         x1, y1,  half_t, *rim, nx, ny, 0.0,
                         x2, y2, -half_t, *rim, nx, ny, 0.0,
                         x2, y2,  half_t, *rim, nx, ny, 0.0])

    return _make_mesh(vertices)


def create_slipper_mesh(
    primary=(0.68, 0.90, 1.00),
    secondary=(0.42, 0.72, 0.95),
    highlight=(1.0, 1.0, 1.0),
) -> Mesh:
    """Glass Slipper — crystalline heeled shoe shape."""
    vertices: list = []
    p, s, h = list(primary), list(secondary), list(highlight)

    # Sole (flat base)
    add_box(vertices, [-0.28, -0.05, -0.12], [0.28, 0.02, 0.12], s)
    # Toe cap (rounded front)
    add_box(vertices, [-0.24, 0.02, -0.14], [0.24, 0.12, 0.14], p)
    # Vamp / body
    add_box(vertices, [-0.20, 0.02, -0.10], [0.20, 0.22, 0.10], p)
    # Back collar
    add_box(vertices, [-0.18, 0.08, 0.07], [0.18, 0.28, 0.14], h)
    # Heel
    add_box(vertices, [-0.06, -0.26, 0.06], [0.06, 0.02, 0.14], s)
    # Crystal highlight facets
    add_box(vertices, [-0.10, 0.12, -0.14], [0.10, 0.20, -0.11], h)

    return _make_mesh(vertices)


def create_apple_mesh(
    primary=(0.90, 0.12, 0.12),
    secondary=(0.68, 0.08, 0.08),
    highlight=(1.00, 0.70, 0.60),
) -> Mesh:
    """Magic Apple — round red apple with leaf."""
    vertices: list = []
    p, s, h = list(primary), list(secondary), list(highlight)
    green  = [0.22, 0.60, 0.18]
    brown  = [0.42, 0.26, 0.12]

    # Apple body (layered boxes to suggest roundness)
    add_box(vertices, [-0.22, 0.00, -0.22], [0.22, 0.10, 0.22], s)
    add_box(vertices, [-0.28, 0.08, -0.28], [0.28, 0.26, 0.28], p)
    add_box(vertices, [-0.30, 0.22, -0.30], [0.30, 0.38, 0.30], p)
    add_box(vertices, [-0.28, 0.35, -0.28], [0.28, 0.46, 0.28], p)
    add_box(vertices, [-0.22, 0.42, -0.22], [0.22, 0.50, 0.22], s)
    # Highlight cheek
    add_box(vertices, [-0.05, 0.22, -0.31], [0.14, 0.38, -0.26], h)
    # Stem
    add_box(vertices, [-0.025, 0.46, -0.025], [0.025, 0.60, 0.025], brown)
    # Leaf
    add_box(vertices, [0.02, 0.50, -0.08], [0.16, 0.56, 0.00], green)

    return _make_mesh(vertices)


def create_lamp_mesh(
    primary=(0.95, 0.80, 0.22),
    secondary=(0.78, 0.60, 0.12),
    highlight=(1.00, 0.95, 0.65),
) -> Mesh:
    """Magic Lamp — Aladdin-style oil lamp."""
    vertices: list = []
    p, s, h = list(primary), list(secondary), list(highlight)
    dark = [c * 0.60 for c in p]

    # Base
    add_box(vertices, [-0.24, 0.00, -0.14], [0.24, 0.08, 0.14], s)
    # Body (bulbous middle)
    add_box(vertices, [-0.28, 0.06, -0.18], [0.28, 0.24, 0.18], p)
    add_box(vertices, [-0.24, 0.20, -0.16], [0.24, 0.32, 0.16], p)
    add_box(vertices, [-0.18, 0.28, -0.12], [0.18, 0.38, 0.12], s)
    # Neck
    add_box(vertices, [-0.08, 0.34, -0.08], [0.08, 0.46, 0.08], dark)
    # Spout (pointing -Z)
    add_box(vertices, [-0.06, 0.12, -0.28], [0.06, 0.20, -0.14], p)
    add_box(vertices, [-0.04, 0.14, -0.38], [0.04, 0.18, -0.26], s)
    # Handle (loop on +Z side)
    add_box(vertices, [0.24, 0.10, 0.10], [0.32, 0.26, 0.20], p)
    add_box(vertices, [0.24, 0.10, 0.08], [0.32, 0.14, 0.24], p)
    add_box(vertices, [0.24, 0.22, 0.08], [0.32, 0.26, 0.24], p)
    # Highlight band
    add_box(vertices, [-0.29, 0.14, -0.19], [0.29, 0.18, 0.19], h)

    return _make_mesh(vertices)


def create_sun_symbol_mesh(
    primary=(1.00, 0.88, 0.22),
    secondary=(0.95, 0.72, 0.10),
    highlight=(1.00, 1.00, 0.80),
) -> Mesh:
    """Sun Symbol — Rapunzel's corona sun icon."""
    vertices: list = []
    p, s, h = list(primary), list(secondary), list(highlight)

    # Central disc
    num_seg = 10
    radius  = 0.22
    thick   = 0.06
    angles  = np.linspace(0, 2 * np.pi, num_seg, endpoint=False)
    for i in range(num_seg):
        a1, a2 = angles[i], angles[(i + 1) % num_seg]
        x1, y1 = radius * np.cos(a1), radius * np.sin(a1)
        x2, y2 = radius * np.cos(a2), radius * np.sin(a2)
        c = list(h) if i % 2 == 0 else list(p)
        vertices.extend([0.0, 0.0, thick, *c, 0.0, 0.0, 1.0,
                         x1,  y1,  thick, *c, 0.0, 0.0, 1.0,
                         x2,  y2,  thick, *c, 0.0, 0.0, 1.0])

    # 8 triangular rays
    num_rays = 8
    inner_r  = 0.22
    outer_r  = 0.46
    ray_hw   = 0.07
    for i in range(num_rays):
        a = (i / num_rays) * 2.0 * np.pi
        cx = np.cos(a) * ((inner_r + outer_r) / 2.0)
        cy = np.sin(a) * ((inner_r + outer_r) / 2.0)
        perp = a + np.pi / 2.0
        b1 = [np.cos(a) * inner_r + np.cos(perp) * ray_hw,
              np.sin(a) * inner_r + np.sin(perp) * ray_hw, 0.0]
        b2 = [np.cos(a) * inner_r - np.cos(perp) * ray_hw,
              np.sin(a) * inner_r - np.sin(perp) * ray_hw, 0.0]
        tip = [np.cos(a) * outer_r, np.sin(a) * outer_r, 0.0]
        rc = list(p) if i % 2 == 0 else list(s)
        vertices.extend([*b1, *rc, 0.0, 0.0, 1.0,
                         *b2, *rc, 0.0, 0.0, 1.0,
                         *tip, *rc, 0.0, 0.0, 1.0])

    return _make_mesh(vertices)


def create_lion_token_mesh(
    primary=(0.90, 0.72, 0.22),
    secondary=(0.72, 0.52, 0.12),
    highlight=(1.00, 0.90, 0.60),
) -> Mesh:
    """Lion Token — stamped golden medallion with mane ring."""
    vertices: list = []
    p, s, h = list(primary), list(secondary), list(highlight)

    # Main medallion disc
    num_seg = 12
    radius  = 0.32
    for i in range(num_seg):
        a1 = (i / num_seg) * 2.0 * np.pi
        a2 = ((i + 1) / num_seg) * 2.0 * np.pi
        x1, y1 = radius * np.cos(a1), radius * np.sin(a1)
        x2, y2 = radius * np.cos(a2), radius * np.sin(a2)
        c = list(h) if i % 3 == 0 else list(p)
        vertices.extend([0.0, 0.0, 0.05, *c, 0.0, 0.0, 1.0,
                         x1,  y1,  0.05, *c, 0.0, 0.0, 1.0,
                         x2,  y2,  0.05, *c, 0.0, 0.0, 1.0])

    # Mane ring (8 petal-like boxes radiating outward)
    for i in range(8):
        a = (i / 8) * 2.0 * np.pi
        mx = np.cos(a) * 0.38
        my = np.sin(a) * 0.38
        add_box(vertices, [mx - 0.06, my - 0.06, 0.0], [mx + 0.06, my + 0.06, 0.07], s)

    # Face detail (simple 3-box suggestion)
    add_box(vertices, [-0.08, 0.04, 0.05], [0.08, 0.14, 0.09], h)   # Forehead
    add_box(vertices, [-0.06, -0.04, 0.05], [0.06, 0.06, 0.09], p)  # Snout
    add_box(vertices, [-0.04, -0.10, 0.05], [0.04, -0.04, 0.09], s) # Jaw

    return _make_mesh(vertices)


def create_seashell_mesh(
    primary=(0.95, 0.80, 0.70),
    secondary=(0.90, 0.65, 0.55),
    highlight=(1.00, 0.95, 0.90),
) -> Mesh:
    """Seashell — spiral conch-like shell."""
    vertices: list = []
    p, s, h = list(primary), list(secondary), list(highlight)

    # Outer body coils (layered ovals)
    add_box(vertices, [-0.30, -0.05, -0.22], [0.30, 0.10, 0.22], s)
    add_box(vertices, [-0.28, 0.08,  -0.20], [0.28, 0.22, 0.20], p)
    add_box(vertices, [-0.24, 0.18,  -0.16], [0.24, 0.30, 0.16], p)
    add_box(vertices, [-0.18, 0.26,  -0.12], [0.18, 0.36, 0.12], h)
    add_box(vertices, [-0.12, 0.32,  -0.08], [0.12, 0.44, 0.08], s)
    add_box(vertices, [-0.06, 0.40,  -0.04], [0.06, 0.52, 0.04], p)

    # Lip / opening flare (front facing -Z)
    add_box(vertices, [-0.32, 0.00, -0.24], [0.32, 0.12, -0.20], h)
    # Ridge lines along body
    for i, y0 in enumerate([0.08, 0.16, 0.24]):
        c = s if i % 2 == 0 else h
        add_box(vertices, [-0.26 + i*0.03, y0, -0.21 + i*0.02],
                [0.26 - i*0.03, y0 + 0.025, 0.21 - i*0.02], c)

    return _make_mesh(vertices)


def create_pixie_dust_mesh(
    primary=(1.00, 0.95, 0.60),
    secondary=(0.95, 0.88, 0.40),
    highlight=(1.00, 1.00, 0.90),
) -> Mesh:
    """Pixie Dust — sparkling star cluster."""
    vertices: list = []
    p, s, h = list(primary), list(secondary), list(highlight)

    # Central star
    num_points = 5
    inner_r = 0.12
    outer_r = 0.30
    thick   = 0.06
    for i in range(num_points * 2):
        a1 = (i / (num_points * 2)) * 2.0 * np.pi
        a2 = ((i + 1) / (num_points * 2)) * 2.0 * np.pi
        r1 = outer_r if i % 2 == 0 else inner_r
        r2 = inner_r if i % 2 == 0 else outer_r
        x1, y1 = r1 * np.cos(a1), r1 * np.sin(a1)
        x2, y2 = r2 * np.cos(a2), r2 * np.sin(a2)
        c = list(h) if i % 2 == 0 else list(p)
        vertices.extend([0.0, 0.0, thick, *c, 0.0, 0.0, 1.0,
                         x1,  y1,  thick, *c, 0.0, 0.0, 1.0,
                         x2,  y2,  thick, *c, 0.0, 0.0, 1.0])

    # Orbiting sparkle dots (small boxes)
    for i in range(6):
        a = (i / 6) * 2.0 * np.pi
        sx = np.cos(a) * 0.42
        sy = np.sin(a) * 0.42
        sc = list(s) if i % 2 == 0 else list(h)
        add_box(vertices, [sx - 0.04, sy - 0.04, 0.0], [sx + 0.04, sy + 0.04, 0.07], sc)

    return _make_mesh(vertices)


def create_snowflake_mesh(
    primary=(0.88, 0.95, 1.00),
    secondary=(0.65, 0.82, 0.95),
    highlight=(1.00, 1.00, 1.00),
) -> Mesh:
    """Snowflake — six-arm crystalline star."""
    vertices: list = []
    p, s, h = list(primary), list(secondary), list(highlight)
    thick = 0.04

    # 6 arms
    for i in range(6):
        a = (i / 6) * 2.0 * np.pi
        ex = np.cos(a) * 0.38
        ey = np.sin(a) * 0.38
        perp = a + np.pi / 2.0
        hw = 0.055
        b1 = [np.cos(perp) * hw, np.sin(perp) * hw, thick]
        b2 = [-np.cos(perp) * hw, -np.sin(perp) * hw, thick]
        tip = [ex, ey, thick]
        c = list(h) if i % 2 == 0 else list(p)
        vertices.extend([*b1, *c, 0.0, 0.0, 1.0,
                         *b2, *c, 0.0, 0.0, 1.0,
                         *tip, *c, 0.0, 0.0, 1.0])

        # Side branches (two smaller arms per main arm)
        for side in [-1, 1]:
            ba_angle = a + side * np.pi / 4.0
            brx = np.cos(a) * 0.18 + np.cos(ba_angle) * 0.14
            bry = np.sin(a) * 0.18 + np.sin(ba_angle) * 0.14
            origin = [np.cos(a) * 0.18, np.sin(a) * 0.18, thick]
            branch_tip = [brx, bry, thick]
            bperp = ba_angle + np.pi / 2.0
            bhw = 0.035
            bb1 = [origin[0] + np.cos(bperp) * bhw, origin[1] + np.sin(bperp) * bhw, thick]
            bb2 = [origin[0] - np.cos(bperp) * bhw, origin[1] - np.sin(bperp) * bhw, thick]
            sc = list(s) if i % 2 == 0 else list(h)
            vertices.extend([*bb1, *sc, 0.0, 0.0, 1.0,
                             *bb2, *sc, 0.0, 0.0, 1.0,
                             *branch_tip, *sc, 0.0, 0.0, 1.0])

    # Central hexagon disc
    for i in range(6):
        a1 = (i / 6) * 2.0 * np.pi
        a2 = ((i + 1) / 6) * 2.0 * np.pi
        cr = 0.10
        x1, y1 = cr * np.cos(a1), cr * np.sin(a1)
        x2, y2 = cr * np.cos(a2), cr * np.sin(a2)
        vertices.extend([0.0, 0.0, thick, *h, 0.0, 0.0, 1.0,
                         x1,  y1,  thick, *h, 0.0, 0.0, 1.0,
                         x2,  y2,  thick, *h, 0.0, 0.0, 1.0])

    return _make_mesh(vertices)


# ---------------------------------------------------------------------------
# Dispatch table: world index → mesh factory function
# ---------------------------------------------------------------------------

WORLD_COLLECTIBLE_FACTORIES = {
    0: create_slipper_mesh,       # Cinderella  — Glass Slipper
    1: create_apple_mesh,         # Snow White  — Magic Apple
    2: create_lamp_mesh,          # Aladdin     — Magic Lamp
    3: create_sun_symbol_mesh,    # Tangled     — Sun Symbol
    4: create_lion_token_mesh,    # Lion King   — Lion Token
    5: create_seashell_mesh,      # Mermaid     — Seashell
    6: create_pixie_dust_mesh,    # Peter Pan   — Pixie Dust
    7: create_snowflake_mesh,     # Frozen      — Snowflake
}


def create_collectible_mesh_for_world(world_index: int, world_config=None) -> Mesh:
    """
    Returns the appropriate collectible mesh for the given world.
    Uses world_config colors if provided, otherwise default palette.
    """
    factory = WORLD_COLLECTIBLE_FACTORIES.get(world_index % 8, create_coin_mesh)
    if world_config is not None:
        return factory(
            primary=world_config.collectible_color_primary,
            secondary=world_config.collectible_color_secondary,
            highlight=world_config.collectible_color_highlight,
        )
    return factory()


# ---------------------------------------------------------------------------
# Mesh Cache — world-aware singleton
# ---------------------------------------------------------------------------

class CollectibleMeshCache:
    """
    Singleton cache for the active world's collectible GPU mesh.
    Call refresh_for_world(world_index, world_config) on world change.
    """
    _instance = None

    def __init__(self):
        self.mesh: Optional[Mesh] = None
        self._world_index: int = -1

    @classmethod
    def get(cls) -> "CollectibleMeshCache":
        if cls._instance is None:
            cls._instance = CollectibleMeshCache()
            cls._instance.init_mesh()
        return cls._instance

    def init_mesh(self, world_index: int = 0, world_config=None) -> None:
        if self.mesh is not None and self._world_index == world_index:
            return
        if self.mesh is not None:
            self.mesh.delete()
            self.mesh = None
        self.mesh = create_collectible_mesh_for_world(world_index, world_config)
        self._world_index = world_index

    def refresh_for_world(self, world_index: int, world_config=None) -> None:
        """Rebuilds the collectible mesh for the new world. Called on world transition."""
        if world_index == self._world_index:
            return
        if self.mesh is not None:
            self.mesh.delete()
            self.mesh = None
        self.mesh = create_collectible_mesh_for_world(world_index, world_config)
        self._world_index = world_index
        name = world_config.collectible_name if world_config else "Coin"
        print(f"[COLLECTIBLE] Mesh updated to: {name}")

    def get_mesh(self) -> Optional[Mesh]:
        return self.mesh

    def delete(self) -> None:
        if self.mesh:
            self.mesh.delete()
            self.mesh = None
        CollectibleMeshCache._instance = None


# ---------------------------------------------------------------------------
# Collectible Entity
# ---------------------------------------------------------------------------

class Collectible:
    """3D World-aware Collectible Entity with rotation and floating animation."""

    def __init__(self, lane: int, z: float, base_y: float = 0.90):
        self.lane   = max(-1, min(1, lane))
        self.x      = float(self.lane * settings.LANE_WIDTH)
        self.base_y = float(base_y)
        self.y      = self.base_y
        self.z      = float(z)

        self.rotation_y = float(np.random.uniform(0.0, 360.0))
        self.spin_speed = 180.0
        self.bob_timer  = float(np.random.uniform(0.0, 2 * np.pi))

        self.collected = False
        self.mesh = CollectibleMeshCache.get().get_mesh()

    def update(self, speed: float, delta_time: float) -> None:
        """Updates position, continuous rotation, and floating bobbing."""
        self.z += speed * delta_time
        self.rotation_y = (self.rotation_y + self.spin_speed * delta_time) % 360.0
        self.bob_timer  += 4.0 * delta_time
        self.y = self.base_y + 0.10 * np.sin(self.bob_timer)

    def is_past_player(self, threshold_z: float = 15.0) -> bool:
        return self.z > threshold_z

    def get_bounding_box(self):
        r = 0.40
        min_pt = np.array([self.x - r, self.y - r, self.z - r], dtype=np.float32)
        max_pt = np.array([self.x + r, self.y + r, self.z + r], dtype=np.float32)
        return min_pt, max_pt

    def get_model_matrix(self) -> pyrr.Matrix44:
        t = pyrr.Matrix44.from_translation([self.x, self.y, self.z])
        r = pyrr.Matrix44.from_y_rotation(np.radians(self.rotation_y))
        return t * r

    def render(self, renderer, shader, camera) -> None:
        mesh = CollectibleMeshCache.get().get_mesh()
        if not self.collected and mesh is not None:
            renderer.render(mesh, shader, self.get_model_matrix(), camera)
