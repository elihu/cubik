"""
Cubie class representing a single piece of the Rubik's Cube.
"""

import numpy as np
import math
from OpenGL.GL import *
import config

class Cubie:
    """Represents a single cubie of the Rubik's Cube."""
    
    def __init__(self, pos, N):
        """
        Initialize a cubie.
        
        Args:
            pos (tuple): Initial position (x, y, z)
            N (int): Cube size
        """
        self.pos = np.array(pos, dtype=float)
        self.matrix = np.identity(4)
        self.matrix[0:3, 3] = self.pos
        
        # Assign colors based on initial position
        self.colors = {}
        boundary = (N - 1) / 2.0
        epsilon = 1e-6
        
        # Assign 'INSIDE' color by default to all faces
        for normal, face_name in config.FACES.items():
            self.colors[face_name] = config.COLORS['INSIDE']
            
        # Assign face colors to exterior faces
        if abs(self.pos[0] - boundary) < epsilon:
            self.colors['R'] = config.COLORS['R']
        if abs(self.pos[0] + boundary) < epsilon:
            self.colors['L'] = config.COLORS['L']
        if abs(self.pos[1] - boundary) < epsilon:
            self.colors['U'] = config.COLORS['U']
        if abs(self.pos[1] + boundary) < epsilon:
            self.colors['D'] = config.COLORS['D']
        if abs(self.pos[2] - boundary) < epsilon:
            self.colors['F'] = config.COLORS['F']
        if abs(self.pos[2] + boundary) < epsilon:
            self.colors['B'] = config.COLORS['B']
        
        # Selection state
        self.is_selected = False
        self.is_adjacent = False
    
    def set_selected(self, selected):
        """Set whether this cubie is selected."""
        self.is_selected = selected
    
    def set_adjacent(self, adjacent):
        """Set whether this cubie is adjacent to selected face."""
        self.is_adjacent = adjacent

    def draw(self, animating_matrix=None):
        """
        Draw the cubie applying its transformation matrix and animation matrix if provided.
        
        Args:
            animating_matrix: Optional animation matrix to apply
        """
        glPushMatrix()

        # Get the final transformation matrix
        final_matrix = np.identity(4)
        if animating_matrix is not None:
            final_matrix = np.dot(animating_matrix, self.matrix)
            glMultMatrixf(final_matrix.T)
        else:
            final_matrix = self.matrix
            glMultMatrixf(self.matrix.T)

        # Extract rotation matrix to transform normals
        rotation_matrix = final_matrix[:3, :3]
        
        # Check if this cubie is currently animating
        is_animating = animating_matrix is not None
        
        glBegin(GL_QUADS)
        s = config.CUBIE_SIZE / 2.0
        for normal, face_name in config.FACES.items():
            # Use pre-assigned color
            original_color = self.colors[face_name]
            color = original_color
            
            # Apply brightness for selected faces or animating cubies
            if (self.is_selected and original_color != config.COLORS['INSIDE']) or is_animating:
                # Make selected faces or animating cubies brighter
                color = tuple(min(1.0, c * config.SELECTION_BRIGHTNESS_MULTIPLIER) for c in color)
            
            # Apply interior color for selected cubies or animating cubies
            if ((self.is_selected and original_color == config.COLORS['INSIDE']) or 
                (is_animating and original_color == config.COLORS['INSIDE'])):
                color = config.SELECTION_INTERIOR_COLOR
            
            glColor3fv(color)
            
            # For lighting, always use the transformed normal
            transformed_normal = np.dot(rotation_matrix, normal)
            glNormal3fv(transformed_normal)

            # Create the 4 vertices of the face using vector algebra
            p1 = np.array([-s, -s, s])
            p2 = np.array([s, -s, s])
            p3 = np.array([s, s, s])
            p4 = np.array([-s, s, s])
            
            # Rotate vertices to match the normal orientation
            if normal[0] != 0:
                rotation = self.get_rotation_matrix(90 * normal[0], (0, 1, 0))
            elif normal[1] != 0:
                rotation = self.get_rotation_matrix(-90 * normal[1], (1, 0, 0))
            else:
                rotation = self.get_rotation_matrix(180 if normal[2] < 0 else 0, (0, 1, 0))
            
            glVertex3fv(np.dot(rotation, p1))
            glVertex3fv(np.dot(rotation, p2))
            glVertex3fv(np.dot(rotation, p3))
            glVertex3fv(np.dot(rotation, p4))
        glEnd()

        # Draw borders for selection highlighting or animating cubies (all gold)
        if self.is_selected or self.is_adjacent or is_animating:
            glColor3f(*config.SELECTION_COLOR)
            
            # Draw borders for each face
            for normal, face_name in config.FACES.items():
                if self.colors[face_name] != config.COLORS['INSIDE']:
                    # Draw border for this face
                    self._draw_face_border(normal, s)
        
        glPopMatrix()
    
    def _draw_face_border(self, normal, s):
        """Draw a border around a face."""
        # Create border vertices (slightly larger than the face)
        border_offset = config.BORDER_WIDTH
        p1 = np.array([-s - border_offset, -s - border_offset, s + border_offset])
        p2 = np.array([s + border_offset, -s - border_offset, s + border_offset])
        p3 = np.array([s + border_offset, s + border_offset, s + border_offset])
        p4 = np.array([-s - border_offset, s + border_offset, s + border_offset])
        
        # Rotate vertices to match the normal orientation
        if normal[0] != 0:
            rotation = self.get_rotation_matrix(90 * normal[0], (0, 1, 0))
        elif normal[1] != 0:
            rotation = self.get_rotation_matrix(-90 * normal[1], (1, 0, 0))
        else:
            rotation = self.get_rotation_matrix(180 if normal[2] < 0 else 0, (0, 1, 0))
        
        # Draw border as line loop
        glBegin(GL_LINE_LOOP)
        glVertex3fv(np.dot(rotation, p1))
        glVertex3fv(np.dot(rotation, p2))
        glVertex3fv(np.dot(rotation, p3))
        glVertex3fv(np.dot(rotation, p4))
        glEnd()
    
    def get_rotation_matrix(self, angle, axis):
        """
        Generate a 3x3 rotation matrix.
        
        Args:
            angle (float): Rotation angle in degrees
            axis (tuple): Rotation axis (x, y, z)
            
        Returns:
            numpy.ndarray: 3x3 rotation matrix
        """
        c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        x, y, z = axis
        return np.array([
            [c + x*x*(1-c), x*y*(1-c) - z*s, x*z*(1-c) + y*s],
            [y*x*(1-c) + z*s, c + y*y*(1-c), y*z*(1-c) - x*s],
            [z*x*(1-c) - y*s, z*y*(1-c) + x*s, c + z*z*(1-c)]
        ]) 