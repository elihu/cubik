"""
rubiks_cube.py

Rubik's Cube class that handles cube generation, rendering, and manipulation.
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import config

class RubiksCube:
    """
    A 3D Rubik's Cube class that handles generation, rendering, and manipulation.
    """
    
    def __init__(self, sticker_size=None):
        """
        Initialize the Rubik's Cube.
        
        Args:
            sticker_size (float, optional): Size of stickers. If None, uses config default.
        """
        self.selected_face = None  # Track which face is currently selected
        self.sticker_size = sticker_size or config.STICKER_SIZE
        self.cube_stickers = {}
        self.printed_stickers = set()
        self.printed_rotation_logs = set()
        
        # Update config if custom sticker size provided
        if sticker_size is not None:
            self._update_config_sticker_size(sticker_size)
        
        # Generate the cube
        self.generate_cube()
    
    def _update_config_sticker_size(self, new_size):
        """Update config values when sticker size changes."""
        config.STICKER_SIZE = new_size
        config.STICKER_SPACING = config.STICKER_SIZE * 2
        config.BORDER_WIDTH = config.STICKER_SIZE * 11.67
        config.FACE_DISTANCE = config.STICKER_SIZE * 3.0
        
        # Update face configs with new distances
        for face in config.FACE_CONFIGS:
            center = config.FACE_CONFIGS[face]['center']
            if 'Y' in str(center):  # Up/Down faces
                config.FACE_CONFIGS[face]['center'] = (center[0], 
                    center[1] * (config.FACE_DISTANCE / (config.STICKER_SIZE * 3.0)), center[2])
            elif 'Z' in str(center):  # Front/Back faces
                config.FACE_CONFIGS[face]['center'] = (center[0], center[1], 
                    center[2] * (config.FACE_DISTANCE / (config.STICKER_SIZE * 3.0)))
            elif 'X' in str(center):  # Left/Right faces
                config.FACE_CONFIGS[face]['center'] = (center[0] * (config.FACE_DISTANCE / (config.STICKER_SIZE * 3.0)), 
                    center[1], center[2])
    
    def calculate_sticker_position(self, face, i, j):
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
        sticker_spacing = config.STICKER_SIZE * 2
        
        # Convert grid position to offset from center of face
        offset_i = (i - 1) * sticker_spacing  # -1, 0, 1
        offset_j = (j - 1) * sticker_spacing  # -1, 0, 1
        
        # Get face configuration
        face_config = config.FACE_CONFIGS[face]
        center_x, center_y, center_z = face_config['center']
        
        # Apply mapping based on face
        if face in ['U', 'D']:
            map_x, map_y, map_z = offset_j, 0, offset_i
        elif face in ['F', 'B']:
            map_x, map_y, map_z = offset_j, -offset_i, 0
        elif face in ['L', 'R']:
            map_x, map_y, map_z = 0, -offset_i, offset_j
        
        return (center_x + map_x, center_y + map_y, center_z + map_z)
    
    def generate_cube(self):
        """Generate the complete cube sticker configuration."""
        self.cube_stickers = {}
        
        for face in config.FACE_NAMES:
            face_config = config.FACE_CONFIGS[face]
            stickers = {}
            
            # Generate all 9 stickers for this face
            for i in range(3):
                for j in range(3):
                    pos = self.calculate_sticker_position(face, i, j)
                    stickers[(i, j)] = {
                        'pos': pos,
                        'color': config.FACE_COLORS[face]
                    }
            
            self.cube_stickers[face] = {
                'center': face_config['center'],
                'normal': face_config['normal'],
                'rotation': face_config['rotation'],
                'stickers': stickers
            }
    
    def apply_rotation(self, rotation_type):
        """Apply the specified rotation to orient the sticker correctly."""
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
    
    def draw_sticker(self, x, y, z, face, color, i=None, j=None):
        """
        Draws a single sticker (square) at (x, y, z) on the given face with the given color.
        """
        vertices = [
            (-config.STICKER_SIZE, -config.STICKER_SIZE, 0),
            ( config.STICKER_SIZE, -config.STICKER_SIZE, 0),
            ( config.STICKER_SIZE,  config.STICKER_SIZE, 0),
            (-config.STICKER_SIZE,  config.STICKER_SIZE, 0),
        ]
        
        glPushMatrix()
        glTranslatef(x, y, z)
        
        # Apply rotation based on face
        face_data = self.cube_stickers[face]
        self.apply_rotation(face_data['rotation'])
        
        # Draw sticker color
        if face == self.selected_face:
            # Make stickers much brighter for selected face (exaggerated for debug)
            color_rgb = config.COLOR_RGB[color]
            bright_color = tuple(min(1.0, c * 2.0) for c in color_rgb)  # 100% brighter for debug
            glColor3fv(bright_color)
        else:
            glColor3fv(config.COLOR_RGB[color])
        glBegin(GL_QUADS)
        for v in vertices:
            glVertex3fv(v)
        glEnd()
        
        # Draw black border for separation
        if face == self.selected_face:
            glColor3f(*config.SELECTION_BORDER_COLOR)  # Gold border for selected face
            glLineWidth(config.BORDER_WIDTH * 3)  # Thicker border for selected face
        else:
            glColor3f(*config.NORMAL_BORDER_COLOR)  # Dark gray border for normal faces
            glLineWidth(config.BORDER_WIDTH)
        glBegin(GL_LINE_LOOP)
        for v in vertices:
            glVertex3fv(v)
        glEnd()
        
        glPopMatrix()
    
    def draw(self):
        """Draws the complete Rubik's Cube."""
        for face in config.FACE_NAMES:
            face_data = self.cube_stickers[face]
            for (i, j), sticker_data in face_data['stickers'].items():
                x, y, z = sticker_data['pos']
                color = sticker_data['color']
                self.draw_sticker(x, y, z, face, color, i=i, j=j)
    
    def update_sticker_size(self, new_size):
        """
        Update the sticker size and regenerate the cube.
        
        Args:
            new_size (float): New sticker size
        """
        if new_size != self.sticker_size:
            self.sticker_size = new_size
            self._update_config_sticker_size(new_size)
            self.generate_cube()
            print(f"✓ Sticker size updated to {new_size}")
            print(f"  - Border width: {config.BORDER_WIDTH:.2f}")
            print(f"  - Face distance: {config.FACE_DISTANCE:.2f}")
    
    def validate_parameters(self):
        """Validate that the current parameters are within reasonable ranges."""
        if config.STICKER_SIZE <= 0 or config.STICKER_SIZE > 1.0:
            raise ValueError(f"STICKER_SIZE must be between 0 and 1.0, got {config.STICKER_SIZE}")
        
        if config.WINDOW_WIDTH <= 0 or config.WINDOW_HEIGHT <= 0:
            raise ValueError(f"Window dimensions must be positive, got {config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        
        print(f"✓ Parameters validated:")
        print(f"  - Sticker size: {config.STICKER_SIZE}")
        print(f"  - Border width: {config.BORDER_WIDTH:.2f} (calculated)")
        print(f"  - Face distance: {config.FACE_DISTANCE:.2f} (calculated)")
        print(f"  - Window size: {config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
    
    def get_cube_state(self):
        """Get the current state of the cube."""
        return self.cube_stickers.copy()
    
    def reset_to_solved(self):
        """Reset the cube to its solved state."""
        self.generate_cube()
        print("✓ Cube reset to solved state")
    
    def set_selected_face(self, face_name):
        """
        Set which face is currently selected for highlighting.
        
        Args:
            face_name (str or None): Face name ('U', 'D', 'F', 'B', 'L', 'R') or None to clear selection
        """
        self.selected_face = face_name