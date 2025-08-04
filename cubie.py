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
    
    def set_interior_color(self, color):
        """Set the interior color of the cubie."""
        # Find all faces that are not exterior faces (i.e., interior faces)
        for normal, face_name in config.FACES.items():
            if self.colors[face_name] == config.COLORS['INSIDE']:
                self.colors[face_name] = color
            # Also reset any faces that were previously set to selection color
            elif self.colors[face_name] == config.SELECTION_COLOR:
                self.colors[face_name] = color

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
        
        glBegin(GL_QUADS)
        s = config.CUBIE_SIZE / 2.0
        for normal, face_name in config.FACES.items():
            # Use pre-assigned color
            glColor3fv(self.colors[face_name])
            
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

        glPopMatrix()
    
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