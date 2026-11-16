"""
powerup.py - Power-Up Entities, Procedural Geometry, and Mesh Cache.
Phase 8.1: Defines PowerUpType, 3D procedural meshes for universal power-ups
(Shield, Magnet, Double Score) and World Special Ability Orbs, with singleton
GPU mesh caching matching CollectibleMeshCache conventions.
"""

from enum import Enum
from typing import Tuple, List, Optional
import numpy as np
import pyrr
from config import settings
from engine.mesh import Mesh, VertexAttribute
from engine.shader import ShaderProgram
from engine.camera import Camera
from engine.renderer import Renderer
from entities.scenery import add_box, add_quad


class PowerUpType(str, Enum):
    """Universal and World-Specific Power-Up classifications."""
    MAGIC_SHIELD = "magic_shield"
    TREASURE_MAGNET = "treasure_magnet"
    DOUBLE_SCORE = "double_score"
    WORLD_ABILITY = "world_ability"


# ---------------------------------------------------------------------------
# Vertex Attribute Helpers
# ---------------------------------------------------------------------------

def _attrs() -> List[VertexAttribute]:
    return [
        VertexAttribute(location=0, size=3),
        VertexAttribute(location=1, size=3),
        VertexAttribute(location=2, size=3),
    ]


def _make_mesh(vertices: list) -> Mesh:
    return Mesh(vertices=np.array(vertices, dtype=np.float32), attributes=_attrs())


# ---------------------------------------------------------------------------
# Procedural 3D Mesh Creators
# ---------------------------------------------------------------------------

def create_shield_mesh() -> Mesh:
    """
    Builds a 3D protective crystal polyhedron with glowing outer facets
    and inner diamond core.
    """
    vertices: list = []
    core = [0.35, 0.75, 1.00]      # Luminous sapphire blue
    edge = [0.70, 0.90, 1.00]      # Bright rim highlight
    facet = [0.20, 0.50, 0.85]     # Deep crystal facet
    gold = [0.95, 0.82, 0.25]      # Golden clasp rim

    # Central faceted gem body (layered stepped octagonal boxes)
    add_box(vertices, [-0.22, 0.05, -0.22], [0.22, 0.45, 0.22], core)
    add_box(vertices, [-0.28, 0.15, -0.16], [0.28, 0.35, 0.16], facet)
    add_box(vertices, [-0.16, 0.15, -0.28], [0.16, 0.35, 0.28], facet)

    # Top pointed crystal pyramid peak
    add_box(vertices, [-0.14, 0.45, -0.14], [0.14, 0.56, 0.14], edge)
    add_box(vertices, [-0.06, 0.56, -0.06], [0.06, 0.65, 0.06], [1.0, 1.0, 1.0])

    # Bottom tapered crystal point
    add_box(vertices, [-0.14, -0.06, -0.14], [0.14, 0.05, 0.14], facet)
    add_box(vertices, [-0.06, -0.15, -0.06], [0.06, -0.06, 0.06], edge)

    # Outer protective crest ring / clasp
    add_box(vertices, [-0.34, 0.22, -0.08], [0.34, 0.28, 0.08], gold)
    add_box(vertices, [-0.08, 0.22, -0.34], [0.08, 0.28, 0.34], gold)

    return _make_mesh(vertices)


def create_magnet_mesh() -> Mesh:
    """
    Builds a 3D golden horseshoe magnet with red/silver metallic poles.
    """
    vertices: list = []
    gold = [0.98, 0.80, 0.18]      # Rich polished gold body
    silver = [0.88, 0.90, 0.94]    # Silver metallic poles
    red_accent = [0.92, 0.18, 0.18] # Classic magnet red tips
    shadow = [0.70, 0.55, 0.10]

    # Curved base arch (bottom connector spanning X: -0.25 to 0.25)
    add_box(vertices, [-0.25, -0.05, -0.10], [0.25, 0.10, 0.10], gold)
    add_box(vertices, [-0.20, -0.08, -0.08], [0.20, -0.05, 0.08], shadow)

    # Left prong (ascending Y: 0.10 to 0.55, at X: -0.30 to -0.15)
    add_box(vertices, [-0.30, 0.10, -0.10], [-0.15, 0.42, 0.10], gold)
    add_box(vertices, [-0.31, 0.42, -0.11], [-0.14, 0.52, 0.11], red_accent)
    add_box(vertices, [-0.31, 0.52, -0.11], [-0.14, 0.60, 0.11], silver)

    # Right prong (ascending Y: 0.10 to 0.55, at X: 0.15 to 0.30)
    add_box(vertices, [0.15, 0.10, -0.10], [0.30, 0.42, 0.10], gold)
    add_box(vertices, [0.14, 0.42, -0.11], [0.31, 0.52, 0.11], red_accent)
    add_box(vertices, [0.14, 0.52, -0.11], [0.31, 0.60, 0.11], silver)

    # Luminous magnetic energy core between prongs
    add_box(vertices, [-0.08, 0.22, -0.06], [0.08, 0.38, 0.06], [1.0, 0.95, 0.50])

    return _make_mesh(vertices)


