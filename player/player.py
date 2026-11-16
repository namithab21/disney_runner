"""
player.py - Advanced 3D Character Entities with 8 Unique Disney Runner Designs.
Features distinct silhouettes, hair styles, costumes, facial accents, and accessories:
 0. Cinderella: Ball gown running bodice, blonde bun, blue headband, choker, glass slippers.
 1. Snow White: Blue bodice with slashed red puff sleeves, white stand collar, dark bob hair, red hair ribbon bow.
 2. Aladdin: Open purple vest, shirtless chest detail, white baggy harem pants, red fez cap, curled toe slippers.
 3. Rapunzel: Lavender corset dress with pink lace, cascading golden braid with woven flower pins.
 4. Simba: Feline stylized humanoid runner, gold/amber fur, glorious red-brown chest/neck lion mane, perked ears, tail.
 5. Ariel: Shimmering purple seashell top, emerald scaled leggings, flowing red hair with starfish hair accessory.
 6. Peter Pan: Forest green jagged tunic with belt & dagger sheath, auburn hair, pointed green cap with red feather.
 7. Anna: Nordic winter traveling cloak, magenta capelet with brass clasp, dark dress with rosemaling gold trim, braided pigtails.
"""

from typing import List, Tuple, Optional
import numpy as np
import pyrr
from config import settings
from engine.mesh import Mesh, VertexAttribute
from engine.shader import ShaderProgram
from engine.camera import Camera
from engine.renderer import Renderer
from entities.scenery import add_box, add_quad
from player.movement import PlayerMovement
from player.animation import PlayerAnimation


def _attrs():
    return [
        VertexAttribute(location=0, size=3),
        VertexAttribute(location=1, size=3),
        VertexAttribute(location=2, size=3)
    ]


def _mesh(vertices: list) -> Mesh:
    arr = np.array(vertices, dtype=np.float32)
    return Mesh(vertices=arr, attributes=_attrs())


# =============================================================================
# 1. RUNNER TORSO MESH FACTORY (WORLD SPECIFIC SILHOUETTES & CLOTHING)
# =============================================================================

