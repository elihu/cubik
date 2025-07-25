"""
main.py

This script renders a 3D Rubik's Cube (3x3x3) using Pygame and PyOpenGL.
No interaction yet, just a static cube for visualization.
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys

# ============================================================================
# CONFIGURABLE PARAMETERS
# ============================================================================

# Cube dimensions and appearance
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
BORDER_WIDTH = STICKER_SIZE * 11.67  # Border width proportional to sticker size (3.5/0.3 = 11.67)
FACE_DISTANCE = STICKER_SIZE * 3.0   # Face distance proportional to sticker size (0.9/0.3 = 3.0)

def validate_parameters():
    """
    Validate that the configurable parameters are within reasonable ranges.
    Only validates STICKER_SIZE and window parameters, as other parameters
    are calculated automatically.
    """
    if STICKER_SIZE <= 0 or STICKER_SIZE > 1.0:
        raise ValueError(f"STICKER_SIZE must be between 0 and 1.0, got {STICKER_SIZE}")
    
    if WINDOW_WIDTH <= 0 or WINDOW_HEIGHT <= 0:
        raise ValueError(f"Window dimensions must be positive, got {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    
    print(f"✓ Parameters validated:")
    print(f"  - Sticker size: {STICKER_SIZE}")
    print(f"  - Border width: {BORDER_WIDTH:.2f} (calculated)")
    print(f"  - Face distance: {FACE_DISTANCE:.2f} (calculated)")
    print(f"  - Window size: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")

# Validate parameters at startup
validate_parameters()

def calculate_sticker_position(face, i, j):
    """
    Calculate the 3D position of a sticker based on its face and grid position.
    
    Args:
        face (str): Face identifier ('U', 'D', 'F', 'B', 'L', 'R')
        i (int): Row index (0, 1, 2)
        j (int): Column index (0, 1, 2)
    
    Returns:
        tuple: (x, y, z) coordinates
    """
    # Calculate sticker spacing based on current parameters
    # We want stickers to be adjacent with only border separation
    sticker_spacing = STICKER_SIZE * 2  # Full sticker width for adjacent placement
    
    # Convert grid position to offset from center of face
    # Grid positions: (0,0) is top-left, (2,2) is bottom-right
    offset_i = (i - 1) * sticker_spacing  # -1, 0, 1
    offset_j = (j - 1) * sticker_spacing  # -1, 0, 1
    
    # Face centers and coordinate mappings
    # Using parametrized face centers
    face_configs = {
        'U': {'center': (0, FACE_DISTANCE, 0), 'mapping': (offset_j, 0, offset_i)},
        'D': {'center': (0, -FACE_DISTANCE, 0), 'mapping': (offset_j, 0, offset_i)},
        'F': {'center': (0, 0, FACE_DISTANCE), 'mapping': (offset_j, -offset_i, 0)},
        'B': {'center': (0, 0, -FACE_DISTANCE), 'mapping': (offset_j, -offset_i, 0)},
        'L': {'center': (-FACE_DISTANCE, 0, 0), 'mapping': (0, -offset_i, offset_j)},
        'R': {'center': (FACE_DISTANCE, 0, 0), 'mapping': (0, -offset_i, -offset_j)},
    }
    
    config = face_configs[face]
    center_x, center_y, center_z = config['center']
    map_x, map_y, map_z = config['mapping']
    
    return (center_x + map_x, center_y + map_y, center_z + map_z)

def generate_cube_stickers():
    """
    Generate the complete cube sticker configuration dynamically.
    
    Returns:
        dict: Complete CUBE_STICKERS configuration
    """
    # Initial solved state colors for each face
    face_colors = {
        'U': 'W',  # White (Up)
        'D': 'Y',  # Yellow (Down)
        'F': 'R',  # Red (Front)
        'B': 'O',  # Orange (Back)
        'L': 'G',  # Green (Left)
        'R': 'B',  # Blue (Right)
    }
    
    # Face configurations with center, normal, and rotation
    face_configs = {
        'U': {'center': (0, FACE_DISTANCE, 0), 'normal': (0, 1, 0), 'rotation': '90_x'},
        'D': {'center': (0, -FACE_DISTANCE, 0), 'normal': (0, -1, 0), 'rotation': '-90_x'},
        'F': {'center': (0, 0, FACE_DISTANCE), 'normal': (0, 0, 1), 'rotation': '180_y'},
        'B': {'center': (0, 0, -FACE_DISTANCE), 'normal': (0, 0, -1), 'rotation': '180_y'},
        'L': {'center': (-FACE_DISTANCE, 0, 0), 'normal': (-1, 0, 0), 'rotation': '90_y'},
        'R': {'center': (FACE_DISTANCE, 0, 0), 'normal': (1, 0, 0), 'rotation': '90_y'},
    }
    
    cube_stickers = {}
    
    for face in ['U', 'D', 'F', 'B', 'L', 'R']:
        config = face_configs[face]
        stickers = {}
        
        # Generate all 9 stickers for this face
        for i in range(3):
            for j in range(3):
                pos = calculate_sticker_position(face, i, j)
                stickers[(i, j)] = {
                    'pos': pos,
                    'color': face_colors[face]
                }
        
        cube_stickers[face] = {
            'center': config['center'],
            'normal': config['normal'],
            'rotation': config['rotation'],
            'stickers': stickers
        }
    
    return cube_stickers

def regenerate_cube():
    """
    Regenerate the cube configuration with current parameters.
    This function can be called if parameters are changed at runtime.
    """
    global CUBE_STICKERS
    CUBE_STICKERS = generate_cube_stickers()
    print("✓ Cube configuration regenerated with current parameters")

def update_parameter(param_name, new_value):
    """
    Update a parameter and regenerate the cube.
    Currently only supports updating STICKER_SIZE, which automatically
    updates all other derived parameters.
    
    Args:
        param_name (str): Name of the parameter to update (only 'STICKER_SIZE' supported)
        new_value: New value for the parameter
    """
    global STICKER_SIZE, BORDER_WIDTH, FACE_DISTANCE, STICKER_SPACING
    
    if param_name == 'STICKER_SIZE':
        STICKER_SIZE = new_value
        # Update all derived parameters automatically
        STICKER_SPACING = STICKER_SIZE * 2
        BORDER_WIDTH = STICKER_SIZE * 11.67
        FACE_DISTANCE = STICKER_SIZE * 3.0
    else:
        raise ValueError(f"Only STICKER_SIZE can be updated directly. Other parameters are calculated automatically.")
    
    # Validate and regenerate
    validate_parameters()
    regenerate_cube()
    print(f"✓ Parameter {param_name} updated to {new_value}")
    print(f"  - BORDER_WIDTH automatically updated to {BORDER_WIDTH:.2f}")
    print(f"  - FACE_DISTANCE automatically updated to {FACE_DISTANCE:.2f}")

# Generate the cube configuration dynamically
regenerate_cube()

# Color letters: W=White, Y=Yellow, R=Red, O=Orange, B=Blue, G=Green
COLOR_RGB = {
    'W': (1, 1, 1),      # White
    'Y': (1, 1, 0),      # Yellow
    'R': (1, 0, 0),      # Red
    'O': (1, 0.5, 0),    # Orange
    'B': (0, 0, 1),      # Blue
    'G': (0, 1, 0),      # Green
}

# CUBE_STICKERS is now generated by regenerate_cube() function

# Set to keep track of printed stickers for debugging
PRINTED_STICKERS = set()
# Set to keep track of printed rotation test logs
PRINTED_ROTATION_LOGS = set()

def apply_rotation(rotation_type):
    """
    Apply the specified rotation to orient the sticker correctly.
    """
    if rotation_type == 'none':
        pass
    elif rotation_type == '180_x':
        glRotatef(180, 1, 0, 0)
    elif rotation_type == '180_y':
        glRotatef(180, 0, 1, 0)
    elif rotation_type == '90_x':
        glRotatef(90, 1, 0, 0)
    elif rotation_type == '-90_x':
        glRotatef(-90, 1, 0, 0)
    elif rotation_type == '90_y':
        glRotatef(90, 0, 1, 0)
    elif rotation_type == '-90_y':
        glRotatef(-90, 0, 1, 0)
    elif rotation_type == '90_z':
        glRotatef(90, 0, 0, 1)
    elif rotation_type == '-90_z':
        glRotatef(-90, 0, 0, 1)
    elif rotation_type == '90_y_90_x':
        glRotatef(90, 0, 1, 0)
        glRotatef(90, 1, 0, 0)
    elif rotation_type == '-90_y_90_x':
        glRotatef(-90, 0, 1, 0)
        glRotatef(90, 1, 0, 0)

def draw_sticker(x, y, z, face, color, i=None, j=None):
    """
    Draws a single sticker (square) at (x, y, z) on the given face with the given color.
    Prints the position and orientation for debugging (only once per sticker).
    Draws a black border for separation between stickers.
    """
    vertices = [
        (-STICKER_SIZE, -STICKER_SIZE, 0),
        ( STICKER_SIZE, -STICKER_SIZE, 0),
        ( STICKER_SIZE,  STICKER_SIZE, 0),
        (-STICKER_SIZE,  STICKER_SIZE, 0),
    ]
    glPushMatrix()
    glTranslatef(x, y, z)
    
    # Apply rotation based on face
    face_data = CUBE_STICKERS[face]
    apply_rotation(face_data['rotation'])
    
    # Debug print (only once per sticker)
    key = (face, i, j)
    if key not in PRINTED_STICKERS:
        print(f"Sticker {face}[{i},{j}] at ({x:.2f}, {y:.2f}, {z:.2f})")
        PRINTED_STICKERS.add(key)
    
    # Draw sticker color
    glColor3fv(COLOR_RGB[color])
    glBegin(GL_QUADS)
    for v in vertices:
        glVertex3fv(v)
    glEnd()
    
    # Draw black border for separation
    glColor3f(0, 0, 0)
    glLineWidth(BORDER_WIDTH)
    glBegin(GL_LINE_LOOP)
    for v in vertices:
        glVertex3fv(v)
    glEnd()
    glPopMatrix()

def test_rotations():
    """
    Test function to understand the rotation axes by rendering a single sticker
    with different rotations.
    """
    vertices = [
        (-STICKER_SIZE, -STICKER_SIZE, 0),
        ( STICKER_SIZE, -STICKER_SIZE, 0),
        ( STICKER_SIZE,  STICKER_SIZE, 0),
        (-STICKER_SIZE,  STICKER_SIZE, 0),
    ]
    
    # Test different rotations
    rotations = [
        ('none', 'No rotation'),
        ('90_x', '90° X axis'),
        ('-90_x', '-90° X axis'),
        ('90_y', '90° Y axis'),
        ('-90_y', '-90° Y axis'),
        ('90_z', '90° Z axis'),
        ('-90_z', '-90° Z axis'),
    ]
    
    for i, (rotation_type, description) in enumerate(rotations):
        x_pos = -2 + i * 0.6
        glPushMatrix()
        glTranslatef(x_pos, 0, 0)  # Space them out horizontally
        
        # Apply the rotation
        apply_rotation(rotation_type)
        
        # Log the rotation and position (only once)
        if rotation_type not in PRINTED_ROTATION_LOGS:
            print(f"Sticker {i+1}: {description} at position ({x_pos:.1f}, 0, 0)")
            PRINTED_ROTATION_LOGS.add(rotation_type)
        
        # Draw sticker with different color for each rotation
        glColor3f(1, 0.5, 0)  # Orange
        glBegin(GL_QUADS)
        for v in vertices:
            glVertex3fv(v)
        glEnd()
        
        # Draw border
        glColor3f(1, 1, 1)  # White border
        glLineWidth(2)
        glBegin(GL_LINE_LOOP)
        for v in vertices:
            glVertex3fv(v)
        glEnd()
        
        glPopMatrix()

def draw_rubiks_cube():
    """
    Draws the complete Rubik's Cube using the new sticker-based structure.
    """
    for face in ['F', 'B', 'U', 'D', 'L', 'R']:  # All faces
        face_data = CUBE_STICKERS[face]
        for (i, j), sticker_data in face_data['stickers'].items():
            x, y, z = sticker_data['pos']
            color = sticker_data['color']
            draw_sticker(x, y, z, face, color, i=i, j=j)

def main():
    pygame.init()
    display = (WINDOW_WIDTH, WINDOW_HEIGHT)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1)
    glDisable(GL_CULL_FACE)
    gluPerspective(FOV, (display[0] / display[1]), NEAR_PLANE, FAR_PLANE)
    glTranslatef(0.0, 0.0, -CAMERA_DISTANCE)
    glRotatef(INITIAL_ROTATION_X, 1, 0, 0)
    glRotatef(INITIAL_ROTATION_Y, 0, 1, 0)

    clock = pygame.time.Clock()
    running = True
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            draw_rubiks_cube()
            pygame.display.flip()
            clock.tick(60)
    except KeyboardInterrupt:
        print("\nCerrando el programa con Ctrl+C...")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main() 