def create_double_score_mesh() -> Mesh:
    """
    Builds a 3D golden 2X emblem with a dimensional star crest and ring.
    """
    vertices: list = []
    gold_rim = [0.95, 0.78, 0.15]
    gold_face = [1.00, 0.90, 0.30]
    star_white = [1.00, 1.00, 0.85]
    ruby_trim = [0.85, 0.15, 0.20]

    # Outer octagonal badge / disc backing
    add_box(vertices, [-0.30, -0.05, -0.06], [0.30, 0.55, 0.06], gold_rim)
    add_box(vertices, [-0.26, -0.01, -0.08], [0.26, 0.51, 0.08], gold_face)
    add_box(vertices, [-0.28, 0.22, -0.09], [0.28, 0.28, 0.09], ruby_trim)

    # "2" glyph representation (procedural stepped segments)
    c2 = star_white
    # Top horizontal bar of '2'
    add_box(vertices, [-0.20, 0.40, 0.07], [-0.04, 0.46, 0.12], c2)
    # Upper-right vertical post
    add_box(vertices, [-0.08, 0.28, 0.07], [-0.04, 0.40, 0.12], c2)
    # Middle diagonal crossbar
    add_box(vertices, [-0.18, 0.22, 0.07], [-0.04, 0.28, 0.12], c2)
    # Lower-left vertical leg
    add_box(vertices, [-0.20, 0.14, 0.07], [-0.15, 0.22, 0.12], c2)
    # Bottom base bar
    add_box(vertices, [-0.20, 0.08, 0.07], [-0.04, 0.14, 0.12], c2)

    # "X" glyph representation (criss-crossing bars)
    cx = [1.0, 0.95, 0.45]
    add_box(vertices, [0.06, 0.08, 0.07], [0.22, 0.46, 0.12], cx)
    add_box(vertices, [0.06, 0.38, 0.07], [0.22, 0.16, 0.12], cx)
    # Central intersection highlight
    add_box(vertices, [0.11, 0.23, 0.08], [0.17, 0.31, 0.14], star_white)

    # Floating crown top
    add_box(vertices, [-0.12, 0.55, -0.04], [0.12, 0.64, 0.04], gold_rim)
    add_box(vertices, [-0.04, 0.64, -0.02], [0.04, 0.70, 0.02], star_white)

    return _make_mesh(vertices)


def create_world_orb_mesh(world_index: int = 0, world_config=None) -> Mesh:
    """
    Builds a luminous 3D celestial World Orb with dual orbiting rings,
    thematically colored to match the active Disney WorldConfig.
    """
    vertices: list = []

    if world_config is not None:
        p_col = list(world_config.collectible_color_primary)
        s_col = list(world_config.collectible_color_secondary)
        h_col = list(world_config.collectible_color_highlight)
    else:
        p_col = [0.85, 0.75, 0.95]
        s_col = [0.65, 0.45, 0.85]
        h_col = [1.00, 1.00, 1.00]

    # Inner mystical energy core
    add_box(vertices, [-0.16, 0.09, -0.16], [0.16, 0.41, 0.16], p_col)
    add_box(vertices, [-0.20, 0.13, -0.12], [0.20, 0.37, 0.12], s_col)
    add_box(vertices, [-0.12, 0.13, -0.20], [0.12, 0.37, 0.20], s_col)

    # Glowing center spark
    add_box(vertices, [-0.08, 0.17, -0.08], [0.08, 0.33, 0.08], h_col)

    # Horizontal planetary ring
    add_box(vertices, [-0.34, 0.23, -0.34], [0.34, 0.27, -0.26], h_col)
    add_box(vertices, [-0.34, 0.23,  0.26], [0.34, 0.27,  0.34], h_col)
    add_box(vertices, [-0.34, 0.23, -0.26], [-0.26, 0.27, 0.26], h_col)
    add_box(vertices, [ 0.26, 0.23, -0.26], [ 0.34, 0.27, 0.26], h_col)

    # Tilted orbital ring
    add_box(vertices, [-0.28, 0.04, -0.28], [0.28, 0.10, -0.22], s_col)
    add_box(vertices, [-0.28, 0.40,  0.22], [0.28, 0.46,  0.28], s_col)

    return _make_mesh(vertices)


# ---------------------------------------------------------------------------
# PowerUp Mesh Cache (Singleton)
# ---------------------------------------------------------------------------

