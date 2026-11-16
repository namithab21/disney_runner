"""
villain.py - Advanced 3D Villain Entities with 8 Unique Iconic Disney Antagonist Designs.
Features distinct silhouettes, robes, capes, crowns, headwear, and reaching predator animations:
 0. Lady Tremaine (Cinderella): Flared burgundy Victorian gown, high standing collar, pompadour hair, brooch.
 1. Evil Queen (Snow White): Flowing royal purple robe, gold rope belt, white standing fan collar, pointed high gold crown.
 2. Jafar (Aladdin): Towering black/red robes with wide shoulder flair, tall black sultan mitre headdress with ruby jewel, coiled cobra staff.
 3. Mother Gothel (Tangled): Deep crimson hooded cowl, gold buckle belt, voluminous cascading dark curls.
 4. Scar (Lion King): Sleek tawny predator body, iconic black shaggy mane, sinister facial scar over left eye, extended claws.
 5. Ursula (Little Mermaid): Imposing curvy silhouette, purple tentacle dress base, sculpted shock of white sea-witch hair, golden nautilus shell pendant.
 6. Captain Hook (Peter Pan): Scarlet naval frock coat with gold braided frogging, purple plumaged cavalier hat, iconic gleaming steel hook on left arm.
 7. Prince Hans (Frozen): Aristocratic navy & white swallowtail uniform with gold epaulets, sideburns, military medal ribbons.
"""

from typing import Tuple, Optional
import numpy as np
import pyrr
from config import settings
from engine.mesh import Mesh, VertexAttribute
from engine.shader import ShaderProgram
from engine.camera import Camera
from engine.renderer import Renderer
from entities.scenery import add_box, add_quad


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
# 1. VILLAIN GOWN / SKIRT / LOWER BODY FACTORY
# =============================================================================

