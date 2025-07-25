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

# Color letters: W=White, Y=Yellow, R=Red, O=Orange, B=Blue, G=Green
COLOR_RGB = {
    'W': (1, 1, 1),      # White
    'Y': (1, 1, 0),      # Yellow
    'R': (1, 0, 0),      # Red
    'O': (1, 0.5, 0),    # Orange
    'B': (0, 0, 1),      # Blue
    'G': (0, 1, 0),      # Green
}

# Estructura de datos para cada sticker del cubo
CUBE_STICKERS = {
    'U': {
        'center': (0, 1.0, 0),
        'normal': (0, 1, 0),
        'rotation': '90_x',
        'stickers': {
            (0, 0): {'pos': (-0.67, 1.0, -0.67), 'color': 'W'},
            (0, 1): {'pos': (0, 1.0, -0.67), 'color': 'W'},
            (0, 2): {'pos': (0.67, 1.0, -0.67), 'color': 'W'},
            (1, 0): {'pos': (-0.67, 1.0, 0), 'color': 'W'},
            (1, 1): {'pos': (0, 1.0, 0), 'color': 'W'},
            (1, 2): {'pos': (0.67, 1.0, 0), 'color': 'W'},
            (2, 0): {'pos': (-0.67, 1.0, 0.67), 'color': 'W'},
            (2, 1): {'pos': (0, 1.0, 0.67), 'color': 'W'},
            (2, 2): {'pos': (0.67, 1.0, 0.67), 'color': 'W'},
        }
    },
    'D': {
        'center': (0, -1, 0),
        'normal': (0, -1, 0),
        'rotation': '-90_x',
        'stickers': {
            (0, 0): {'pos': (-0.67, -1, -0.67), 'color': 'Y'},
            (0, 1): {'pos': (0, -1, -0.67), 'color': 'Y'},
            (0, 2): {'pos': (0.67, -1, -0.67), 'color': 'Y'},
            (1, 0): {'pos': (-0.67, -1, 0), 'color': 'Y'},
            (1, 1): {'pos': (0, -1, 0), 'color': 'Y'},
            (1, 2): {'pos': (0.67, -1, 0), 'color': 'Y'},
            (2, 0): {'pos': (-0.67, -1, 0.67), 'color': 'Y'},
            (2, 1): {'pos': (0, -1, 0.67), 'color': 'Y'},
            (2, 2): {'pos': (0.67, -1, 0.67), 'color': 'Y'},
        }
    },
    'F': {
        'center': (0, 0, -1),
        'normal': (0, 0, -1),
        'rotation': '180_y',
        'stickers': {
            (0, 0): {'pos': (-0.67, 0.67, -1), 'color': 'R'},
            (0, 1): {'pos': (0, 0.67, -1), 'color': 'R'},
            (0, 2): {'pos': (0.67, 0.67, -1), 'color': 'R'},
            (1, 0): {'pos': (-0.67, 0, -1), 'color': 'R'},
            (1, 1): {'pos': (0, 0, -1), 'color': 'R'},
            (1, 2): {'pos': (0.67, 0, -1), 'color': 'R'},
            (2, 0): {'pos': (-0.67, -0.67, -1), 'color': 'R'},
            (2, 1): {'pos': (0, -0.67, -1), 'color': 'R'},
            (2, 2): {'pos': (0.67, -0.67, -1), 'color': 'R'},
        }
    },
    'B': {
        'center': (0, 0, 1),
        'normal': (0, 0, 1),
        'rotation': '180_y',
        'stickers': {
            (0, 0): {'pos': (0.67, 0.67, 1), 'color': 'O'},
            (0, 1): {'pos': (0, 0.67, 1), 'color': 'O'},
            (0, 2): {'pos': (-0.67, 0.67, 1), 'color': 'O'},
            (1, 0): {'pos': (0.67, 0, 1), 'color': 'O'},
            (1, 1): {'pos': (0, 0, 1), 'color': 'O'},
            (1, 2): {'pos': (-0.67, 0, 1), 'color': 'O'},
            (2, 0): {'pos': (0.67, -0.67, 1), 'color': 'O'},
            (2, 1): {'pos': (0, -0.67, 1), 'color': 'O'},
            (2, 2): {'pos': (-0.67, -0.67, 1), 'color': 'O'},
        }
    },
    'L': {
        'center': (-1, 0, 0),
        'normal': (-1, 0, 0),
        'rotation': '90_y',
        'stickers': {
            (0, 0): {'pos': (-1, 0.67, -0.67), 'color': 'G'},
            (0, 1): {'pos': (-1, 0.67, 0), 'color': 'G'},
            (0, 2): {'pos': (-1, 0.67, 0.67), 'color': 'G'},
            (1, 0): {'pos': (-1, 0, -0.67), 'color': 'G'},
            (1, 1): {'pos': (-1, 0, 0), 'color': 'G'},
            (1, 2): {'pos': (-1, 0, 0.67), 'color': 'G'},
            (2, 0): {'pos': (-1, -0.67, -0.67), 'color': 'G'},
            (2, 1): {'pos': (-1, -0.67, 0), 'color': 'G'},
            (2, 2): {'pos': (-1, -0.67, 0.67), 'color': 'G'},
        }
    },
    'R': {
        'center': (1, 0, 0),
        'normal': (1, 0, 0),
        'rotation': '90_y',
        'stickers': {
            (0, 0): {'pos': (1, 0.67, 0.67), 'color': 'B'},
            (0, 1): {'pos': (1, 0.67, 0), 'color': 'B'},
            (0, 2): {'pos': (1, 0.67, -0.67), 'color': 'B'},
            (1, 0): {'pos': (1, 0, 0.67), 'color': 'B'},
            (1, 1): {'pos': (1, 0, 0), 'color': 'B'},
            (1, 2): {'pos': (1, 0, -0.67), 'color': 'B'},
            (2, 0): {'pos': (1, -0.67, 0.67), 'color': 'B'},
            (2, 1): {'pos': (1, -0.67, 0), 'color': 'B'},
            (2, 2): {'pos': (1, -0.67, -0.67), 'color': 'B'},
        }
    }
}

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
    S = 0.30  # Sticker size (slightly smaller to create more gaps)
    vertices = [
        (-S, -S, 0),
        ( S, -S, 0),
        ( S,  S, 0),
        (-S,  S, 0),
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
    
    # Draw black border for separation (thicker)
    glColor3f(0, 0, 0)
    glLineWidth(3)
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
    S = 0.28  # Sticker size
    vertices = [
        (-S, -S, 0),
        ( S, -S, 0),
        ( S,  S, 0),
        (-S,  S, 0),
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
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1)
    glDisable(GL_CULL_FACE)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -10)
    glRotatef(25, 1, 0, 0)
    glRotatef(-30, 0, 1, 0)

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