class PowerUpMeshCache:
    """
    Singleton cache for power-up GPU meshes.
    Manages shared VBOs/VAOs for Shield, Magnet, Double Score, and World Orb,
    following CollectibleMeshCache resource ownership and cleanup conventions.
    """
    _instance: Optional["PowerUpMeshCache"] = None

    def __init__(self):
        self.shield_mesh: Optional[Mesh] = None
        self.magnet_mesh: Optional[Mesh] = None
        self.double_score_mesh: Optional[Mesh] = None
        self.world_orb_mesh: Optional[Mesh] = None
        self._world_index: int = -1

    @classmethod
    def get(cls) -> "PowerUpMeshCache":
        if cls._instance is None:
            cls._instance = PowerUpMeshCache()
            cls._instance.init_meshes()
        return cls._instance

    def init_meshes(self, world_index: int = 0, world_config=None) -> None:
        """Uploads meshes to GPU if not already initialized."""
        if self.shield_mesh is None:
            self.shield_mesh = create_shield_mesh()
        if self.magnet_mesh is None:
            self.magnet_mesh = create_magnet_mesh()
        if self.double_score_mesh is None:
            self.double_score_mesh = create_double_score_mesh()
        if self.world_orb_mesh is None or self._world_index != world_index:
            if self.world_orb_mesh is not None:
                self.world_orb_mesh.delete()
            self.world_orb_mesh = create_world_orb_mesh(world_index, world_config)
            self._world_index = world_index

    def refresh_for_world(self, world_index: int, world_config=None) -> None:
        """Rebuilds the World Orb mesh when transitioning to a new world."""
        if world_index == self._world_index and self.world_orb_mesh is not None:
            return
        if self.world_orb_mesh is not None:
            self.world_orb_mesh.delete()
            self.world_orb_mesh = None
        self.world_orb_mesh = create_world_orb_mesh(world_index, world_config)
        self._world_index = world_index
        name = world_config.name if world_config else f"World {world_index}"
        print(f"[POWERUP] World Orb mesh updated for: {name}")

    def get_mesh(self, powerup_type: PowerUpType) -> Optional[Mesh]:
        """Returns the cached GPU mesh for the requested power-up type."""
        if powerup_type == PowerUpType.MAGIC_SHIELD:
            return self.shield_mesh
        elif powerup_type == PowerUpType.TREASURE_MAGNET:
            return self.magnet_mesh
        elif powerup_type == PowerUpType.DOUBLE_SCORE:
            return self.double_score_mesh
        elif powerup_type == PowerUpType.WORLD_ABILITY:
            return self.world_orb_mesh
        return None

    def delete(self) -> None:
        """Releases all OpenGL GPU buffers cleanly."""
        if self.shield_mesh:
            self.shield_mesh.delete()
            self.shield_mesh = None
        if self.magnet_mesh:
            self.magnet_mesh.delete()
            self.magnet_mesh = None
        if self.double_score_mesh:
            self.double_score_mesh.delete()
            self.double_score_mesh = None
        if self.world_orb_mesh:
            self.world_orb_mesh.delete()
            self.world_orb_mesh = None
        self._world_index = -1
        PowerUpMeshCache._instance = None


# ---------------------------------------------------------------------------
# PowerUp Entity
# ---------------------------------------------------------------------------

class PowerUp:
    """
    3D World-aware Power-Up entity with rotation and sinusoidal bobbing.
    Follows identical coordinate and bounding conventions to Collectible.
    """

    def __init__(
        self,
        powerup_type: PowerUpType,
        lane: int,
        z: float,
        world_index: int = 0,
        base_y: float = 0.95
    ):
        self.powerup_type = powerup_type
        self.lane = max(-1, min(1, lane))
        self.x = float(self.lane * settings.LANE_WIDTH)
        self.base_y = float(base_y)
        self.y = self.base_y
        self.z = float(z)
        self.world_index = world_index

        self.rotation_y = float(np.random.uniform(0.0, 360.0))
        self.spin_speed = 150.0   # Degrees per second
        self.bob_timer = float(np.random.uniform(0.0, 2 * np.pi))
        self.collected = False

    def update(self, speed: float, delta_time: float) -> None:
        """Moves towards camera along +Z and animates rotation and bobbing."""
        self.z += speed * delta_time
        self.rotation_y = (self.rotation_y + self.spin_speed * delta_time) % 360.0
        self.bob_timer += 4.5 * delta_time
        self.y = self.base_y + 0.12 * np.sin(self.bob_timer)

    def is_past_player(self, threshold_z: float = 15.0) -> bool:
        """Returns True if power-up has moved past the player and camera."""
        return self.z > threshold_z

    def get_bounding_box(self) -> Tuple[np.ndarray, np.ndarray]:
        """Returns 3D AABB for collision with calibrated radius."""
        r = 0.45
        min_pt = np.array([self.x - r, self.y - r, self.z - r], dtype=np.float32)
        max_pt = np.array([self.x + r, self.y + r, self.z + r], dtype=np.float32)
        return min_pt, max_pt

    def get_model_matrix(self) -> pyrr.Matrix44:
        """Computes world transformation matrix."""
        t = pyrr.Matrix44.from_translation([self.x, self.y, self.z])
        r = pyrr.Matrix44.from_y_rotation(np.radians(self.rotation_y))
        return t * r

    def render(self, renderer: Renderer, shader: ShaderProgram, camera: Camera) -> None:
        """Renders using cached mesh if not yet collected."""
        if not self.collected:
            mesh = PowerUpMeshCache.get().get_mesh(self.powerup_type)
            if mesh is not None:
                renderer.render(mesh, shader, self.get_model_matrix(), camera)
