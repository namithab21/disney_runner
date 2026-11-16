"""
camera.py - 3D Camera system with View and Perspective Projection management.
"""

import numpy as np
import pyrr
from config import settings


class Camera:
    """Manages 3D view and projection matrices using Pyrr with smooth third-person follow."""

    def __init__(
        self,
        position: list[float] | np.ndarray = None,
        target: list[float] | np.ndarray = None,
        up: list[float] | np.ndarray = None,
        fov: float = settings.DEFAULT_FOV,
        aspect_ratio: float = settings.WINDOW_WIDTH / settings.WINDOW_HEIGHT,
        near: float = settings.NEAR_CLIP,
        far: float = settings.FAR_CLIP,
        offset: list[float] | np.ndarray = None,
        smooth_speed: float = settings.CAMERA_SMOOTH_SPEED
    ):
        self.position = np.array(position if position is not None else settings.CAMERA_POS, dtype=np.float32)
        self.target = np.array(target if target is not None else settings.CAMERA_TARGET, dtype=np.float32)
        self.up = np.array(up if up is not None else settings.CAMERA_UP, dtype=np.float32)

        self.offset = np.array(offset if offset is not None else settings.CAMERA_OFFSET, dtype=np.float32)
        self.smooth_speed = smooth_speed

        self.fov = fov
        self.aspect_ratio = aspect_ratio
        self.near = near
        self.far = far

        self._projection_matrix: pyrr.Matrix44 = None
        self._update_projection()

    def _update_projection(self) -> None:
        """Recalculates the perspective projection matrix."""
        self._projection_matrix = pyrr.Matrix44.perspective_projection(
            self.fov,
            self.aspect_ratio,
            self.near,
            self.far
        )

    def set_aspect_ratio(self, width: int, height: int) -> None:
        """Updates aspect ratio and recalculates projection matrix upon window resize."""
        if height <= 0:
            height = 1
        self.aspect_ratio = float(width) / float(height)
        self._update_projection()

    def follow(self, target_pos: list[float] | np.ndarray, delta_time: float) -> None:
        """
        Smoothly follows a target position (e.g., player position) using exponential damping
        to avoid sudden camera movements. Follows jumping movement subtly.
        """
        target_pos_arr = np.array(target_pos, dtype=np.float32)
        
        # Subtly follow jumping movement without sudden camera jumps
        subtle_jump_y = target_pos_arr[1] * 0.35
        desired_pos = np.array([
            target_pos_arr[0] + self.offset[0],
            self.offset[1] + subtle_jump_y,
            target_pos_arr[2] + self.offset[2]
        ], dtype=np.float32)

        desired_target = np.array([
            target_pos_arr[0] * 0.4,  # Slight lateral damping for camera look-at
            1.2 + (target_pos_arr[1] * 0.20),
            target_pos_arr[2] - settings.CAMERA_LOOK_AHEAD
        ], dtype=np.float32)

        if delta_time > 0.0:
            # Exponential decay factor for frame-rate-independent smoothing
            factor = min(1.0, 1.0 - np.exp(-self.smooth_speed * delta_time))
            self.position += (desired_pos - self.position) * factor
            self.target += (desired_target - self.target) * factor
        else:
            self.position = desired_pos
            self.target = desired_target

    def get_view_matrix(self) -> pyrr.Matrix44:
        """Computes the view matrix looking from position towards target."""
        return pyrr.Matrix44.look_at(self.position, self.target, self.up)

    def get_projection_matrix(self) -> pyrr.Matrix44:
        """Returns the current perspective projection matrix."""
        return self._projection_matrix
