"""
scoring.py - Distance, Collectibles, and Game Score Progression System.
Tracks live distance traveled, collection count, dynamic difficulty speed scaling,
and overall game score.
"""

from config import settings


class ScoreManager:
    """Manages game score, distance tracking, speed progression, and high scores."""

    def __init__(self, base_speed: float = settings.ROAD_SPEED):
        self.base_speed = base_speed
        self.current_speed = base_speed
        self.distance = 0.0
        self.collectibles_count = 0
        self.collectible_score = 0
        self.score = 0
        self.high_score = 0
        self.is_game_over = False
        self.game_over_reason = ""
        self.multiplier: float = 1.0  # Dynamic multiplier (e.g. 2.0x during Double Score)

    def set_multiplier(self, multiplier: float) -> None:
        """Sets active score multiplier (e.g. 2.0)."""
        self.multiplier = max(1.0, float(multiplier))

    def reset_multiplier(self) -> None:
        """Restores baseline 1.0x score multiplier."""
        self.multiplier = 1.0

    def update(self, delta_time: float) -> None:
        """Updates distance, speed scaling, and total score over time."""
        if self.is_game_over or delta_time <= 0.0:
            return

        # Advance distance traveled based on current speed
        distance_step = self.current_speed * delta_time
        self.distance += distance_step

        # Gradual difficulty progression: speed scales smoothly with distance (up to +10.0 units/sec)
        speed_boost = min(10.0, (self.distance / 120.0) * 0.75)
        self.current_speed = self.base_speed + speed_boost

        # Score computation: distance points scaled by multiplier + collectible points
        if self.multiplier > 1.0:
            # Earn extra bonus distance points when multiplier is active
            self.score = int(self.distance * self.multiplier) + self.collectible_score
        else:
            self.score = int(self.distance) + self.collectible_score

        if self.score > self.high_score:
            self.high_score = self.score

    def add_collectible(self, value: int = 50) -> None:
        """Increments collectible counter and grants bonus points scaled by multiplier."""
        if not self.is_game_over:
            self.collectibles_count += 1
            awarded_points = int(value * self.multiplier)
            self.collectible_score += awarded_points
            self.score += awarded_points
            if self.score > self.high_score:
                self.high_score = self.score

    def trigger_game_over(self, reason: str = "OBSTACLE COLLISION") -> None:
        """Freezes progression upon obstacle collision or villain capture."""
        if not self.is_game_over:
            self.is_game_over = True
            self.game_over_reason = reason
            if self.score > self.high_score:
                self.high_score = self.score

    def reset(self) -> None:
        """Resets gameplay run state for restart."""
        self.current_speed = self.base_speed
        self.distance = 0.0
        self.collectibles_count = 0
        self.collectible_score = 0
        self.score = 0
        self.multiplier = 1.0
        self.is_game_over = False
        self.game_over_reason = ""
