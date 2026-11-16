"""
cube.py - 3D Cube Mesh Generator and Entity.
Defines 3D cube geometry with distinct colored faces and surface normals.
"""

import numpy as np
import pyrr
from engine.mesh import Mesh, VertexAttribute
from engine.shader import ShaderProgram
from engine.camera import Camera
from engine.renderer import Renderer


def create_cube_mesh() -> Mesh:
    """
    Creates a unit cube mesh centered at the origin (-0.5 to +0.5).
    Each of the 6 faces features distinct Disney story colors and explicit normal vectors.
    Layout per vertex: [Position (3), Color (3), Normal (3)] - total 9 floats.
    """
    # Vertex layout definition:
    # [Px, Py, Pz,  R, G, B,  Nx, Ny, Nz]
    vertices = np.array([
        # --- Front Face (+Z) : Cinderella Glass Slipper Blue ---
        -0.5, -0.5,  0.5,   0.20, 0.60, 0.95,   0.0,  0.0,  1.0,
         0.5, -0.5,  0.5,   0.20, 0.60, 0.95,   0.0,  0.0,  1.0,
         0.5,  0.5,  0.5,   0.20, 0.60, 0.95,   0.0,  0.0,  1.0,
         0.5,  0.5,  0.5,   0.20, 0.60, 0.95,   0.0,  0.0,  1.0,
        -0.5,  0.5,  0.5,   0.20, 0.60, 0.95,   0.0,  0.0,  1.0,
        -0.5, -0.5,  0.5,   0.20, 0.60, 0.95,   0.0,  0.0,  1.0,

        # --- Back Face (-Z) : Snow White Poison Apple Crimson ---
         0.5, -0.5, -0.5,   0.90, 0.22, 0.25,   0.0,  0.0, -1.0,
        -0.5, -0.5, -0.5,   0.90, 0.22, 0.25,   0.0,  0.0, -1.0,
        -0.5,  0.5, -0.5,   0.90, 0.22, 0.25,   0.0,  0.0, -1.0,
        -0.5,  0.5, -0.5,   0.90, 0.22, 0.25,   0.0,  0.0, -1.0,
         0.5,  0.5, -0.5,   0.90, 0.22, 0.25,   0.0,  0.0, -1.0,
         0.5, -0.5, -0.5,   0.90, 0.22, 0.25,   0.0,  0.0, -1.0,

        # --- Top Face (+Y) : Aladdin Magic Lamp Gold ---
        -0.5,  0.5,  0.5,   0.98, 0.82, 0.20,   0.0,  1.0,  0.0,
         0.5,  0.5,  0.5,   0.98, 0.82, 0.20,   0.0,  1.0,  0.0,
         0.5,  0.5, -0.5,   0.98, 0.82, 0.20,   0.0,  1.0,  0.0,
         0.5,  0.5, -0.5,   0.98, 0.82, 0.20,   0.0,  1.0,  0.0,
        -0.5,  0.5, -0.5,   0.98, 0.82, 0.20,   0.0,  1.0,  0.0,
        -0.5,  0.5,  0.5,   0.98, 0.82, 0.20,   0.0,  1.0,  0.0,

        # --- Bottom Face (-Y) : Peter Pan Neverland Emerald ---
        -0.5, -0.5, -0.5,   0.15, 0.75, 0.42,   0.0, -1.0,  0.0,
         0.5, -0.5, -0.5,   0.15, 0.75, 0.42,   0.0, -1.0,  0.0,
         0.5, -0.5,  0.5,   0.15, 0.75, 0.42,   0.0, -1.0,  0.0,
         0.5, -0.5,  0.5,   0.15, 0.75, 0.42,   0.0, -1.0,  0.0,
        -0.5, -0.5,  0.5,   0.15, 0.75, 0.42,   0.0, -1.0,  0.0,
        -0.5, -0.5, -0.5,   0.15, 0.75, 0.42,   0.0, -1.0,  0.0,

        # --- Right Face (+X) : Tangled Rapunzel Royal Violet ---
         0.5, -0.5,  0.5,   0.68, 0.28, 0.88,   1.0,  0.0,  0.0,
         0.5, -0.5, -0.5,   0.68, 0.28, 0.88,   1.0,  0.0,  0.0,
         0.5,  0.5, -0.5,   0.68, 0.28, 0.88,   1.0,  0.0,  0.0,
         0.5,  0.5, -0.5,   0.68, 0.28, 0.88,   1.0,  0.0,  0.0,
         0.5,  0.5,  0.5,   0.68, 0.28, 0.88,   1.0,  0.0,  0.0,
         0.5, -0.5,  0.5,   0.68, 0.28, 0.88,   1.0,  0.0,  0.0,

        # --- Left Face (-X) : Little Mermaid Ariel Lagoon Turquoise ---
        -0.5, -0.5, -0.5,   0.12, 0.82, 0.85,  -1.0,  0.0,  0.0,
        -0.5, -0.5,  0.5,   0.12, 0.82, 0.85,  -1.0,  0.0,  0.0,
        -0.5,  0.5,  0.5,   0.12, 0.82, 0.85,  -1.0,  0.0,  0.0,
        -0.5,  0.5,  0.5,   0.12, 0.82, 0.85,  -1.0,  0.0,  0.0,
        -0.5,  0.5, -0.5,   0.12, 0.82, 0.85,  -1.0,  0.0,  0.0,
        -0.5, -0.5, -0.5,   0.12, 0.82, 0.85,  -1.0,  0.0,  0.0,
    ], dtype=np.float32)

    attributes = [
        VertexAttribute(location=0, size=3),  # aPos (vec3)
        VertexAttribute(location=1, size=3),  # aColor (vec3)
        VertexAttribute(location=2, size=3),  # aNormal (vec3)
    ]

    return Mesh(vertices=vertices, attributes=attributes)