def create_villain_skirt_mesh(world_idx: int, world_config) -> Mesh:
    vertices = []
    gw = list(world_config.villain_gown)
    ac = list(world_config.villain_accent)
    gold = [0.95, 0.82, 0.22]
    black = [0.10, 0.08, 0.12]
    boots = [0.08, 0.08, 0.08]

    if world_idx == 0:
        # Lady Tremaine: Severe burgundy Victorian skirt with black velvet apron panel
        add_box(vertices, [-0.36, 0.0, -0.26],  [0.36, 0.40, 0.26],  gw)
        add_box(vertices, [-0.30, 0.38, -0.22], [0.30, 0.85, 0.22],  gw)
        add_quad(vertices, [-0.14, 0.02, -0.265], [0.14, 0.02, -0.265],
                 [0.12, 0.84, -0.225], [-0.12, 0.84, -0.225], black, [0.0, 0.0, -1.0])
        add_box(vertices, [-0.37, 0.0, -0.27], [0.37, 0.08, 0.27], ac)
        add_box(vertices, [-0.22, 0.0, -0.34], [-0.08, 0.08, -0.24], boots)
        add_box(vertices, [ 0.08, 0.0, -0.34], [ 0.22, 0.08, -0.24], boots)

    elif world_idx == 1:
        # Evil Queen: Dramatic royal purple floor-length robe with gold cord belt
        add_box(vertices, [-0.38, 0.0, -0.28], [0.38, 0.45, 0.28], gw)
        add_box(vertices, [-0.32, 0.42, -0.24], [0.32, 0.85, 0.24], gw)
        # Gold hanging cord belt down the front
        add_box(vertices, [-0.04, 0.05, -0.29], [0.04, 0.80, -0.25], gold)
        add_box(vertices, [-0.07, 0.02, -0.30], [0.07, 0.08, -0.24], gold) # Tassel

    elif world_idx == 2:
        # Jafar: Flowing pitch-black and blood-red sorcerer robes
        red_trim = [0.85, 0.12, 0.15]
        add_box(vertices, [-0.36, 0.0, -0.26], [0.36, 0.40, 0.26], [0.08, 0.06, 0.08])
        add_box(vertices, [-0.30, 0.38, -0.22], [0.30, 0.85, 0.22], [0.08, 0.06, 0.08])
        # Blood red front slit revealing inner crimson silk
        add_quad(vertices, [-0.10, 0.0, -0.265], [0.10, 0.0, -0.265],
                 [0.02, 0.84, -0.225], [-0.02, 0.84, -0.225], red_trim, [0.0, 0.0, -1.0])
        # Pointed curled black sorcerer shoes
        add_box(vertices, [-0.22, 0.0, -0.38], [-0.08, 0.08, -0.22], boots)
        add_box(vertices, [ 0.08, 0.0, -0.38], [ 0.22, 0.08, -0.22], boots)

    elif world_idx == 4:
        # Scar: Sleek black-maned lion body with predatory hind legs and tail
        lion_fur = [0.55, 0.42, 0.24]
        add_box(vertices, [-0.24, 0.0, -0.20], [0.24, 0.50, 0.20], lion_fur)
        add_box(vertices, [-0.22, 0.45, -0.18], [0.22, 0.85, 0.18], lion_fur)
        # Tail with black tuft
        add_box(vertices, [-0.04, 0.12, 0.18], [0.04, 0.40, 0.45], lion_fur)
        add_box(vertices, [-0.06, 0.36, 0.42], [0.06, 0.48, 0.55], black)

    elif world_idx == 5:
        # Ursula: Wide black torso with 6 writhing purple-underbellied sea octopus tentacles
        tentacle_black = [0.12, 0.08, 0.14]
        tentacle_purple = [0.65, 0.20, 0.70]
        add_box(vertices, [-0.42, 0.0, -0.32], [0.42, 0.45, 0.32], tentacle_black)
        add_box(vertices, [-0.36, 0.42, -0.26], [0.36, 0.85, 0.26], tentacle_black)
        # Coiled tentacles around base
        for tx, tz in [(-0.46, -0.25), (0.46, -0.25), (-0.46, 0.25), (0.46, 0.25), (0.0, -0.36), (0.0, 0.36)]:
            add_box(vertices, [tx - 0.10, 0.0, tz - 0.10], [tx + 0.10, 0.24, tz + 0.10], tentacle_purple)

    elif world_idx == 6:
        # Captain Hook: Crimson breeches with white stockings and buckle shoes
        add_box(vertices, [-0.24, 0.45, -0.16], [0.24, 0.85, 0.16], [0.70, 0.12, 0.15]) # Breeches
        # White naval stockings
        add_box(vertices, [-0.22, 0.10, -0.14], [-0.08, 0.50, 0.14], [0.95, 0.95, 0.95])
        add_box(vertices, [ 0.08, 0.10, -0.14], [ 0.22, 0.50, 0.14], [0.95, 0.95, 0.95])
        # Black buckled shoes
        add_box(vertices, [-0.23, 0.0, -0.24], [-0.07, 0.10, 0.12], boots)
        add_box(vertices, [ 0.07, 0.0, -0.24], [ 0.23, 0.10, 0.12], boots)
        add_box(vertices, [-0.20, 0.06, -0.25], [-0.10, 0.11, -0.22], gold)
        add_box(vertices, [ 0.10, 0.06, -0.25], [ 0.20, 0.11, -0.22], gold)

    elif world_idx == 7:
        # Prince Hans: White military dress trousers with grey cavalry riding boots
        add_box(vertices, [-0.24, 0.45, -0.16], [0.24, 0.85, 0.16], [0.92, 0.92, 0.96])
        add_box(vertices, [-0.22, 0.0, -0.16], [-0.08, 0.48, 0.16], [0.35, 0.35, 0.38])
        add_box(vertices, [ 0.08, 0.0, -0.16], [ 0.22, 0.48, 0.16], [0.35, 0.35, 0.38])

    else:
        # Mother Gothel / Generic: Rich burgundy gown with gold hem trim
        add_box(vertices, [-0.36, 0.0, -0.26],  [0.36, 0.40, 0.26],  gw)
        add_box(vertices, [-0.30, 0.38, -0.22], [0.30, 0.85, 0.22],  gw)
        add_box(vertices, [-0.37, 0.0, -0.27], [0.37, 0.08, 0.27], ac)
        add_box(vertices, [-0.22, 0.0, -0.34], [-0.08, 0.08, -0.24], boots)
        add_box(vertices, [ 0.08, 0.0, -0.34], [ 0.22, 0.08, -0.24], boots)

    return _mesh(vertices)


