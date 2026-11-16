"""
window.py - GLFW Window Lifecycle and OpenGL Context Manager.
Encapsulates window creation, resize callbacks, frame delta timing, and input polling.
"""

from typing import Callable, Optional
import glfw
from OpenGL.GL import glViewport
from config import settings


class Window:
    """Manages GLFW window lifecycle, context initialization, and input events."""

    def __init__(
        self,
        width: int = settings.WINDOW_WIDTH,
        height: int = settings.WINDOW_HEIGHT,
        title: str = settings.WINDOW_TITLE,
        vsync: bool = settings.VSYNC
    ):
        self.width = width
        self.height = height
        self.title = title
        self.vsync = vsync
        self.window = None

        self._last_frame_time = 0.0
        self.delta_time = 0.0

        # Resize callbacks registry
        self._resize_callbacks: list[Callable[[int, int], None]] = []

        self._init_glfw()

    def _init_glfw(self) -> None:
        """Initializes GLFW and creates a modern OpenGL 3.3 Core profile window."""
        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW library.")

        # Request modern OpenGL Core Profile
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, settings.OPENGL_MAJOR_VERSION)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, settings.OPENGL_MINOR_VERSION)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        if settings.OPENGL_FORWARD_COMPAT:
            glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
        glfw.window_hint(glfw.RESIZABLE, glfw.TRUE)

        # Create window
        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Failed to create GLFW window with OpenGL 3.3 Core Profile.")

        glfw.make_context_current(self.window)

        # Set swap interval (VSync)
        glfw.swap_interval(1 if self.vsync else 0)

        # Setup callbacks
        glfw.set_framebuffer_size_callback(self.window, self._framebuffer_size_callback)
        glfw.set_key_callback(self.window, self._key_callback)

        # Configure initial viewport
        fb_width, fb_height = glfw.get_framebuffer_size(self.window)
        glViewport(0, 0, fb_width, fb_height)

        self._last_frame_time = glfw.get_time()

    def add_resize_callback(self, callback: Callable[[int, int], None]) -> None:
        """Register a callback for window/framebuffer resize events."""
        self._resize_callbacks.append(callback)

    def _framebuffer_size_callback(self, window, width: int, height: int) -> None:
        """Internal callback invoked by GLFW when window dimensions change."""
        if width > 0 and height > 0:
            self.width = width
            self.height = height
            glViewport(0, 0, width, height)
            for callback in self._resize_callbacks:
                callback(width, height)

    def _key_callback(self, window, key: int, scancode: int, action: int, mods: int) -> None:
        """Default key handler: ESC to close window."""
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window, True)

    def update_delta_time(self) -> float:
        """Calculates elapsed time between consecutive frames in seconds."""
        current_time = glfw.get_time()
        self.delta_time = current_time - self._last_frame_time
        self._last_frame_time = current_time
        return self.delta_time

    def should_close(self) -> bool:
        """Checks if the window has been instructed to close."""
        return glfw.window_should_close(self.window)

    def swap_buffers(self) -> None:
        """Swaps front and back buffers."""
        glfw.swap_buffers(self.window)

    def poll_events(self) -> None:
        """Polls for system and input events."""
        glfw.poll_events()

    def get_time(self) -> float:
        """Returns total elapsed time since GLFW init."""
        return glfw.get_time()

    def close(self) -> None:
        """Closes and cleans up GLFW window resources."""
        if self.window:
            glfw.destroy_window(self.window)
            self.window = None
        glfw.terminate()