class CubeEntity:
    """A 3D Cube Entity with position, rotation, scaling, and animation logic."""

    def __init__(
        self,
        position: list[float] | None = None,
        rotation: list[float] | None = None,
        scale: list[float] | None = None,
        rot_speed_y: float = 45.0,
        rot_speed_x: float = 25.0
    ):
        self.position = np.array(position if position is not None else [0.0, 0.0, 0.0], dtype=np.float32)
        self.rotation = np.array(rotation if rotation is not None else [0.0, 0.0, 0.0], dtype=np.float32)
        self.scale = np.array(scale if scale is not None else [1.5, 1.5, 1.5], dtype=np.float32)

        self.rot_speed_y = rot_speed_y
        self.rot_speed_x = rot_speed_x

        self.mesh = create_cube_mesh()

    def update(self, delta_time: float) -> None:
        """Updates cube rotation angles based on frame delta time."""
        self.rotation[1] += self.rot_speed_y * delta_time
        self.rotation[0] += self.rot_speed_x * delta_time

        # Keep rotation angles bounded within [0, 360)
        self.rotation[1] %= 360.0
        self.rotation[0] %= 360.0

    def get_model_matrix(self) -> pyrr.Matrix44:
        """Computes the 4x4 Model Transformation Matrix (T * R * S)."""
        t = pyrr.Matrix44.from_translation(self.position)
        r_y = pyrr.Matrix44.from_y_rotation(np.radians(self.rotation[1]))
        r_x = pyrr.Matrix44.from_x_rotation(np.radians(self.rotation[0]))
        r_z = pyrr.Matrix44.from_z_rotation(np.radians(self.rotation[2]))
        s = pyrr.Matrix44.from_scale(self.scale)

        # Transformation order: Scale -> Rotate Z -> Rotate X -> Rotate Y -> Translate
        rotation = r_y * r_x * r_z
        model = t * rotation * s
        return model

    def render(self, renderer: Renderer, shader: ShaderProgram, camera: Camera) -> None:
        """Issues the render call to the renderer."""
        renderer.render(
            mesh=self.mesh,
            shader=shader,
            model_matrix=self.get_model_matrix(),
            camera=camera
        )

    def delete(self) -> None:
        """Releases underlying GPU mesh resources."""
        if self.mesh:
            self.mesh.delete()
            self.mesh = None