# =============================================================================
# 2. VILLAIN TORSO & ACCESSORIES FACTORY
# =============================================================================

def create_villain_torso_mesh(world_idx: int, world_config) -> Mesh:
    vertices = []
    gw = list(world_config.villain_gown)
    ac = list(world_config.villain_accent)
    sk = list(world_config.villain_skin)
    gold = [0.95, 0.82, 0.22]
    white = [0.95, 0.95, 0.95]

    if world_idx == 0:
        # Lady Tremaine: Bodice with emerald brooch & fan collar
        add_box(vertices, [-0.24, 0.0, -0.15], [0.24, 0.65, 0.15], gw)
        add_box(vertices, [-0.22, 0.55, 0.08], [0.22, 0.88, 0.18], [0.12, 0.10, 0.14])
        add_box(vertices, [-0.05, 0.52, -0.165], [0.05, 0.62, -0.152], ac)
        add_box(vertices, [-0.035, 0.535, -0.168], [0.035, 0.605, -0.154], [0.12, 0.65, 0.35])

    elif world_idx == 1:
        # Evil Queen: Black cowl bodice, gigantic white standing queen collar
        add_box(vertices, [-0.24, 0.0, -0.15], [0.24, 0.65, 0.15], [0.10, 0.08, 0.14])
        # Giant white fan collar rising high behind head
        add_box(vertices, [-0.28, 0.52, 0.10], [0.28, 0.95, 0.18], white)
        # Ruby brooch at neck
        add_box(vertices, [-0.05, 0.50, -0.165], [0.05, 0.60, -0.152], [0.85, 0.12, 0.15])

    elif world_idx == 2:
        # Jafar: Dramatic winged shoulder pads & black/gold robe
        add_box(vertices, [-0.24, 0.0, -0.15], [0.24, 0.65, 0.15], [0.08, 0.06, 0.08])
        # Giant angular shoulder pads
        add_box(vertices, [-0.36, 0.45, -0.16], [-0.20, 0.72, 0.16], [0.85, 0.15, 0.15])
        add_box(vertices, [ 0.20, 0.45, -0.16], [ 0.36, 0.72, 0.16], [0.85, 0.15, 0.15])
        # Gold cobra crest on chest
        add_box(vertices, [-0.04, 0.30, -0.165], [0.04, 0.58, -0.152], gold)

    elif world_idx == 4:
        # Scar: Sinister black shaggy mane completely draping upper chest & shoulders
        add_box(vertices, [-0.24, 0.0, -0.15], [0.24, 0.65, 0.15], [0.55, 0.42, 0.24])
        # Voluminous black mane ruff
        add_box(vertices, [-0.30, 0.35, -0.18], [0.30, 0.72, 0.18], [0.10, 0.08, 0.10])

    elif world_idx == 5:
        # Ursula: Curvy black corset with glowing gold nautilus shell necklace
        add_box(vertices, [-0.28, 0.0, -0.18], [0.28, 0.65, 0.18], [0.10, 0.08, 0.12])
        # Decolletage skin
        add_box(vertices, [-0.18, 0.45, -0.185], [0.18, 0.64, -0.12], sk)
        # Golden nautilus shell pendant
        add_box(vertices, [-0.04, 0.40, -0.19], [0.04, 0.50, -0.15], gold)

    elif world_idx == 6:
        # Captain Hook: Royal crimson officer coat with gold lace embroidery & white cravat
        crimson = [0.72, 0.10, 0.15]
        add_box(vertices, [-0.26, 0.0, -0.16], [0.26, 0.65, 0.16], crimson)
        # Gold braided frog closures down front
        for yb in [0.20, 0.32, 0.44]:
            add_box(vertices, [-0.14, yb, -0.168], [0.14, yb + 0.04, -0.155], gold)
        # White ruffled lace cravat
        add_box(vertices, [-0.08, 0.48, -0.175], [0.08, 0.64, -0.15], white)

    elif world_idx == 7:
        # Prince Hans: Tailored military dress jacket with gold epaulets & sash
        jacket_grey = [0.85, 0.88, 0.92]
        navy_collar = [0.15, 0.25, 0.45]
        add_box(vertices, [-0.24, 0.0, -0.15], [0.24, 0.65, 0.15], jacket_grey)
        # Gold fringed epaulets on shoulders
        add_box(vertices, [-0.32, 0.54, -0.14], [-0.20, 0.65, 0.14], gold)
        add_box(vertices, [ 0.20, 0.54, -0.14], [ 0.32, 0.65, 0.14], gold)
        # Navy blue high lapels
        add_box(vertices, [-0.14, 0.45, -0.16], [0.14, 0.66, -0.14], navy_collar)

    else:
        # Mother Gothel / Default
        add_box(vertices, [-0.24, 0.0, -0.15], [0.24, 0.65, 0.15], gw)
        add_box(vertices, [-0.22, 0.02, -0.16], [0.22, 0.10, 0.16], gold)

    return _mesh(vertices)


