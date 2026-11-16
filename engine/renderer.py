"""
renderer.py - Modern OpenGL Rendering Pipeline Manager.
Configures pipeline states (depth testing, clearing, culling) and coordinates drawing.
"""

from typing import Tuple
import logging
from OpenGL.GL import (
    glEnable, glDisable, glClearColor, glClear, glDepthFunc,
    glGetString, GL_DEPTH_TEST, GL_LESS, GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT, GL_VERSION, GL_RENDERER, GL_VENDOR,
    GL_SHADING_LANGUAGE_VERSION
)
import pyrr
from config import settings
from engine.shader import ShaderProgram
from engine.mesh import Mesh
from engine.camera import Camera

logger = logging.getLogger(__name__)


class Renderer:
    """Configures OpenGL rendering state and issues draw passes."""

    def __init__(self, clear_color: Tuple[float, float, float, float] = settings.CLEAR_COLOR):
        self.clear_color = clear_color
        self._init_gl_state()
        # Profiling counters
        self.draw_calls = 0
        self.total_vertices = 0
        self.last_frame_time = 0.0
        self.last_cpu_time = 0.0
        self.last_gpu_time = 0.0


    def _init_gl_state(self) -> None:
        """Enables depth testing and sets background clear color."""
        # Enable depth testing to correctly render 3D geometry
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        # Set default clear color
        glClearColor(*self.clear_color)

        # Query and log graphics driver details
        vendor = glGetString(GL_VENDOR).decode('utf-8')
        renderer = glGetString(GL_RENDERER).decode('utf-8')
        version = glGetString(GL_VERSION).decode('utf-8')
        glsl_version = glGetString(GL_SHADING_LANGUAGE_VERSION).decode('utf-8')

        print("=" * 60)
        print("OpenGL Context Initialized Successfully")
        print(f"Vendor:   {vendor}")
        print(f"Renderer: {renderer}")
        print(f"Version:  {version}")
        print(f"GLSL:     {glsl_version}")
        print("=" * 60)

    def set_clear_color(self, r: float, g: float, b: float, a: float = 1.0) -> None:
        """Sets the background clear color."""
        self.clear_color = (r, g, b, a)
        glClearColor(r, g, b, a)

    def clear(self) -> None:
        """Clears color and depth buffers for the upcoming frame."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def render(
        self,
        mesh: Mesh,
        shader: ShaderProgram,
        model_matrix: pyrr.Matrix44,
        camera: Camera,
        light_pos: list[float] | None = None,
        light_color: list[float] | None = None,
        fog_color: list[float] | None = None,
        fog_start: float | None = None,
        fog_end: float | None = None
    ) -> None:
        """Binds shader, updates MVP, lighting, and fog uniforms, and draws the mesh."""
        shader.use()

        # Upload transformation matrices
        shader.set_mat4("uModel", model_matrix)
        shader.set_mat4("uView", camera.get_view_matrix())
        shader.set_mat4("uProjection", camera.get_projection_matrix())

        # Upload lighting & eye uniforms
        if light_pos is None:
            light_pos = settings.SUN_LIGHT_POS
        if light_color is None:
            light_color = settings.SUN_LIGHT_COLOR

        shader.set_vec3("uLightPos", light_pos)
        shader.set_vec3("uLightColor", light_color)
        shader.set_vec3("uViewPos", camera.position)

        # Upload atmospheric distance fog uniforms
        if fog_color is None and hasattr(settings, "FOG_COLOR"):
            fog_color = settings.FOG_COLOR
        if fog_start is None and hasattr(settings, "FOG_START"):
            fog_start = settings.FOG_START
        if fog_end is None and hasattr(settings, "FOG_END"):
            fog_end = settings.FOG_END

        if fog_color is not None:
            shader.set_vec3("uFogColor", fog_color)
        if fog_start is not None:
            shader.set_float("uFogStart", fog_start)
        if fog_end is not None:
            shader.set_float("uFogEnd", fog_end)

        # Draw mesh geometry
        mesh.draw()

        shader.unbind()