def create_runner_torso(world_idx: int, world_config) -> Mesh:
    vertices = []
    jk = list(world_config.runner_jacket)
    ac = list(world_config.runner_accent)
    sk = list(world_config.runner_skin)
    gold = [0.96, 0.82, 0.22]
    white = [0.95, 0.95, 0.95]

    if world_idx == 0:
        # Cinderella: Gown-inspired running corset with silver front tabard & white collar
        add_box(vertices, [-0.24, 0.08, -0.15], [0.24, 0.62, 0.15], jk)
        # Silver/White center bodice panel
        add_quad(vertices, [-0.08, 0.10, -0.155], [0.08, 0.10, -0.155],
                 [0.11, 0.60, -0.155], [-0.11, 0.60, -0.155], white, [0.0, 0.0, -1.0])
        # Waist peplum puffs
        add_box(vertices, [-0.27, 0.04, -0.17], [-0.18, 0.16, 0.17], [c * 1.15 for c in jk])
        add_box(vertices, [ 0.18, 0.04, -0.17], [ 0.27, 0.16, 0.17], [c * 1.15 for c in jk])
        # Black velvet choker at neck
        add_box(vertices, [-0.09, 0.60, -0.09], [0.09, 0.66, 0.09], [0.10, 0.08, 0.12])

    elif world_idx == 1:
        # Snow White: Royal blue bodice, yellow waist trim, tall standing white collar
        blue = [0.15, 0.25, 0.70]
        red = [0.85, 0.12, 0.15]
        yellow = [0.95, 0.85, 0.18]
        add_box(vertices, [-0.24, 0.08, -0.15], [0.24, 0.60, 0.15], blue)
        # Gold front laced trim
        add_box(vertices, [-0.02, 0.12, -0.155], [0.02, 0.58, -0.151], yellow)
        # Standing high white collar behind neck (+Z)
        add_box(vertices, [-0.22, 0.55, 0.08], [0.22, 0.78, 0.16], white)

    elif world_idx == 2:
        # Aladdin: Open purple vest revealing skin chest & gold trimmed edge
        purple = [0.42, 0.14, 0.52]
        add_box(vertices, [-0.22, 0.08, -0.14], [0.22, 0.60, 0.14], sk) # Chest skin
        # Left and Right vest flaps
        add_box(vertices, [-0.24, 0.08, -0.15], [-0.10, 0.62, 0.15], purple)
        add_box(vertices, [ 0.10, 0.08, -0.15], [ 0.24, 0.62, 0.15], purple)
        # Red sash cummerbund belt
        add_box(vertices, [-0.25, 0.00, -0.16], [ 0.25, 0.10, 0.16], [0.85, 0.15, 0.15])

    elif world_idx == 3:
        # Rapunzel: Lavender corset with pink criss-cross ribbon laces & puff shoulders
        lavender = [0.65, 0.45, 0.78]
        pink = [0.95, 0.60, 0.75]
        add_box(vertices, [-0.24, 0.08, -0.15], [0.24, 0.62, 0.15], lavender)
        add_quad(vertices, [-0.08, 0.10, -0.155], [0.08, 0.10, -0.155],
                 [0.10, 0.55, -0.155], [-0.10, 0.55, -0.155], pink, [0.0, 0.0, -1.0])
        add_box(vertices, [-0.24, 0.04, -0.16], [0.24, 0.10, 0.16], gold)

    elif world_idx == 4:
        # Simba: Feline lion anatomy — golden fur with majestic red-brown mane
        gold_fur = [0.90, 0.72, 0.32]
        mane_col = [0.65, 0.30, 0.10]
        cream = [0.96, 0.90, 0.75]
        add_box(vertices, [-0.23, 0.08, -0.15], [0.23, 0.60, 0.15], gold_fur)
        # Cream chest bib
        add_quad(vertices, [-0.10, 0.10, -0.155], [0.10, 0.10, -0.155],
                 [0.12, 0.52, -0.155], [-0.12, 0.52, -0.155], cream, [0.0, 0.0, -1.0])
        # Majestic chest & shoulder mane ruff
        add_box(vertices, [-0.27, 0.42, -0.18], [0.27, 0.70, 0.18], mane_col)
        # Tail attached to lower spine extending backward (+Z)
        add_box(vertices, [-0.04, 0.08, 0.14], [0.04, 0.35, 0.38], gold_fur)
        add_box(vertices, [-0.06, 0.30, 0.36], [0.06, 0.44, 0.48], mane_col) # Tail tuft

    elif world_idx == 5:
        # Ariel: Lavender/purple seashell top with green shimmering scale bodice
        seashell_purple = [0.68, 0.35, 0.80]
        scale_green = [0.12, 0.68, 0.62]
        add_box(vertices, [-0.22, 0.08, -0.14], [0.22, 0.60, 0.14], sk) # Midriff
        # Seashell cups on front
        add_box(vertices, [-0.22, 0.34, -0.18], [-0.03, 0.54, -0.12], seashell_purple)
        add_box(vertices, [ 0.03, 0.34, -0.18], [ 0.22, 0.54, -0.12], seashell_purple)
        # Emerald waistband
        add_box(vertices, [-0.24, 0.06, -0.15], [ 0.24, 0.16, 0.15], scale_green)

    elif world_idx == 6:
        # Peter Pan: Forest green jagged tunic with brown rope belt & dagger sheath
        forest_green = [0.18, 0.52, 0.22]
        leather = [0.42, 0.28, 0.16]
        add_box(vertices, [-0.24, 0.08, -0.15], [0.24, 0.62, 0.15], forest_green)
        # V-neck chest skin triangle
        add_quad(vertices, [-0.06, 0.46, -0.155], [0.06, 0.46, -0.155],
                 [0.08, 0.62, -0.155], [-0.08, 0.62, -0.155], sk, [0.0, 0.0, -1.0])
        # Leather belt with golden dagger sheath on right hip
        add_box(vertices, [-0.25, 0.08, -0.16], [0.25, 0.16, 0.16], leather)
        add_box(vertices, [0.22, 0.00, -0.12], [0.28, 0.26, -0.04], gold)

    else:
        # Anna (Frozen): Black Nordic vest with gold rosemaling embroidery & magenta capelet
        black_vest = [0.12, 0.14, 0.18]
        magenta = [0.72, 0.14, 0.38]
        add_box(vertices, [-0.24, 0.08, -0.15], [0.24, 0.60, 0.15], black_vest)
        # Gold rosemaling front filigree
        add_box(vertices, [-0.03, 0.14, -0.155], [0.03, 0.54, -0.151], gold)
        add_box(vertices, [-0.14, 0.26, -0.155], [0.14, 0.32, -0.151], gold)
        # Magenta capelet draped over shoulders & back (+Z)
        add_box(vertices, [-0.28, 0.40, -0.08], [0.28, 0.64, 0.22], magenta)

    return _mesh(vertices)


