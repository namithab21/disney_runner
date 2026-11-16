"""
transition.py - Seamless Disney World Transition System.
Manages a short 2-second crossfade between worlds:
  - Blends sky and environment colours.
  - Displays world-introduction title banner.
  - Coordinates the moment to advance the world (at mid-transition).
"""

from typing import Optional, Tuple
from worlds.world_config import WorldConfig


# Transition duration in seconds
TRANSITION_DURATION = 2.0

# Fraction of duration at which the actual world switch fires (mid-point)
WORLD_SWITCH_POINT = 0.50


class WorldTransition:
    """
    Drives the visual crossfade and title-card animation between worlds.

    States:
      IDLE       — no transition in progress.
      FADING_OUT — environment blending from old → new (first half).
      FADING_IN  — environment settling to new palette (second half).
    """

    STATE_IDLE = "idle"
    STATE_FADING_OUT = "fading_out"
    STATE_FADING_IN = "fading_in"

    def __init__(self):
        self.state: str = self.STATE_IDLE
        self.progress: float = 0.0        # 0.0 → 1.0 over TRANSITION_DURATION
        self.duration: float = TRANSITION_DURATION

        self.from_world: Optional[WorldConfig] = None
        self.to_world: Optional[WorldConfig] = None

        # Set True at WORLD_SWITCH_POINT (single-frame flag)
        self.world_switched: bool = False

        # Controls banner display (shows during the first ~60% of transition)
        self.show_banner: bool = False
        self.banner_alpha: float = 0.0    # 0.0–1.0 for HUD fade
        self.title_text: str = ""
        self.subtitle_text: str = ""

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------

    @property
    def is_active(self) -> bool:
        return self.state != self.STATE_IDLE

    @property
    def blend_alpha(self) -> float:
        """
        Returns how far along the new palette should be blended in (0→1).
        0.0 = fully old world, 1.0 = fully new world.
        """
        if self.state == self.STATE_IDLE:
            return 1.0
        # First half: 0.0 → 1.0 linearly
        if self.progress <= WORLD_SWITCH_POINT:
            return self.progress / WORLD_SWITCH_POINT
        # Second half stays at 1.0
        return 1.0

    @property
    def screen_flash_alpha(self) -> float:
        """
        Brief white flash at the switch point (peak of 0.5 for 2 frames).
        Used by HUD to draw a white rect at low opacity.
        """
        switch_window = 0.08  # Fraction of total duration for flash
        rel = abs(self.progress - WORLD_SWITCH_POINT)
        if rel < switch_window:
            return max(0.0, 1.0 - rel / switch_window) * 0.45
        return 0.0

    # -------------------------------------------------------------------------
    # Control
    # -------------------------------------------------------------------------

    def start(self, from_world: WorldConfig, to_world: WorldConfig, duration: float = TRANSITION_DURATION) -> None:
        """Begin a transition from from_world to to_world."""
        self.from_world = from_world
        self.to_world = to_world
        self.progress = 0.0
        self.duration = duration
        self.state = self.STATE_FADING_OUT
        self.world_switched = False
        self.show_banner = True
        self.banner_alpha = 0.0
        self.title_text = to_world.name.upper()
        self.subtitle_text = to_world.subtitle
        print(f"[TRANSITION] Starting: {from_world.name} → {to_world.name}")

    def update(self, delta_time: float) -> bool:
        """
        Advances transition. Returns True at the exact frame the world switches.
        Call WorldManager.advance_world() when this returns True.
        """
        if self.state == self.STATE_IDLE:
            return False

        self.world_switched = False
        self.progress += delta_time / self.duration

        # Banner alpha: fade in quickly, hold, then fade out near end
        if self.progress < 0.20:
            self.banner_alpha = self.progress / 0.20
        elif self.progress < 0.70:
            self.banner_alpha = 1.0
        elif self.progress < 0.90:
            self.banner_alpha = 1.0 - (self.progress - 0.70) / 0.20
        else:
            self.banner_alpha = 0.0
            self.show_banner = False

        # Fire the world-switch at the mid-point (once only)
        prev_before = (self.progress - delta_time / self.duration) < WORLD_SWITCH_POINT
        now_at_or_past = self.progress >= WORLD_SWITCH_POINT
        if prev_before and now_at_or_past:
            self.world_switched = True
            self.state = self.STATE_FADING_IN

        # Complete transition
        if self.progress >= 1.0:
            self.progress = 1.0
            self.state = self.STATE_IDLE
            self.show_banner = False
            self.banner_alpha = 0.0

        return self.world_switched

    def get_blended_sky(self) -> Tuple[float, float, float, float]:
        """Returns the linearly interpolated sky color during transition."""
        if not self.is_active or self.from_world is None or self.to_world is None:
            if self.to_world:
                return self.to_world.sky_color
            return (0.42, 0.65, 0.88, 1.0)

        alpha = self.blend_alpha
        fw = self.from_world.sky_color
        tw = self.to_world.sky_color
        return (
            fw[0] + (tw[0] - fw[0]) * alpha,
            fw[1] + (tw[1] - fw[1]) * alpha,
            fw[2] + (tw[2] - fw[2]) * alpha,
            1.0
        )

    def get_blended_fog(self) -> Tuple[float, float, float]:
        """Returns linearly interpolated fog color."""
        if not self.is_active or self.from_world is None or self.to_world is None:
            if self.to_world:
                return self.to_world.fog_color
            return (0.42, 0.65, 0.88)

        alpha = self.blend_alpha
        fw = self.from_world.fog_color
        tw = self.to_world.fog_color
        return (
            fw[0] + (tw[0] - fw[0]) * alpha,
            fw[1] + (tw[1] - fw[1]) * alpha,
            fw[2] + (tw[2] - fw[2]) * alpha,
        )

    def get_blended_light(self) -> Tuple[float, float, float]:
        """Returns linearly interpolated light color."""
        if not self.is_active or self.from_world is None or self.to_world is None:
            if self.to_world:
                return self.to_world.light_color
            return (1.0, 0.98, 0.92)

        alpha = self.blend_alpha
        fw = self.from_world.light_color
        tw = self.to_world.light_color
        return (
            fw[0] + (tw[0] - fw[0]) * alpha,
            fw[1] + (tw[1] - fw[1]) * alpha,
            fw[2] + (tw[2] - fw[2]) * alpha,
        )

    def abort(self) -> None:
        """Cancel any active transition immediately."""
        self.state = self.STATE_IDLE
        self.progress = 1.0
        self.show_banner = False
        self.banner_alpha = 0.0
