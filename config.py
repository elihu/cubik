"""
config.py

Configuration file containing all constants and static values for the Rubik's Cube project.
"""

# ============================================================================
# CUBE CONFIGURATION
# ============================================================================

# Main cube parameter - all other dimensions are calculated from this
STICKER_SIZE = 0.5           # Size of each sticker (0.0 to 1.0) - MAIN PARAMETER

# Window and rendering settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FOV = 45                     # Field of view
NEAR_PLANE = 0.1
FAR_PLANE = 50.0
CAMERA_DISTANCE = 10.0
INITIAL_ROTATION_X = 25
INITIAL_ROTATION_Y = -30

# ============================================================================
# CALCULATED VALUES
# ============================================================================

# Calculate derived values (these are computed automatically based on STICKER_SIZE)
STICKER_SPACING = STICKER_SIZE * 2  # Full sticker width for adjacent placement
BORDER_WIDTH = STICKER_SIZE * 0.4  # Border width proportional to sticker size (much smaller)
FACE_DISTANCE = STICKER_SIZE * 3.0   # Face distance proportional to sticker size

# ============================================================================
# COLOR DEFINITIONS
# ============================================================================

# Color letters: W=White, Y=Yellow, R=Red, O=Orange, B=Blue, G=Green
COLOR_RGB = {
    'W': (1, 1, 1),      # White
    'Y': (1, 1, 0),      # Yellow
    'R': (1, 0, 0),      # Red
    'O': (1, 0.5, 0),    # Orange
    'B': (0, 0, 1),      # Blue
    'G': (0, 1, 0),      # Green
}

# ============================================================================
# FACE CONFIGURATIONS
# ============================================================================

# Standard Rubik's Cube face colors
FACE_COLORS = {
    'U': 'W',  # White (Up)
    'D': 'Y',  # Yellow (Down)
    'F': 'R',  # Red (Front)
    'B': 'O',  # Orange (Back)
    'L': 'G',  # Green (Left face)
    'R': 'B',  # Blue (Right face)
}

# Face identifiers
FACE_NAMES = ['U', 'D', 'F', 'B', 'L', 'R']

# Face configurations with center, normal, and rotation
FACE_CONFIGS = {
    'U': {'center': (0, FACE_DISTANCE, 0), 'normal': (0, 1, 0), 'rotation': '90_x'},
    'D': {'center': (0, -FACE_DISTANCE, 0), 'normal': (0, -1, 0), 'rotation': '-90_x'},
    'F': {'center': (0, 0, FACE_DISTANCE), 'normal': (0, 0, 1), 'rotation': '180_y'},
    'B': {'center': (0, 0, -FACE_DISTANCE), 'normal': (0, 0, -1), 'rotation': '180_y'},
    'L': {'center': (-FACE_DISTANCE, 0, 0), 'normal': (-1, 0, 0), 'rotation': '90_y'},
    'R': {'center': (FACE_DISTANCE, 0, 0), 'normal': (1, 0, 0), 'rotation': '90_y'},
}

# ============================================================================
# SELECTION COLORS
# ============================================================================

# Selection highlighting colors
SELECTION_BORDER_COLOR = (1, 0.8, 0)  # Gold border for selected face
ADJACENT_BORDER_COLOR = (0.8, 0.6, 0)  # Darker gold for adjacent stickers
NORMAL_BORDER_COLOR = (0.2, 0.2, 0.2)  # Dark gray for normal faces 