# =============================================================================
# 2. RUNNER HEAD MESH FACTORY (WORLD SPECIFIC HAIR, ACCESSORIES & EYES)
# =============================================================================

def create_runner_head(world_idx: int, world_config) -> Mesh:
    vertices = []
    sk = list(world_config.runner_skin)
    hr = list(world_config.runner_hair)
    ac = list(world_config.runner_accent)
    eye_dark = [0.12, 0.10, 0.14]
    eye_white = [0.98, 0.98, 0.98]
    lip_color = [0.82, 0.35, 0.38]

    # Base Head Core (X: -0.16 to 0.16, Y: 0.0 to 0.32, Z: -0.16 to 0.16)
    add_box(vertices, [-0.16, 0.0, -0.16], [0.16, 0.32, 0.16], sk)

    # Expressive Anime/Disney Eyes on front (-Z face)
    # Left eye
    add_box(vertices, [-0.13, 0.12, -0.165], [-0.03, 0.22, -0.158], eye_white)
    add_box(vertices, [-0.10, 0.14, -0.168], [-0.04, 0.20, -0.162], eye_dark)
    # Right eye
    add_box(vertices, [ 0.03, 0.12, -0.165], [ 0.13, 0.22, -0.158], eye_white)
    add_box(vertices, [ 0.04, 0.14, -0.168], [ 0.10, 0.20, -0.162], eye_dark)
    # Lips
    add_box(vertices, [-0.04, 0.04, -0.165], [0.04, 0.07, -0.158], lip_color)

    if world_idx == 0:
        # Cinderella: Elegant blonde swept updo bun + light blue satin headband
        add_box(vertices, [-0.18, 0.18, -0.14], [0.18, 0.36, 0.19], hr)
        # High round ballerina bun on top
        add_box(vertices, [-0.12, 0.34, -0.04], [0.12, 0.52, 0.16], [c * 1.1 for c in hr])
        # Blue satin headband with diamond jewel
        add_box(vertices, [-0.185, 0.26, -0.16], [0.185, 0.32, -0.08], ac)
        add_box(vertices, [-0.03, 0.30, -0.168], [0.03, 0.34, -0.155], [0.90, 0.95, 1.0])

    elif world_idx == 1:
        # Snow White: Jet-black bob hairstyle curling inward + bright red bow on top
        add_box(vertices, [-0.19, 0.14, -0.14], [0.19, 0.36, 0.19], hr)
        # Side bob hair curls
        add_box(vertices, [-0.21, 0.02, -0.10], [-0.15, 0.22, 0.12], hr)
        add_box(vertices, [ 0.15, 0.02, -0.10], [ 0.21, 0.22, 0.12], hr)
        # Red ribbon bow on top
        add_box(vertices, [-0.10, 0.34, -0.08], [0.10, 0.44, 0.02], ac)
        add_box(vertices, [-0.03, 0.35, -0.09], [0.03, 0.42, 0.03], [0.70, 0.08, 0.10])

    elif world_idx == 2:
        # Aladdin: Thick black hair with wind-swept front bang + iconic tilted red fez
        add_box(vertices, [-0.18, 0.18, -0.14], [0.18, 0.38, 0.19], hr)
        add_box(vertices, [-0.08, 0.26, -0.19], [0.08, 0.35, -0.14], hr) # Front swoop
        # Tilted red Fez hat
        add_box(vertices, [0.02, 0.36, -0.06], [0.14, 0.52, 0.06], [0.85, 0.12, 0.15])
        # Gold tassel
        add_box(vertices, [0.12, 0.42, 0.04], [0.16, 0.48, 0.12], [0.95, 0.82, 0.22])

    elif world_idx == 3:
        # Rapunzel: Cascading golden hair with long thick braid swinging down the back (+Z)
        add_box(vertices, [-0.18, 0.18, -0.14], [0.18, 0.38, 0.19], hr)
        # Mega braid extending down the back
        add_box(vertices, [-0.10, -0.10, 0.14], [0.10, 0.34, 0.24], hr)
        add_box(vertices, [-0.08, -0.35, 0.16], [0.08, -0.10, 0.24], [c * 1.08 for c in hr])
        # Flower clips in hair (magenta & white blossoms)
        add_box(vertices, [-0.16, 0.22, 0.15], [-0.10, 0.28, 0.20], [0.95, 0.35, 0.65])
        add_box(vertices, [ 0.02, 0.08, 0.21], [ 0.08, 0.14, 0.26], [0.95, 0.85, 0.25])

    elif world_idx == 4:
        # Simba: Lion cub/youth head with adorable perked ears and mane crown
        add_box(vertices, [-0.18, 0.12, -0.15], [0.18, 0.38, 0.18], hr)
        # Perked triangular lion ears
        add_box(vertices, [-0.22, 0.32, -0.06], [-0.14, 0.48, 0.06], [0.90, 0.72, 0.32])
        add_box(vertices, [-0.19, 0.34, -0.04], [-0.15, 0.44, 0.04], [0.55, 0.25, 0.10])
        add_box(vertices, [ 0.14, 0.32, -0.06], [ 0.22, 0.48, 0.06], [0.90, 0.72, 0.32])
        add_box(vertices, [ 0.15, 0.34, -0.04], [ 0.19, 0.44, 0.04], [0.55, 0.25, 0.10])
        # Dark lion nose
        add_box(vertices, [-0.03, 0.08, -0.18], [0.03, 0.13, -0.155], [0.35, 0.15, 0.12])

    elif world_idx == 5:
        # Ariel: Voluminous flowing crimson red hair + purple starfish hairclip
        add_box(vertices, [-0.20, 0.16, -0.14], [0.20, 0.38, 0.20], hr)
        # Giant red side bangs
        add_box(vertices, [-0.18, 0.24, -0.21], [0.05, 0.42, -0.14], hr)
        # Flowing red locks down sides & back
        add_box(vertices, [-0.24, -0.12, -0.04], [-0.16, 0.24, 0.18], hr)
        add_box(vertices, [ 0.16, -0.12, -0.04], [ 0.24, 0.24, 0.18], hr)
        # Aqua starfish hairclip
        add_box(vertices, [0.14, 0.28, -0.16], [0.22, 0.36, -0.09], [0.35, 0.85, 0.90])

    elif world_idx == 6:
        # Peter Pan: Spiky auburn hair + Robin Hood pointed green hat with tall red feather
        add_box(vertices, [-0.18, 0.18, -0.14], [0.18, 0.35, 0.19], hr)
        # Pointed green cap
        cap_green = [0.18, 0.54, 0.22]
        add_box(vertices, [-0.19, 0.28, -0.15], [0.19, 0.42, 0.20], cap_green)
        add_box(vertices, [-0.10, 0.40, -0.04], [0.10, 0.52, 0.18], cap_green)
        # Tall scarlet feather on left side
        add_box(vertices, [-0.18, 0.36, 0.02], [-0.14, 0.65, 0.08], [0.90, 0.12, 0.15])

    else:
        # Anna: Auburn hair with two braided pigtails over shoulders & white streak
        add_box(vertices, [-0.18, 0.18, -0.14], [0.18, 0.38, 0.19], hr)
        # Iconic white hair streak on right side
        add_box(vertices, [0.08, 0.22, -0.16], [0.14, 0.35, -0.08], [0.95, 0.95, 0.95])
        # Two braids dropping forward over shoulders
        add_box(vertices, [-0.20, -0.15, -0.14], [-0.14, 0.18, -0.06], hr)
        add_box(vertices, [ 0.14, -0.15, -0.14], [ 0.20, 0.18, -0.06], hr)
        # Teal hair bows at ends of braids
        add_box(vertices, [-0.21, -0.18, -0.14], [-0.13, -0.12, -0.06], [0.20, 0.60, 0.65])
        add_box(vertices, [ 0.13, -0.18, -0.14], [ 0.21, -0.12, -0.06], [0.20, 0.60, 0.65])

    return _mesh(vertices)