# =============================================================================
# 3. VILLAIN HEAD, HAIR & CROWN FACTORY
# =============================================================================

def create_villain_head_mesh(world_idx: int, world_config) -> Mesh:
    vertices = []
    sk = list(world_config.villain_skin)
    hr = list(world_config.villain_hair)
    dark_eye = [0.10, 0.08, 0.10]
    white_eye = [0.95, 0.95, 0.95]
    red_lip = [0.60, 0.12, 0.15]
    gold = [0.95, 0.82, 0.22]

    # Head core
    add_box(vertices, [-0.16, 0.0, -0.16], [0.16, 0.32, 0.16], sk)
    # Sinister eyes
    add_box(vertices, [-0.13, 0.14, -0.165], [-0.03, 0.22, -0.158], white_eye)
    add_box(vertices, [-0.10, 0.15, -0.168], [-0.04, 0.21, -0.162], dark_eye)
    add_box(vertices, [ 0.03, 0.14, -0.165], [ 0.13, 0.22, -0.158], white_eye)
    add_box(vertices, [ 0.04, 0.15, -0.168], [ 0.10, 0.21, -0.162], dark_eye)
    # Severe angled eyebrows
    add_box(vertices, [-0.14, 0.22, -0.17], [-0.02, 0.26, -0.158], [0.12, 0.08, 0.10])
    add_box(vertices, [ 0.02, 0.22, -0.17], [ 0.14, 0.26, -0.158], [0.12, 0.08, 0.10])
    # Lips
    add_box(vertices, [-0.05, 0.05, -0.168], [0.05, 0.09, -0.158], red_lip)

    if world_idx == 0:
        # Lady Tremaine: Towering sculpted silver pompadour updo
        add_box(vertices, [-0.19, 0.26, -0.18], [0.19, 0.62, 0.19], hr)
        add_box(vertices, [-0.14, 0.60, -0.14], [0.14, 0.70, 0.14], [0.80, 0.80, 0.84])

    elif world_idx == 1:
        # Evil Queen: Tight black balaclava hood & tall 5-point golden queen crown
        add_box(vertices, [-0.18, 0.14, -0.18], [0.18, 0.35, 0.18], [0.10, 0.08, 0.12])
        # Pointed high golden crown
        add_box(vertices, [-0.19, 0.32, -0.18], [0.19, 0.44, 0.18], gold)
        # Crown spires
        for sx in [-0.16, -0.08, 0.0, 0.08, 0.16]:
            add_box(vertices, [sx - 0.02, 0.42, -0.19], [sx + 0.02, 0.58, -0.16], gold)

    elif world_idx == 2:
        # Jafar: Towering black mitre sultan hat with large oval ruby brooch & gold plume
        add_box(vertices, [-0.18, 0.20, -0.16], [0.18, 0.65, 0.18], [0.08, 0.06, 0.08])
        add_box(vertices, [-0.05, 0.38, -0.19], [0.05, 0.48, -0.15], [0.85, 0.12, 0.15]) # Ruby
        add_box(vertices, [-0.02, 0.46, -0.19], [0.02, 0.72, -0.16], gold) # Feather

    elif world_idx == 3:
        # Mother Gothel: Giant mane of voluminous curly black hair cascading over shoulders
        add_box(vertices, [-0.22, 0.16, -0.16], [0.22, 0.38, 0.22], hr)
        add_box(vertices, [-0.25, -0.15, -0.10], [-0.16, 0.22, 0.20], hr)
        add_box(vertices, [ 0.16, -0.15, -0.10], [ 0.25, 0.22, 0.20], hr)

    elif world_idx == 4:
        # Scar: Lion face with sinister black mane, beard & iconic vertical scar over left eye
        add_box(vertices, [-0.20, 0.12, -0.16], [0.20, 0.42, 0.20], hr)
        # Ear tufts
        add_box(vertices, [-0.22, 0.34, -0.04], [-0.14, 0.46, 0.06], hr)
        add_box(vertices, [ 0.14, 0.34, -0.04], [ 0.22, 0.46, 0.06], hr)
        # Sinister eye scar (vertical line crossing left eye)
        add_box(vertices, [-0.11, 0.08, -0.17], [-0.09, 0.28, -0.16], [0.45, 0.20, 0.20])

    elif world_idx == 5:
        # Ursula: Wild shock of gravity-defying white/grey sea-witch hair & beauty mark
        add_box(vertices, [-0.20, 0.22, -0.18], [0.20, 0.58, 0.20], hr)
        add_box(vertices, [-0.14, 0.55, -0.12], [0.14, 0.72, 0.14], hr)
        # Iconic beauty mark mole on right cheek
        add_box(vertices, [0.08, 0.08, -0.168], [0.10, 0.10, -0.162], [0.10, 0.08, 0.10])

    elif world_idx == 6:
        # Captain Hook: Long curling black mustache, cascading raven ringlets & cavalier hat with plume
        add_box(vertices, [-0.20, 0.14, -0.16], [0.20, 0.36, 0.20], hr)
        # Iconic curling handlebar mustache
        add_box(vertices, [-0.14, 0.08, -0.175], [0.14, 0.12, -0.16], [0.10, 0.08, 0.10])
        add_box(vertices, [-0.16, 0.12, -0.175], [-0.12, 0.16, -0.16], [0.10, 0.08, 0.10])
        add_box(vertices, [ 0.12, 0.12, -0.175], [ 0.16, 0.16, -0.16], [0.10, 0.08, 0.10])
        # Wide brim cavalier hat with purple plume
        add_box(vertices, [-0.26, 0.30, -0.22], [0.26, 0.38, 0.24], [0.70, 0.12, 0.15])
        add_box(vertices, [-0.16, 0.36, -0.14], [0.16, 0.48, 0.16], [0.70, 0.12, 0.15])
        add_box(vertices, [-0.14, 0.44, -0.06], [-0.08, 0.68, 0.22], [0.95, 0.95, 0.98]) # White/purple plume

    else:
        # Prince Hans: Auburn sideburns, combed side-parted hair
        add_box(vertices, [-0.18, 0.18, -0.16], [0.18, 0.38, 0.19], hr)
        # Mutton chop sideburns down cheeks
        add_box(vertices, [-0.18, 0.06, -0.12], [-0.14, 0.22, 0.04], hr)
        add_box(vertices, [ 0.14, 0.06, -0.12], [ 0.18, 0.22, 0.04], hr)

    return _mesh(vertices)


