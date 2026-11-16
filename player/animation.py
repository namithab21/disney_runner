"""
animation.py - Procedural Character Animation System.
Calculates limb angles (hips, knees, shoulders, torso bounce, bank roll)
for running, jumping, and sliding states with smooth blend transitions.
"""

import numpy as np
from config import settings
from player.movement import STATE_RUNNING, STATE_JUMPING, STATE_SLIDING


class PlayerAnimation:
    """Manages procedural joint rotations, torso bob, and state blends."""

    def __init__(self):
        # Running phase timer (radians)
        self.run_phase = 0.0
        self.cadence = settings.PLAYER_RUN_CADENCE

        # Current interpolated joint angles (degrees)
        self.left_leg_pitch = 0.0
        self.right_leg_pitch = 0.0
        self.left_arm_pitch = 0.0
        self.right_arm_pitch = 0.0
        self.torso_pitch = 0.0
        self.torso_roll = 0.0
        self.torso_bob_y = 0.0
        self.crouch_offset_y = 0.0

        # State blend weights (0.0 to 1.0)
        self.jump_weight = 0.0
        self.slide_weight = 0.0

    def update(self, delta_time: float, state: str, lateral_velocity: float) -> None:
        """Updates animation cycle, state blends, and joint rotations."""
        if delta_time <= 0.0:
            return

        # -------------------------------------------------------------
        # 1. State Blend Transitions (Smooth ease in/out)
        # -------------------------------------------------------------
        blend_speed = 12.0
        target_jump_weight = 1.0 if state == STATE_JUMPING else 0.0
        target_slide_weight = 1.0 if state == STATE_SLIDING else 0.0

        self.jump_weight += (target_jump_weight - self.jump_weight) * min(1.0, blend_speed * delta_time)
        self.slide_weight += (target_slide_weight - self.slide_weight) * min(1.0, blend_speed * delta_time)

        # -------------------------------------------------------------
        # 2. Continuous Run Cycle Phase
        # -------------------------------------------------------------
        # Running continues at all times (even during lane changes)
        phase_speed = self.cadence * 2.0 * np.pi
        self.run_phase = (self.run_phase + phase_speed * delta_time) % (2.0 * np.pi)

        # Run cycle poses:
        run_leg_amp = 36.0   # Maximum leg swing in degrees
        run_arm_amp = 32.0   # Maximum arm swing in degrees
        run_bob_amp = 0.05   # Torso vertical bounce amplitude

        # Opposite alternating swings
        run_l_leg = np.sin(self.run_phase) * run_leg_amp
        run_r_leg = -run_l_leg
        run_l_arm = -run_l_leg * (run_arm_amp / run_leg_amp)
        run_r_arm = -run_l_arm
        run_bob = np.abs(np.sin(self.run_phase)) * run_bob_amp
        run_pitch = 7.0      # Forward torso athletic lean

        # -------------------------------------------------------------
        # 3. Jump Pose (Dynamic tuck in air)
        # -------------------------------------------------------------
        jump_l_leg = -25.0   # Legs tucked forward
        jump_r_leg = 15.0    # Trailing leg slightly back
        jump_l_arm = -30.0   # Arms raised/extended for balance
        jump_r_arm = -25.0
        jump_pitch = 12.0

        # -------------------------------------------------------------
        # 4. Slide Pose (Low crouch / backward lean, legs forward)
        # -------------------------------------------------------------
        slide_l_leg = -58.0  # Legs thrown forward
        slide_r_leg = -52.0
        slide_l_arm = 38.0   # Arms back for sliding balance
        slide_r_arm = 38.0
        slide_pitch = -22.0  # Torso leans back
        slide_crouch = -0.42 # Drop center of mass down

        # -------------------------------------------------------------
        # 5. Composite Joint Angles via Weighted Blending
        # -------------------------------------------------------------
        run_weight = max(0.0, 1.0 - self.jump_weight - self.slide_weight)

        self.left_leg_pitch = (run_l_leg * run_weight) + (jump_l_leg * self.jump_weight) + (slide_l_leg * self.slide_weight)
        self.right_leg_pitch = (run_r_leg * run_weight) + (jump_r_leg * self.jump_weight) + (slide_r_leg * self.slide_weight)

        self.left_arm_pitch = (run_l_arm * run_weight) + (jump_l_arm * self.jump_weight) + (slide_l_arm * self.slide_weight)
        self.right_arm_pitch = (run_r_arm * run_weight) + (jump_r_arm * self.jump_weight) + (slide_r_arm * self.slide_weight)

        self.torso_pitch = (run_pitch * run_weight) + (jump_pitch * self.jump_weight) + (slide_pitch * self.slide_weight)
        self.torso_bob_y = run_bob * run_weight
        self.crouch_offset_y = slide_crouch * self.slide_weight

        # -------------------------------------------------------------
        # 6. Lateral Banking Roll (Lean into lane switch)
        # -------------------------------------------------------------
        target_roll = -np.clip(lateral_velocity * 1.6, -14.0, 14.0)
        self.torso_roll += (target_roll - self.torso_roll) * min(1.0, 15.0 * delta_time)