# =============================================================================
# 3. RUNNER ARMS MESH FACTORY
# =============================================================================

def create_runner_arm(world_idx: int, world_config) -> Mesh:
    vertices = []
    jk = list(world_config.runner_jacket)
    sk = list(world_config.runner_skin)
    ac = list(world_config.runner_accent)
    white = [0.95, 0.95, 0.95]

    if world_idx == 2: # Aladdin: bare arms with gold wrist cuffs
        add_box(vertices, [-0.07, -0.42, -0.07], [0.07, 0.0, 0.07], sk)
        add_box(vertices, [-0.075, -0.48, -0.075], [0.075, -0.42, 0.075], [0.95, 0.82, 0.22])
        add_box(vertices, [-0.065, -0.55, -0.065], [0.065, -0.48, 0.065], sk)
    elif world_idx == 4: # Simba: golden fur paws
        add_box(vertices, [-0.07, -0.44, -0.07], [0.07, 0.0, 0.07], jk)
        add_box(vertices, [-0.08, -0.55, -0.09], [0.08, -0.44, 0.07], [0.96, 0.88, 0.65])
    elif world_idx == 1: # Snow White: red/blue slashed puff sleeves + bare forearms
        add_box(vertices, [-0.10, -0.22, -0.10], [0.10, 0.0, 0.10], [0.20, 0.35, 0.80])
        add_box(vertices, [-0.105, -0.18, -0.105], [0.105, -0.12, 0.105], [0.85, 0.15, 0.15])
        add_box(vertices, [-0.065, -0.55, -0.065], [0.065, -0.22, 0.065], sk)
    else: # Standard sleeved jacket with wrist cuff & glove
        add_box(vertices, [-0.07, -0.34, -0.07], [0.07, 0.0, 0.07], jk)
        add_box(vertices, [-0.075, -0.40, -0.075], [0.075, -0.34, 0.075], ac)
        add_box(vertices, [-0.065, -0.55, -0.065], [0.065, -0.40, 0.065], sk)

    return _mesh(vertices)