# =============================================================================
# 4. VILLAIN ARMS FACTORY (SPECIAL WEAPONS / ACCESSORIES LIKE HOOK'S HOOK)
# =============================================================================

def create_villain_arms(world_idx: int, world_config) -> Tuple[Mesh, Mesh]:
    gw = list(world_config.villain_gown)
    sk = list(world_config.villain_skin)
    black = [0.10, 0.08, 0.12]
    gold = [0.95, 0.82, 0.22]

    # Right arm (grasping predator hand)
    vr = []
    add_box(vr, [-0.07, -0.38, -0.07], [0.07, 0.0,  0.07], gw)
    add_box(vr, [-0.075, -0.44, -0.075], [0.075, -0.38, 0.075], black)
    add_box(vr, [-0.06, -0.62, -0.12], [0.06, -0.44, 0.06], sk) # Grasping hand
    # Evil long claw fingernails
    add_box(vr, [-0.04, -0.66, -0.14], [0.04, -0.60, -0.10], [0.80, 0.15, 0.20])

    # Left arm
    vl = []
    if world_idx == 6:
        # Captain Hook: LEFT ARM TERMINATES IN A GLEAMING STEEL HOOK!
        silver_steel = [0.88, 0.90, 0.94]
        add_box(vl, [-0.07, -0.38, -0.07], [0.07, 0.0, 0.07], [0.72, 0.10, 0.15]) # Crimson sleeve
        add_box(vl, [-0.08, -0.44, -0.08], [0.08, -0.38, 0.08], gold) # Gold cuff
        add_box(vl, [-0.05, -0.52, -0.05], [0.05, -0.44, 0.05], silver_steel) # Hook base
        # Curved hook shank and sharp curved point facing forward (-Z)
        add_box(vl, [-0.02, -0.62, -0.03], [0.02, -0.52, 0.03], silver_steel)
        add_box(vl, [-0.02, -0.64, -0.15], [0.02, -0.58, -0.02], silver_steel)
        add_box(vl, [-0.02, -0.54, -0.17], [0.02, -0.50, -0.12], silver_steel) # Sharp tip
    elif world_idx == 2:
        # Jafar: Holds coiled golden cobra serpent staff
        add_box(vl, [-0.07, -0.38, -0.07], [0.07, 0.0, 0.07], gw)
        add_box(vl, [-0.06, -0.62, -0.06], [0.06, -0.38, 0.06], sk)
        # Golden cobra staff running through hand
        add_box(vl, [-0.03, -0.90, -0.08], [0.03, 0.35, -0.04], gold)
        add_box(vl, [-0.06, 0.30, -0.14], [0.06, 0.44, -0.04], [0.85, 0.12, 0.15]) # Cobra hood
    else:
        add_box(vl, [-0.07, -0.38, -0.07], [0.07, 0.0, 0.07], gw)
        add_box(vl, [-0.075, -0.44, -0.075], [0.075, -0.38, 0.075], black)
        add_box(vl, [-0.06, -0.62, -0.12], [0.06, -0.44, 0.06], sk)
        add_box(vl, [-0.04, -0.66, -0.14], [0.04, -0.60, -0.10], [0.80, 0.15, 0.20])

    return _mesh(vl), _mesh(vr)


