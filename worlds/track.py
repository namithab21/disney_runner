"""
track.py - Endless Track Manager.
Orchestrates seamless road segment generation, recycling, speed control,
and world-themed environment updates.
"""

from typing import List
from config import settings
from engine.shader import ShaderProgram
from engine.camera import Camera
from engine.renderer import Renderer
from worlds.road_segment import RoadSegment


class Track:
    """Manages continuous endless generation and recycling of three-lane road segments."""

    def __init__(
        self,
        num_segments: int = settings.NUM_SEGMENTS,
        segment_length: float = settings.SEGMENT_LENGTH,
        speed: float = settings.ROAD_SPEED
    ):
        self.num_segments = num_segments
        self.segment_length = segment_length
        self.speed = speed
        self.recycle_threshold = settings.RECYCLE_Z

        # Store current theme colors (default = Cinderella / World 0)
        self._ground_color      = (0.22, 0.52, 0.25)
        self._road_color_side   = (0.20, 0.21, 0.24)
        self._road_color_center = (0.24, 0.25, 0.29)
        self._sidewalk_color    = (0.58, 0.58, 0.60)
        self._foliage_tint      = (0.14, 0.50, 0.22)
        self._scenery_style     = "kingdom"

        self.segments: List[RoadSegment] = []
        self._init_segments()

    def _init_segments(self) -> None:
        """Initializes continuous adjacent road segments stretching from Z=0 into the distance."""
        for i in range(self.num_segments):
            z_pos = -i * self.segment_length
            segment = RoadSegment(
                z_position=z_pos,
                length=self.segment_length,
                variant=i,
                ground_color=self._ground_color,
                road_color_side=self._road_color_side,
                road_color_center=self._road_color_center,
                sidewalk_color=self._sidewalk_color,
                foliage_tint=self._foliage_tint,
                scenery_style=self._scenery_style,
            )
            self.segments.append(segment)

    def apply_world_config(self, world_config) -> None:
        """
        Applies a new WorldConfig theme to all existing road segments.
        Each segment rebuilds its GPU mesh with the new colors.
        Called by WorldManager callbacks when a world transition completes.
        """
        self._ground_color      = world_config.ground_color
        self._road_color_side   = world_config.road_color_side
        self._road_color_center = world_config.road_color_center
        self._sidewalk_color    = world_config.sidewalk_color
        self._foliage_tint      = world_config.foliage_tint
        self._scenery_style     = world_config.scenery_style

        for segment in self.segments:
            segment.apply_world_config(
                ground_color=self._ground_color,
                road_color_side=self._road_color_side,
                road_color_center=self._road_color_center,
                sidewalk_color=self._sidewalk_color,
                foliage_tint=self._foliage_tint,
                scenery_style=self._scenery_style,
            )

    def update(self, delta_time: float) -> None:
        """
        Moves all road segments forward and seamlessly recycles
        segments that pass behind the camera.
        """
        for segment in self.segments:
            segment.update(self.speed, delta_time)

        for segment in self.segments:
            segment_back_z = segment.z_position - (self.segment_length / 2.0)
            if segment_back_z > self.recycle_threshold:
                furthest_z = min(s.z_position for s in self.segments)
                segment.z_position = furthest_z - self.segment_length

    def render(self, renderer: Renderer, shader: ShaderProgram, camera: Camera) -> None:
        """Renders all visible road segments."""
        for segment in self.segments:
            segment.render(renderer, shader, camera)

    def get_lane_x(self, lane_index: int) -> float:
        """Returns the world X position for a given lane (-1, 0, +1)."""
        return max(-1, min(1, lane_index)) * settings.LANE_WIDTH

    def delete(self) -> None:
        """Releases all GPU resources allocated for track segments."""
        for segment in self.segments:
            segment.delete()
        self.segments.clear()