# =============================================================================
# 4. RUNNER LEGS MESH FACTORY (WORLD SPECIFIC PANTS & DETAILED SHOES)
# =============================================================================

def create_runner_leg(world_idx: int, world_config) -> Mesh:
    vertices = []
    pt = list(world_config.runner_pants)
    sh = list(world_config.runner_shoes)
    sk = list(world_config.runner_skin)
    white = [0.96, 0.96, 0.96]

    if world_idx == 0:
        # Cinderella: Gown leggings with sparkling translucent glass slippers
        glass = [0.85, 0.95, 1.00]
        glass_rim = [0.60, 0.85, 1.00]
        add_box(vertices, [-0.09, -0.60, -0.09], [0.09, 0.0, 0.09], pt)
        # Transparent glass slipper with delicate high heel & crystal heart toe
        add_box(vertices, [-0.095, -0.74, -0.16], [0.095, -0.60, 0.095], glass)
        add_box(vertices, [-0.04, -0.80, 0.04], [0.04, -0.74, 0.095], glass_rim) # Heel
        add_box(vertices, [-0.06, -0.66, -0.18], [0.06, -0.58, -0.12], [1.0, 1.0, 1.0]) # Heart

    elif world_idx == 2:
        # Aladdin: Puffy white harem pants gathered at ankle & curled golden slippers
        add_box(vertices, [-0.12, -0.58, -0.12], [0.12, 0.0, 0.12], pt)
        # Curled toe Arabian slipper
        add_box(vertices, [-0.09, -0.72, -0.15], [0.09, -0.58, 0.09], sh)
        add_box(vertices, [-0.06, -0.68, -0.22], [0.06, -0.62, -0.14], [0.95, 0.82, 0.22]) # Curl

    elif world_idx == 4:
        # Simba: Lion fur digitigrade hind legs with claws
        add_box(vertices, [-0.09, -0.62, -0.09], [0.09, 0.0, 0.09], pt)
        add_box(vertices, [-0.10, -0.76, -0.17], [0.10, -0.62, 0.09], [0.92, 0.76, 0.36])
        # Three dark claws
        for cx in [-0.07, 0.0, 0.07]:
            add_box(vertices, [cx - 0.02, -0.78, -0.20], [cx + 0.02, -0.72, -0.16], [0.20, 0.15, 0.12])

    elif world_idx == 5:
        # Ariel: Scaled emerald mermaid fin leggings with ocean fin flair
        scale_green = [0.12, 0.68, 0.62]
        fin_light = [0.35, 0.88, 0.80]
        add_box(vertices, [-0.09, -0.62, -0.09], [0.09, 0.0, 0.09], scale_green)
        add_box(vertices, [-0.10, -0.76, -0.16], [0.10, -0.62, 0.10], scale_green)
        # Back fin flair
        add_box(vertices, [-0.13, -0.74, 0.08], [0.13, -0.60, 0.18], fin_light)

    else:
        # Standard detailed trousers with layered boot / sneaker & sole
        add_box(vertices, [-0.09, -0.60, -0.09], [0.09, 0.0, 0.09], pt)
        add_box(vertices, [-0.095, -0.74, -0.16], [0.095, -0.60, 0.095], sh)
        add_box(vertices, [-0.10,  -0.80, -0.17], [0.10,  -0.74, 0.10], white)

    return _mesh(vertices)


