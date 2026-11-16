"""
road_segment.py - 3D Road Segment Mesh and World Environment Entity.
Generates an immersive, thematic environmental segment for all eight Disney worlds:
 0. Cinderella: White marble curbs, royal palace parapets, castle spires, blue banners, manicured trees.
 1. Snow White: Enchanted mossy forest floor, giant glowing red toadstool mushrooms, fallen mossy log bridges, dark twisted trees.
 2. Aladdin: Sun-baked Agrabah sandstone arches, desert sand dunes, tall date palms, striped market awning stalls.
 3. Tangled: Stone kingdom bridge balustrades, glowing wooden lantern poles with yellow festival lanterns, golden foliage trees.
 4. Lion King: Golden African savanna, flat-topped umbrella acacia trees, majestic red-brown rock outcrop koppies, dry grass tufts.
 5. Little Mermaid: Deep ocean bed, giant branching coral reefs (pink/coral/teal), luminous underwater kelp forests, floating bubble clusters.
 6. Peter Pan: Neverland jungle, towering ancient fantasy trees, Jolly Roger skull-crested pirate barrels, ship rope rigging posts.
 7. Frozen: Glistening snow-covered terrain, snow-laden evergreen conifers, crystalline ice spires and frozen castle battlements.
"""

from typing import Optional, Tuple
import numpy as np
import pyrr
from config import settings
from engine.mesh import Mesh, VertexAttribute
from engine.shader import ShaderProgram
from engine.camera import Camera
from engine.renderer import Renderer
from entities.scenery import add_quad, add_box, add_tree, add_guardrail


# Default theme colors (Cinderella / World 0)
_DEFAULT_GROUND   = (0.22, 0.52, 0.25)
_DEFAULT_ROAD_S   = (0.20, 0.21, 0.24)
_DEFAULT_ROAD_C   = (0.24, 0.25, 0.29)
_DEFAULT_SIDEWALK = (0.58, 0.58, 0.60)
_DEFAULT_FOLIAGE  = (0.14, 0.50, 0.22)
_DEFAULT_STYLE    = "kingdom"


