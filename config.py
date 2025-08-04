"""
Configuration file containing all constants and static values for the Rubik's Cube project.
"""

# ============================================================================
# CUBE CONFIGURATION
# ============================================================================

# Main cube parameter - change this value to have a 2x2, 3x3, 4x4, etc. cube!
CUBE_SIZE = 2

# ============================================================================
# RENDERING CONSTANTS
# ============================================================================

# Cubie size (less than 1 to see the edges)
CUBIE_SIZE = 0.95

# Animation speed in degrees per frame (higher = faster)
ANIMATION_SPEED = 6

# ============================================================================
# WINDOW AND DISPLAY SETTINGS
# ============================================================================

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FOV = 45
NEAR_PLANE = 0.1
FAR_PLANE = 50.0
CAMERA_DISTANCE_MULTIPLIER = 5  # Multiplied by cube size for camera distance

# ============================================================================
# INITIAL VIEW SETTINGS
# ============================================================================

INITIAL_ROTATION_X = -30
INITIAL_ROTATION_Y = -45

# ============================================================================
# COLOR DEFINITIONS
# ============================================================================

# Face colors in RGB format (0-1)
COLORS = {
    'U': (1, 1, 1),       # White (Up)
    'D': (1, 1, 0),       # Yellow (Down)
    'F': (1, 0, 0),       # Red (Front)
    'B': (1, 0.5, 0),     # Orange (Back)
    'R': (0, 0, 1),       # Blue (Right)
    'L': (0, 0.8, 0),     # Green (Left)
    'INSIDE': (0.1, 0.1, 0.1)  # Inside color of cubies
}

# ============================================================================
# FACE DEFINITIONS
# ============================================================================

# Define the faces of a cubie and which normal direction they point to
FACES = {
    (0, 1, 0): 'U', (0, -1, 0): 'D',
    (0, 0, 1): 'F', (0, 0, -1): 'B',
    (1, 0, 0): 'R', (-1, 0, 0): 'L'
}

# Face names for easy iteration
FACE_NAMES = ['U', 'D', 'F', 'B', 'R', 'L']

# ============================================================================
# INPUT SETTINGS
# ============================================================================

# Mouse rotation sensitivity
MOUSE_ROTATION_SENSITIVITY = 0.5

# Key mappings for cube movements (axis, slice_index, base_direction)
def get_key_mappings():
    """Get key mappings based on current cube size."""
    margin = (CUBE_SIZE - 1) / 2.0
    return {
        'UP': ('y', margin, 1),       # Up face
        'DOWN': ('y', -margin, -1),   # Down face
        'RIGHT': ('x', margin, 1),    # Right face
        'LEFT': ('x', -margin, -1),   # Left face
        'FRONT': ('z', margin, 1),    # Front face
        'BACK': ('z', -margin, -1),   # Back face
    } 