# =============================================================================
# 5. COMPLETE PLAYER ENTITY INTEGRATION
# =============================================================================

class Player:
    """3D Player Character Entity supporting 8 highly distinctive Disney Runners."""

    def __init__(self):
        self.movement = PlayerMovement()
        self.animation = PlayerAnimation()
        self.world_index = 0

        # Create initial meshes for World 0 (Cinderella)
        from worlds.world_config import get_world
        self._build_for_world(0, get_world(0))

    def _build_for_world(self, world_idx: int, world_config) -> None:
        self.world_index = world_idx
        self.mesh_torso     = create_runner_torso(world_idx, world_config)
        self.mesh_head      = create_runner_head(world_idx, world_config)
        self.mesh_arm_left  = create_runner_arm(world_idx, world_config)
        self.mesh_arm_right = create_runner_arm(world_idx, world_config)
        self.mesh_leg_left  = create_runner_leg(world_idx, world_config)
        self.mesh_leg_right = create_runner_leg(world_idx, world_config)

    def apply_world_config(self, world_config) -> None:
        """Dynamically morphs character geometry and appearance to new Disney runner."""
        self._delete_meshes()
        self._build_for_world(world_config.index, world_config)
        print(f"[PLAYER] Re-designed as {world_config.runner_name} with unique 3D model geometry")

    def _delete_meshes(self) -> None:
        for attr in ("mesh_torso", "mesh_head", "mesh_arm_left", "mesh_arm_right",
                     "mesh_leg_left", "mesh_leg_right"):
            m = getattr(self, attr, None)
            if m is not None:
                m.delete()
                setattr(self, attr, None)

    def move_left(self) -> bool:
        return self.movement.move_left()

    def move_right(self) -> bool:
        return self.movement.move_right()

    def jump(self) -> bool:
        return self.movement.jump()

    def slide(self) -> bool:
        return self.movement.slide()

    def update(self, delta_time: float) -> None:
        self.movement.update(delta_time)
        self.animation.update(
            delta_time=delta_time,
            state=self.movement.state,
            lateral_velocity=self.movement.lateral_velocity
        )

    @property
    def position(self) -> np.ndarray:
        return self.movement.position

    def render(self, renderer: Renderer, shader: ShaderProgram, camera: Camera) -> None:
        px, py, pz = self.movement.x, self.movement.y, self.movement.z

        # 1. Torso
        torso_y = 0.80 + self.animation.torso_bob_y + self.animation.crouch_offset_y
        torso_t = pyrr.Matrix44.from_translation([px, py + torso_y, pz])
        torso_r_roll  = pyrr.Matrix44.from_z_rotation(np.radians(self.animation.torso_roll))
        torso_r_pitch = pyrr.Matrix44.from_x_rotation(np.radians(self.animation.torso_pitch))
        torso_matrix = torso_t * torso_r_roll * torso_r_pitch
        if self.mesh_torso:
            renderer.render(self.mesh_torso, shader, torso_matrix, camera)

        # 2. Head
        head_local_t = pyrr.Matrix44.from_translation([0.0, 0.65, 0.0])
        head_matrix = torso_matrix * head_local_t
        if self.mesh_head:
            renderer.render(self.mesh_head, shader, head_matrix, camera)

        # 3. Left Arm
        shoulder_l_t = pyrr.Matrix44.from_translation([-0.32, 0.58, 0.0])
        arm_l_r = pyrr.Matrix44.from_x_rotation(np.radians(self.animation.left_arm_pitch))
        arm_l_matrix = torso_matrix * shoulder_l_t * arm_l_r
        if self.mesh_arm_left:
            renderer.render(self.mesh_arm_left, shader, arm_l_matrix, camera)

        # 4. Right Arm
        shoulder_r_t = pyrr.Matrix44.from_translation([0.32, 0.58, 0.0])
        arm_r_r = pyrr.Matrix44.from_x_rotation(np.radians(self.animation.right_arm_pitch))
        arm_r_matrix = torso_matrix * shoulder_r_t * arm_r_r
        if self.mesh_arm_right:
            renderer.render(self.mesh_arm_right, shader, arm_r_matrix, camera)

        # 5. Left Leg
        hip_y = 0.80 + self.animation.crouch_offset_y
        hip_l_t = pyrr.Matrix44.from_translation([px - 0.16, py + hip_y, pz])
        leg_l_r = pyrr.Matrix44.from_x_rotation(np.radians(self.animation.left_leg_pitch))
        leg_l_matrix = hip_l_t * torso_r_roll * leg_l_r
        if self.mesh_leg_left:
            renderer.render(self.mesh_leg_left, shader, leg_l_matrix, camera)

        # 6. Right Leg
        hip_r_t = pyrr.Matrix44.from_translation([px + 0.16, py + hip_y, pz])
        leg_r_r = pyrr.Matrix44.from_x_rotation(np.radians(self.animation.right_leg_pitch))
        leg_r_matrix = hip_r_t * torso_r_roll * leg_r_r
        if self.mesh_leg_right:
            renderer.render(self.mesh_leg_right, shader, leg_r_matrix, camera)

    def delete(self) -> None:
        self._delete_meshes()