class RoadSegment:
    """A modular 3D road segment with rich world-specific environmental geometry."""

    def __init__(
        self,
        z_position: float,
        length: float = settings.SEGMENT_LENGTH,
        variant: int = 0,
        ground_color: Tuple[float, float, float] = _DEFAULT_GROUND,
        road_color_side: Tuple[float, float, float] = _DEFAULT_ROAD_S,
        road_color_center: Tuple[float, float, float] = _DEFAULT_ROAD_C,
        sidewalk_color: Tuple[float, float, float] = _DEFAULT_SIDEWALK,
        foliage_tint: Tuple[float, float, float] = _DEFAULT_FOLIAGE,
        scenery_style: str = _DEFAULT_STYLE,
    ):
        self.z_position = z_position
        self.length = length
        self.variant = variant

        self._ground_color = ground_color
        self._road_color_side = road_color_side
        self._road_color_center = road_color_center
        self._sidewalk_color = sidewalk_color
        self._foliage_tint = foliage_tint
        self._scenery_style = scenery_style

        self.mesh: Optional[Mesh] = None
        self._build_mesh()

    def _build_mesh(self) -> None:
        if self.mesh is not None:
            self.mesh.delete()
            self.mesh = None

        vertices_list: list = []
        half_len = self.length / 2.0
        z_near = half_len
        z_far = -half_len

        grass_color   = list(self._ground_color)
        asphalt_side  = list(self._road_color_side)
        asphalt_cen   = list(self._road_color_center)
        sidewalk_surf = list(self._sidewalk_color)
        curb_face     = [c * 0.90 for c in sidewalk_surf]
        curb_outer    = [c * 0.75 for c in sidewalk_surf]
        sh = settings.SIDEWALK_HEIGHT

        # -------------------------------------------------------------------
        # 1. Surrounding Ground / Terrain with Outer Terraces
        # -------------------------------------------------------------------
        add_quad(vertices_list, [-55.0, -0.05, z_near], [-5.4,  -0.05, z_near],
                 [-5.4,  -0.05, z_far],  [-55.0, -0.05, z_far],  grass_color, [0.0, 1.0, 0.0])
        add_quad(vertices_list, [5.4,  -0.05, z_near], [55.0, -0.05, z_near],
                 [55.0, -0.05, z_far],   [5.4,  -0.05, z_far],   grass_color, [0.0, 1.0, 0.0])

        # Distant terrain elevation hills
        hill_color = [c * 0.85 for c in grass_color]
        add_quad(vertices_list, [-75.0, 3.5, z_near], [-55.0, -0.05, z_near],
                 [-55.0, -0.05, z_far], [-75.0, 3.5, z_far], hill_color, [0.2, 0.9, 0.0])
        add_quad(vertices_list, [55.0, -0.05, z_near], [75.0, 3.5, z_near],
                 [75.0, 3.5, z_far], [55.0, -0.05, z_far], hill_color, [-0.2, 0.9, 0.0])

        # -------------------------------------------------------------------
        # 2. Elevated Curbs & Sidewalks
        # -------------------------------------------------------------------
        # Left sidewalk
        add_quad(vertices_list, [-3.6, 0.0, z_near], [-3.6, 0.0, z_far],
                 [-3.6, sh,  z_far],  [-3.6, sh,  z_near],  curb_face, [1.0, 0.0, 0.0])
        add_quad(vertices_list, [-5.4, sh, z_near], [-3.6, sh, z_near],
                 [-3.6, sh, z_far],   [-5.4, sh, z_far],    sidewalk_surf, [0.0, 1.0, 0.0])
        add_quad(vertices_list, [-5.4, sh,  z_near], [-5.4, sh,  z_far],
                 [-5.4, 0.0, z_far],  [-5.4, 0.0, z_near],  curb_outer, [-1.0, 0.0, 0.0])

        # Right sidewalk
        add_quad(vertices_list, [3.6, 0.0, z_far],  [3.6, 0.0, z_near],
                 [3.6, sh,  z_near], [3.6, sh,  z_far],  curb_face, [-1.0, 0.0, 0.0])
        add_quad(vertices_list, [3.6, sh, z_near],  [5.4, sh, z_near],
                 [5.4, sh, z_far],   [3.6, sh, z_far],   sidewalk_surf, [0.0, 1.0, 0.0])
        add_quad(vertices_list, [5.4, sh,  z_far],  [5.4, sh,  z_near],
                 [5.4, 0.0, z_near], [5.4, 0.0, z_far],  curb_outer, [1.0, 0.0, 0.0])

        # -------------------------------------------------------------------
        # 3. Three Running Lanes
        # -------------------------------------------------------------------
        add_quad(vertices_list, [-3.6, 0.0, z_near], [-1.2, 0.0, z_near],
                 [-1.2, 0.0, z_far], [-3.6, 0.0, z_far], asphalt_side, [0.0, 1.0, 0.0])
        add_quad(vertices_list, [-1.2, 0.0, z_near], [ 1.2, 0.0, z_near],
                 [ 1.2, 0.0, z_far], [-1.2, 0.0, z_far], asphalt_cen, [0.0, 1.0, 0.0])
        add_quad(vertices_list, [ 1.2, 0.0, z_near], [ 3.6, 0.0, z_near],
                 [ 3.6, 0.0, z_far], [ 1.2, 0.0, z_far], asphalt_side, [0.0, 1.0, 0.0])

        # -------------------------------------------------------------------
        # 4. Road Markings
        # -------------------------------------------------------------------
        stripe_white  = [0.95, 0.95, 0.95]
        stripe_yellow = [0.98, 0.88, 0.25]
        marking_y = 0.005
        edge_w = 0.10

        add_quad(vertices_list,
                 [-3.50, marking_y, z_near], [-3.50 + edge_w, marking_y, z_near],
                 [-3.50 + edge_w, marking_y, z_far], [-3.50, marking_y, z_far],
                 stripe_white, [0.0, 1.0, 0.0])
        add_quad(vertices_list,
                 [3.50 - edge_w, marking_y, z_near], [3.50, marking_y, z_near],
                 [3.50, marking_y, z_far], [3.50 - edge_w, marking_y, z_far],
                 stripe_white, [0.0, 1.0, 0.0])

        dash_len = 2.5
        gap_len = 2.5
        period = dash_len + gap_len
        num_dashes = int(self.length / period)
        dash_hw = 0.07

        for i in range(num_dashes):
            d_start = -half_len + i * period + (gap_len / 2.0)
            d_end = d_start + dash_len
            for lane_x in [-1.2, 1.2]:
                add_quad(vertices_list,
                         [lane_x - dash_hw, marking_y, d_start],
                         [lane_x + dash_hw, marking_y, d_start],
                         [lane_x + dash_hw, marking_y, d_end],
                         [lane_x - dash_hw, marking_y, d_end],
                         stripe_yellow, [0.0, 1.0, 0.0])

        # -------------------------------------------------------------------
        # 5. Roadside Guardrails
        # -------------------------------------------------------------------
        add_guardrail(vertices_list, x=-5.3, z_start=z_near, z_end=z_far, base_y=sh, num_posts=5)
        add_guardrail(vertices_list, x=5.3,  z_start=z_near, z_end=z_far, base_y=sh, num_posts=5)

        # -------------------------------------------------------------------
        # 6. Deep World-Specific Thematic Scenery
        # -------------------------------------------------------------------
        self._add_scenery(vertices_list, z_near, z_far)

        vertices_arr = np.array(vertices_list, dtype=np.float32)
        attributes = [
            VertexAttribute(location=0, size=3),
            VertexAttribute(location=1, size=3),
            VertexAttribute(location=2, size=3),
        ]
        self.mesh = Mesh(vertices=vertices_arr, attributes=attributes)

    def _add_scenery(self, vertices_list: list, z_near: float, z_far: float) -> None:
        style = self._scenery_style
        ft = list(self._foliage_tint)
        v = self.variant

        if style == "forest": # SNOW WHITE
            # Dense enchanted forest: thick trees, fallen logs, glowing red mushroom clusters
            trees = [(-8.5, -8.0, 1.2), (-13.0, 5.0, 1.4), (9.0, -4.0, 1.3), (13.5, 8.0, 1.1)] if v % 2 == 0 else \
                    [(-9.5, -11.0, 1.3), (-7.5, 4.0, 1.0), (10.0, -8.0, 1.35), (8.0, 9.0, 1.15)]
            for (x, z, s) in trees:
                add_tree(vertices_list, x=x, z=z, scale=s, foliage_tint=ft)
            # Fallen mossy logs
            log_col = [0.32, 0.20, 0.12]
            moss_col = [0.22, 0.45, 0.18]
            add_box(vertices_list, [-11.0, 0.0, -2.0], [-7.5, 0.45, -1.2], log_col)
            add_box(vertices_list, [-10.5, 0.40, -1.9], [-8.0, 0.48, -1.3], moss_col)
            # Giant red toadstools
            self._add_toadstool(vertices_list, -7.2, 3.0, 1.3)
            self._add_toadstool(vertices_list, -6.8, 4.2, 0.8)
            self._add_toadstool(vertices_list,  7.2, -5.0, 1.1)

        elif style == "desert": # ALADDIN
            # Arabian city walls, desert sand dunes, date palms & market stalls
            sand_col = [0.82, 0.70, 0.42]
            awning_red = [0.85, 0.15, 0.18]
            awning_white = [0.95, 0.95, 0.95]
            # Desert palm trees
            palm_ft = [0.35, 0.58, 0.20]
            add_tree(vertices_list, x=-9.0, z=-7.0, scale=0.9, foliage_tint=palm_ft)
            add_tree(vertices_list, x=9.5,  z=5.0,  scale=0.95, foliage_tint=palm_ft)
            # Arabian market stall building on right
            add_box(vertices_list, [7.5, 0.0, -5.0], [12.0, 3.2, 2.0], sand_col)
            # Striped fabric awning roof
            add_box(vertices_list, [6.5, 2.8, -5.2], [11.5, 3.0, -1.5], awning_red)
            add_box(vertices_list, [6.5, 2.8, -1.5], [11.5, 3.0,  2.2], awning_white)
            # Sand dunes on left
            add_box(vertices_list, [-16.0, 0.0, -10.0], [-10.0, 2.2, 8.0], sand_col)

        elif style == "lanterns": # TANGLED
            # Glowing festival lantern posts, stone bridges, purple kingdom architecture
            add_tree(vertices_list, x=-9.0, z=-8.0, scale=1.1, foliage_tint=ft)
            add_tree(vertices_list, x=9.0,  z=6.0,  scale=1.15, foliage_tint=ft)
            # Ornate lantern posts with glowing lanterns
            self._add_lantern_post(vertices_list, -6.8, -3.0)
            self._add_lantern_post(vertices_list,  6.8,  3.0)
            # Kingdom castle tower on the side
            stone_col = [0.55, 0.48, 0.62]
            roof_gold = [0.95, 0.78, 0.22]
            add_box(vertices_list, [10.0, 0.0, -8.0], [14.0, 5.5, -4.0], stone_col)
            add_box(vertices_list, [9.5, 5.5, -8.5], [14.5, 7.5, -3.5], roof_gold) # Turret roof

        elif style == "savanna": # LION KING
            # African savanna: flat-top acacia trees, Pride Rock style stone koppies, dry grass
            acacia_col = [0.45, 0.48, 0.15]
            add_tree(vertices_list, x=-10.0, z=-9.0, scale=0.85, foliage_tint=acacia_col)
            add_tree(vertices_list, x=10.5,  z=4.0,  scale=0.90, foliage_tint=acacia_col)
            # Red/brown rock kopje outcrop
            rock_col = [0.62, 0.42, 0.25]
            add_box(vertices_list, [-15.0, 0.0, -4.0], [-8.5, 3.2, 4.0], rock_col)
            add_box(vertices_list, [-13.5, 3.0, -2.5], [-9.5, 4.2, 2.5], [c * 1.15 for c in rock_col])
            # Dry savanna grass clumps
            grass_dry = [0.72, 0.60, 0.22]
            add_box(vertices_list, [-7.2, 0.0, 6.0], [-6.4, 0.60, 6.8], grass_dry)
            add_box(vertices_list, [ 6.5, 0.0, -8.0], [ 7.3, 0.65, -7.2], grass_dry)

        elif style == "underwater": # LITTLE MERMAID
            # Coral reef pillars, sea kelp vegetation, floating air bubbles
            coral_pink = [0.95, 0.45, 0.60]
            coral_teal = [0.15, 0.75, 0.80]
            coral_gold = [0.95, 0.75, 0.25]
            bubble_col = [0.85, 0.95, 1.00]
            # Left coral garden
            add_box(vertices_list, [-9.5, 0.0, -6.0], [-8.2, 3.2, -4.8], coral_pink)
            add_box(vertices_list, [-8.8, 0.0, -4.5], [-7.6, 2.4, -3.5], coral_teal)
            add_box(vertices_list, [-12.0, 0.0, 2.0], [-10.5, 4.0, 3.5], coral_gold)
            # Right coral reef
            add_box(vertices_list, [8.2, 0.0, 3.0], [9.5, 3.5, 4.5], coral_teal)
            add_box(vertices_list, [9.2, 0.0, 4.8], [10.4, 2.6, 6.0], coral_pink)
            # Floating air bubbles
            add_box(vertices_list, [-7.5, 1.8, 1.0], [-7.1, 2.2, 1.4], bubble_col)
            add_box(vertices_list, [ 7.2, 2.4, -4.0], [ 7.6, 2.8, -3.6], bubble_col)

        elif style == "neverland": # PETER PAN
            # Fantasy forest, Jolly Roger pirate barrels, rope rigging posts
            add_tree(vertices_list, x=-9.0, z=-9.0, scale=1.2, foliage_tint=ft)
            add_tree(vertices_list, x=10.0, z=5.0,  scale=1.25, foliage_tint=ft)
            # Pirate rum barrels & treasure chest
            barrel_col = [0.45, 0.28, 0.15]
            chest_gold = [0.95, 0.82, 0.22]
            add_box(vertices_list, [-7.8, 0.0, -2.0], [-6.8, 1.1, -1.0], barrel_col)
            add_box(vertices_list, [-7.5, 0.0, -0.8], [-6.7, 0.9,  0.0], barrel_col)
            add_box(vertices_list, [ 6.8, 0.0,  2.0], [ 8.0, 0.75, 3.2], [0.38, 0.22, 0.12])
            add_box(vertices_list, [ 7.1, 0.35, 1.95], [ 7.7, 0.50, 2.05], chest_gold) # Lock

        elif style == "snow": # FROZEN
            # Snow-covered evergreen pines, crystalline ice spires, icy blue castle battlements
            ice_col = [0.72, 0.90, 1.00]
            snow_col = [0.96, 0.98, 1.00]
            add_tree(vertices_list, x=-9.0, z=-8.0, scale=1.1, foliage_tint=ft)
            add_tree(vertices_list, x=9.5,  z=6.0,  scale=1.15, foliage_tint=ft)
            # Snow banks along side of road
            add_box(vertices_list, [-8.5, 0.0, -12.0], [-6.5, 0.75, 12.0], snow_col)
            add_box(vertices_list, [ 6.5, 0.0, -12.0], [ 8.5, 0.75, 12.0], snow_col)
            # Giant icy crystal spires
            add_box(vertices_list, [-12.0, 0.0, -3.0], [-10.2, 5.0, -1.5], ice_col)
            add_box(vertices_list, [ 11.0, 0.0,  2.0], [ 12.8, 4.5,  3.5], ice_col)

        else: # CINDERELLA / KINGDOM
            # Royal palace parapets, castle spires with sapphire pennants, royal trees
            palace_stone = [0.82, 0.85, 0.92]
            palace_roof  = [0.22, 0.45, 0.85]
            gold_accent  = [0.95, 0.82, 0.22]
            add_tree(vertices_list, x=-9.0, z=-8.0, scale=1.1, foliage_tint=ft)
            add_tree(vertices_list, x=9.5,  z=7.0,  scale=1.15, foliage_tint=ft)
            # Royal castle tower structure
            add_box(vertices_list, [-14.0, 0.0, -6.0], [-9.5, 6.0, -1.5], palace_stone)
            add_box(vertices_list, [-14.5, 6.0, -6.5], [-9.0, 8.5, -1.0], palace_roof)
            add_box(vertices_list, [-12.0, 8.5, -4.0], [-11.6, 9.8, -3.6], gold_accent) # Spire

    def _add_toadstool(self, vertices_list: list, x: float, z: float, scale: float = 1.0) -> None:
        white = [0.95, 0.95, 0.92]
        red   = [0.90, 0.12, 0.15]
        # Stem
        add_box(vertices_list, [x - 0.12 * scale, 0.0, z - 0.12 * scale],
                               [x + 0.12 * scale, 0.65 * scale, z + 0.12 * scale], white)
        # Cap
        add_box(vertices_list, [x - 0.40 * scale, 0.55 * scale, z - 0.40 * scale],
                               [x + 0.40 * scale, 0.95 * scale, z + 0.40 * scale], red)
        # White dots
        add_box(vertices_list, [x - 0.15 * scale, 0.92 * scale, z - 0.15 * scale],
                               [x + 0.15 * scale, 0.98 * scale, z + 0.15 * scale], white)

    def _add_lantern_post(self, vertices_list: list, x: float, z: float) -> None:
        pole_col = [0.35, 0.24, 0.14]
        gold_glow = [1.00, 0.85, 0.20]
        # Tall post
        add_box(vertices_list, [x - 0.08, 0.0, z - 0.08], [x + 0.08, 3.2, z + 0.08], pole_col)
        # Crossbar
        add_box(vertices_list, [x - 0.45, 3.0, z - 0.06], [x + 0.45, 3.15, z + 0.06], pole_col)
        # Glowing lanterns hanging from crossbar
        add_box(vertices_list, [x - 0.40, 2.5, z - 0.15], [x - 0.15, 2.95, z + 0.15], gold_glow)
        add_box(vertices_list, [x + 0.15, 2.5, z - 0.15], [x + 0.40, 2.95, z + 0.15], gold_glow)

    def apply_world_config(
        self,
        ground_color: Tuple[float, float, float],
        road_color_side: Tuple[float, float, float],
        road_color_center: Tuple[float, float, float],
        sidewalk_color: Tuple[float, float, float],
        foliage_tint: Tuple[float, float, float],
        scenery_style: str,
    ) -> None:
        self._ground_color = ground_color
        self._road_color_side = road_color_side
        self._road_color_center = road_color_center
        self._sidewalk_color = sidewalk_color
        self._foliage_tint = foliage_tint
        self._scenery_style = scenery_style
        self._build_mesh()

    def update(self, speed: float, delta_time: float) -> None:
        self.z_position += speed * delta_time

    def get_model_matrix(self) -> pyrr.Matrix44:
        return pyrr.Matrix44.from_translation([0.0, 0.0, self.z_position])

    def render(self, renderer: Renderer, shader: ShaderProgram, camera: Camera) -> None:
        if self.mesh is None:
            return
        renderer.render(mesh=self.mesh, shader=shader,
                        model_matrix=self.get_model_matrix(), camera=camera)

    def delete(self) -> None:
        if self.mesh:
            self.mesh.delete()
            self.mesh = None