# =============================================================================
# 5. ANIMATION & CHASER CONTROLLER
# =============================================================================

class VillainAnimation:
    """Independent procedural animation controller for the villain."""

    def __init__(self):
        self.stride_phase = 0.0
        self.cadence = 3.4
        self.arm_l_pitch = 0.0
        self.arm_r_pitch = 0.0
        self.torso_pitch = 0.0
        self.torso_bob_y = 0.0
        self.skirt_sway  = 0.0

    def update(self, delta_time: float, proximity_ratio: float) -> None:
        if delta_time <= 0.0:
            return
        step_rate = self.cadence * (1.0 + 0.35 * proximity_ratio)
        self.stride_phase = (self.stride_phase + step_rate * 2.0 * np.pi * delta_time) % (2.0 * np.pi)
        swing = np.sin(self.stride_phase)
        base_reach  = -35.0 - (40.0 * proximity_ratio)
        arm_pumping = swing * (22.0 + 15.0 * proximity_ratio)
        self.arm_l_pitch = base_reach + arm_pumping
        self.arm_r_pitch = base_reach - arm_pumping
        self.torso_pitch = 12.0 + (14.0 * proximity_ratio)
        self.torso_bob_y = abs(swing) * 0.06
        self.skirt_sway  = swing * 4.0


