"""
settings.py - Global configurations and constants for Disney: Run Through the Stories.
"""

from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
SHADERS_DIR = ASSETS_DIR / "shaders"
TEXTURES_DIR = ASSETS_DIR / "textures"
AUDIO_DIR = ASSETS_DIR / "audio"

# Display & Window Settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Disney - Run Through the Stories [Phase 2: 3D Endless Environment]"
FULLSCREEN = False
VSYNC = True

# OpenGL Context Configuration
OPENGL_MAJOR_VERSION = 3
OPENGL_MINOR_VERSION = 3
OPENGL_FORWARD_COMPAT = True

# Rendering Settings
SKY_COLOR = (0.42, 0.65, 0.88, 1.0)    # Enchanted Disney vibrant sky blue
CLEAR_COLOR = SKY_COLOR
DEFAULT_FOV = 55.0                      # Vertical Field of View (degrees)
NEAR_CLIP = 0.1
FAR_CLIP = 250.0

# Environmental Lighting & Fog
SUN_LIGHT_POS = [15.0, 35.0, 20.0]
SUN_LIGHT_COLOR = [1.0, 0.98, 0.92]    # Warm sunlight
FOG_COLOR = [0.42, 0.65, 0.88]          # Matches sky for seamless horizon fading
FOG_START = 70.0
FOG_END = 210.0

# Third-Person Camera Placement
CAMERA_OFFSET = [0.0, 3.8, 7.6]        # Position relative to player (behind + above)
CAMERA_LOOK_AHEAD = 20.0                # Look-ahead distance down the track
CAMERA_SMOOTH_SPEED = 8.0               # Exponential damping coefficient
CAMERA_POS = [0.0, CAMERA_OFFSET[1], CAMERA_OFFSET[2]]
CAMERA_TARGET = [0.0, 0.8, -CAMERA_LOOK_AHEAD]
CAMERA_UP = [0.0, 1.0, 0.0]

# Three-Lane Road Dimensions
LANE_WIDTH = 2.4                        # Width of each running lane
TOTAL_LANES = 3
LANE_POSITIONS = [-LANE_WIDTH, 0.0, LANE_WIDTH]  # Left: -2.4, Center: 0.0, Right: +2.4
ROAD_WIDTH = LANE_WIDTH * TOTAL_LANES   # 7.2 units total road width
SIDEWALK_WIDTH = 1.8                    # Width of elevated sidewalk on each side
SIDEWALK_HEIGHT = 0.25                  # Height of curb/sidewalk above road surface

# Endless Road Generation
SEGMENT_LENGTH = 30.0                   # Length along Z per road segment
NUM_SEGMENTS = 8                        # Total visible segments (~240 units of track)
ROAD_SPEED = 22.0                       # Forward speed (units per second)
RECYCLE_Z = 15.0                        # Recycle threshold behind camera

# Animation / Demo Cube Settings
CUBE_ROTATION_SPEED_Y = 45.0   # Degrees per second around Y-axis
CUBE_ROTATION_SPEED_X = 25.0   # Degrees per second around X-axis

# Player Movement & Physics Configuration
PLAYER_START_LANE = 0                   # 0 = Center lane (-1 = Left, +1 = Right)
PLAYER_LANE_CHANGE_SPEED = 15.0         # Units per second lateral transition speed
PLAYER_JUMP_VELOCITY = 11.5             # Initial vertical jump velocity
PLAYER_GRAVITY = -34.0                  # Downward gravitational acceleration
PLAYER_SLIDE_DURATION = 0.75            # Slide duration in seconds
PLAYER_SLIDE_FAST_DROP = -22.0          # Accelerated downward drop when sliding in air
PLAYER_HEIGHT_STANDING = 1.85           # Standing bounding height
PLAYER_HEIGHT_SLIDING = 0.85            # Sliding bounding height
PLAYER_WIDTH = 0.70                     # Collision bounding width
PLAYER_DEPTH = 0.50                     # Collision bounding depth
PLAYER_RUN_CADENCE = 3.2                # Steps cycle frequency in Hz

# Villain Chase System Configuration (Evil Stepmother)
VILLAIN_START_DISTANCE = 2.6            # Initial trailing distance behind player (Z)
VILLAIN_MAX_DISTANCE = 3.2              # Safe max chase distance
VILLAIN_MIN_DISTANCE = 0.8              # Caught / Game Over distance
VILLAIN_WARNING_DISTANCE = 2.0          # Distance threshold for Warning state (Yellow)
VILLAIN_CRITICAL_DISTANCE = 1.4         # Distance threshold for Critical state (Red)
VILLAIN_RECOVERY_RATE = 0.16            # Distance player gains per second when running cleanly
VILLAIN_COIN_BONUS = 0.05               # Distance bonus per collectible collected
VILLAIN_MISTAKE_PENALTY = 0.75          # Distance penalty on hurdle stumble / mistake
VILLAIN_LATERAL_OFFSET = 0.78           # Lateral offset to prevent visual overlap with player
VILLAIN_LATERAL_FOLLOW_SPEED = 6.5      # Smoothing speed for villain tracking player lane

# Gameplay Specs (Planned for future phases)
WORLD_TRANSITION_INTERVAL = 60.0  # Seconds per Disney world
