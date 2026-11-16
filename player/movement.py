"""
movement.py - Player Movement Controller and Physics System.
Manages three-lane horizontal positioning, vertical jump trajectories with gravity,
and sliding mechanics with collision height reduction.
"""

from typing import Tuple
import numpy as np
from config import settings

STATE_RUNNING = "running"
STATE_JUMPING = "jumping"
STATE_SLIDING = "sliding"


class PlayerMovement:
    """Handles lane switching, jump gravity physics, and sliding states."""

    def __init__(self):
        # Lane indices: -1 = Left (-2.4), 0 = Center (0.0), 1 = Right (+2.4)
        self.current_lane = settings.PLAYER_START_LANE
        self.lane_width = settings.LANE_WIDTH

        # 3D Coordinates
        self.x = self.current_lane * self.lane_width
        self.target_x = self.x
        self.y = 0.0
        self.z = 0.0

        # Physical velocities
        self.velocity_y = 0.0
        self.lateral_velocity = 0.0

        # State tracking
        self.is_grounded = True
        self.state = STATE_RUNNING
        self.slide_timer = 0.0
        self.pending_slide_on_land = False

    def move_left(self) -> bool:
        """
        Initiates a single-lane move to the left.
        Clamped to the leftmost lane (-1).
        Returns True if lane changed, False if already at leftmost lane.
        """
        if self.current_lane > -1:
            self.current_lane -= 1
            self.target_x = self.current_lane * self.lane_width
            return True
        return False

    def move_right(self) -> bool:
        """
        Initiates a single-lane move to the right.
        Clamped to the rightmost lane (+1).
        Returns True if lane changed, False if already at rightmost lane.
        """
        if self.current_lane < 1:
            self.current_lane += 1
            self.target_x = self.current_lane * self.lane_width
            return True
        return False

    def jump(self) -> bool:
        """
        Initiates a vertical jump if grounded.
        Returns True if jump successfully triggered.
        """
        if self.is_grounded:
            # If sliding, cancel slide and launch into jump
            self.slide_timer = 0.0
            self.pending_slide_on_land = False
            self.velocity_y = settings.PLAYER_JUMP_VELOCITY
            self.is_grounded = False
            self.state = STATE_JUMPING
            return True
        return False

    def slide(self) -> bool:
        """
        Initiates a slide action.
        If airborne, performs an immediate fast downward dive to ground,
        then enters slide upon landing.
        If grounded and not already sliding, enters slide.
        """
        if not self.is_grounded:
            # Fast aerial downward dive into slide
            self.velocity_y = settings.PLAYER_SLIDE_FAST_DROP
            self.pending_slide_on_land = True
            return True

        if self.state != STATE_SLIDING:
            self.state = STATE_SLIDING
            self.slide_timer = settings.PLAYER_SLIDE_DURATION
            return True

        return False

    def update(self, delta_time: float) -> None:
        """Updates lateral interpolation, vertical jump physics, and slide duration."""
        if delta_time <= 0.0:
            return

        # -------------------------------------------------------------
        # 1. Lateral (X) Lane Movement with Smooth Exponential Damping
        # -------------------------------------------------------------
        prev_x = self.x
        diff_x = self.target_x - self.x

        if abs(diff_x) > 1e-4:
            decay_factor = 1.0 - np.exp(-settings.PLAYER_LANE_CHANGE_SPEED * delta_time)
            self.x += diff_x * decay_factor
            if abs(self.target_x - self.x) < 0.005:
                self.x = self.target_x
        else:
            self.x = self.target_x

        self.lateral_velocity = (self.x - prev_x) / delta_time

        # -------------------------------------------------------------
        # 2. Vertical (Y) Physics: Gravity and Ground Collision
        # -------------------------------------------------------------
        if not self.is_grounded or self.velocity_y != 0.0:
            self.velocity_y += settings.PLAYER_GRAVITY * delta_time
            self.y += self.velocity_y * delta_time

            # Ground collision check
            if self.y <= 0.0:
                self.y = 0.0
                self.velocity_y = 0.0
                self.is_grounded = True

                if self.pending_slide_on_land:
                    self.pending_slide_on_land = False
                    self.state = STATE_SLIDING
                    self.slide_timer = settings.PLAYER_SLIDE_DURATION
                elif self.state == STATE_JUMPING:
                    self.state = STATE_RUNNING

        # -------------------------------------------------------------
        # 3. Slide Timer Countdown
        # -------------------------------------------------------------
        if self.state == STATE_SLIDING:
            self.slide_timer -= delta_time
            if self.slide_timer <= 0.0:
                self.slide_timer = 0.0
                self.state = STATE_RUNNING

    @property
    def position(self) -> np.ndarray:
        """Returns [x, y, z] as a numpy array."""
        return np.array([self.x, self.y, self.z], dtype=np.float32)

    @property
    def is_jumping(self) -> bool:
        return self.state == STATE_JUMPING

    @property
    def is_sliding(self) -> bool:
        return self.state == STATE_SLIDING

    @property
    def current_height(self) -> float:
        """Returns active collision height depending on whether player is sliding."""
        if self.state == STATE_SLIDING:
            return settings.PLAYER_HEIGHT_SLIDING
        return settings.PLAYER_HEIGHT_STANDING

    def get_bounding_box(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Returns axis-aligned bounding box (min_corner, max_corner)
        taking current position and height into account.
        """
        hw = settings.PLAYER_WIDTH / 2.0
        hd = settings.PLAYER_DEPTH / 2.0
        h = self.current_height

        min_pt = np.array([self.x - hw, self.y, self.z - hd], dtype=np.float32)
        max_pt = np.array([self.x + hw, self.y + h, self.z + hd], dtype=np.float32)
        return min_pt, max_pt