class Villain:
    """World-aware 3D Humanoid Chaser Entity supporting 8 unique Disney Villains."""

    def __init__(self):
        self.x = settings.VILLAIN_LATERAL_OFFSET
        self.y = 0.0
        self.z = settings.VILLAIN_START_DISTANCE
        self.animation = VillainAnimation()
        self.world_index = 0

        from worlds.world_config import get_world
        self._build_for_world(0, get_world(0))

    def _build_for_world(self, world_idx: int, world_config) -> None:
        self.world_index = world_idx
        self.mesh_gown  = create_villain_skirt_mesh(world_idx, world_config)
        self.mesh_torso = create_villain_torso_mesh(world_idx, world_config)
        self.mesh_head  = create_villain_head_mesh(world_idx, world_config)
        self.mesh_arm_left, self.mesh_arm_right = create_villain_arms(world_idx, world_config)

    def _delete_meshes(self) -> None:
        for attr in ("mesh_gown", "mesh_torso", "mesh_head", "mesh_arm_left", "mesh_arm_right"):
            m = getattr(self, attr, None)
            if m is not None:
                m.delete()
                setattr(self, attr, None)

    def apply_world_config(self, world_config) -> None:
        """Morphs the villain to match the new world antagonist."""
        self._delete_meshes()
        self._build_for_world(world_config.index, world_config)
        print(f"[VILLAIN] Re-designed as {world_config.villain_name} with unique 3D antagonist geometry")

    def update(
        self,
        player_x: float,
        player_z: float,
        chase_distance: float,
        proximity_ratio: float,
        delta_time: float
    ) -> None:
        if player_x > 1.0:
            target_x = player_x - settings.VILLAIN_LATERAL_OFFSET
        else:
            target_x = player_x + settings.VILLAIN_LATERAL_OFFSET

        decay = 1.0 - np.exp(-settings.VILLAIN_LATERAL_FOLLOW_SPEED * delta_time)
        self.x += (target_x - self.x) * decay
        self.z  = player_z + chase_distance
        self.y  = 0.0
        self.animation.update(delta_time, proximity_ratio)

    def render(self, renderer: Renderer, shader: ShaderProgram, camera: Camera) -> None:
        px, py, pz = self.x, self.y, self.z

        # 1. Gown / Skirt
        gown_t = pyrr.Matrix44.from_translation([px, py, pz])
        gown_r = pyrr.Matrix44.from_z_rotation(np.radians(self.animation.skirt_sway))
        gown_matrix = gown_t * gown_r
        if self.mesh_gown:
            renderer.render(self.mesh_gown, shader, gown_matrix, camera)

        # 2. Torso
        torso_y = 0.85 + self.animation.torso_bob_y
        torso_t = pyrr.Matrix44.from_translation([px, py + torso_y, pz])
        torso_r = pyrr.Matrix44.from_x_rotation(np.radians(self.animation.torso_pitch))
        torso_matrix = torso_t * torso_r
        if self.mesh_torso:
            renderer.render(self.mesh_torso, shader, torso_matrix, camera)

        # 3. Head
        head_local = pyrr.Matrix44.from_translation([0.0, 0.65, 0.0])
        head_matrix = torso_matrix * head_local
        if self.mesh_head:
            renderer.render(self.mesh_head, shader, head_matrix, camera)

        # 4. Left Arm
        shoulder_l = pyrr.Matrix44.from_translation([-0.32, 0.58, 0.0])
        arm_l_r    = pyrr.Matrix44.from_x_rotation(np.radians(self.animation.arm_l_pitch))
        arm_l_matrix = torso_matrix * shoulder_l * arm_l_r
        if self.mesh_arm_left:
            renderer.render(self.mesh_arm_left, shader, arm_l_matrix, camera)

        # 5. Right Arm
        shoulder_r = pyrr.Matrix44.from_translation([0.32, 0.58, 0.0])
        arm_r_r    = pyrr.Matrix44.from_x_rotation(np.radians(self.animation.arm_r_pitch))
        arm_r_matrix = torso_matrix * shoulder_r * arm_r_r
        if self.mesh_arm_right:
            renderer.render(self.mesh_arm_right, shader, arm_r_matrix, camera)

    def delete(self) -> None:
        self._delete_meshes()
