"""
Main Rubik's Cube class that manages the collection of cubies, rotations, and rendering.
"""

import numpy as np
import math
from OpenGL.GL import *
import config
from cubie import Cubie
from utils import logger

class RubiksCube:
    """Manages the collection of cubies, rotations, and rendering."""
    
    def __init__(self, n=None):
        """
        Initialize the Rubik's Cube.
        
        Args:
            n (int): Cube size. If None, uses config.CUBE_SIZE
        """
        self.n = n if n is not None else config.CUBE_SIZE
        
        # Margin helps calculate coordinates from -X to +X
        margin = (self.n - 1) / 2.0
        
        # Create the list of cubies in their initial positions
        self.cubies = [Cubie((x, y, z), self.n)
                       for x in np.linspace(-margin, margin, self.n)
                       for y in np.linspace(-margin, margin, self.n)
                       for z in np.linspace(-margin, margin, self.n)]

        # Animation state
        self.is_animating = False
        self.animation_cubies = []
        self.animation_axis = None
        self.animation_angle = 0
        self.animation_target_angle = 0

        # View rotation of the entire cube (controlled by user)
        self.view_rot_x = config.INITIAL_ROTATION_X
        self.view_rot_y = config.INITIAL_ROTATION_Y
        
        logger.info(f"🎲 {self.n}x{self.n} Rubik's Cube initialized")

    def get_rotation_matrix(self, angle, axis):
        """
        Generate a 4x4 rotation matrix for OpenGL.
        
        Args:
            angle (float): Rotation angle in degrees
            axis (str): Rotation axis ('x', 'y', 'z')
            
        Returns:
            numpy.ndarray: 4x4 rotation matrix
        """
        c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        if axis == 'x': 
            return np.array([[1, 0, 0, 0], [0, c,-s, 0], [0, s, c, 0], [0, 0, 0, 1]], dtype=float)
        if axis == 'y': 
            return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s,0, c, 0], [0, 0, 0, 1]], dtype=float)
        if axis == 'z': 
            return np.array([[c,-s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=float)
        # For safety, if axis is None (during animation), return identity matrix
        return np.identity(4)

    def start_move(self, axis, slice_index, direction):
        """
        Prepare a rotation animation if no other is in progress.
        
        Args:
            axis (str): Rotation axis ('x', 'y', 'z')
            slice_index (float): Index of the slice to rotate
            direction (int): Rotation direction (1 or -1)
        """
        if self.is_animating: 
            return

        self.is_animating = True
        self.animation_axis = axis
        self.animation_target_angle = 90 * direction
        self.animation_angle = 0
        
        # Select cubies that belong to the slice to rotate
        axis_map = {'x': 0, 'y': 1, 'z': 2}
        
        epsilon = 1e-6  # Use threshold for floating point comparison
        
        self.animation_cubies = [c for c in self.cubies if abs(c.pos[axis_map[axis]] - slice_index) < epsilon]
        
        logger.debug(f"🔄 Starting move: axis={axis}, slice={slice_index}, direction={direction}")

    def update_animation(self):
        """Advance animation one step and finish if target is reached."""
        if not self.is_animating: 
            return

        # Advance the angle
        self.animation_angle += config.ANIMATION_SPEED * np.sign(self.animation_target_angle)
        
        # If we've reached or passed the target angle, finish
        if abs(self.animation_angle) >= abs(self.animation_target_angle):
            self.animation_angle = self.animation_target_angle
            self.finish_move()

    def finish_move(self):
        """Finish animation by updating matrices and logical positions of cubies."""
        rot_matrix = self.get_rotation_matrix(self.animation_target_angle, self.animation_axis)
        
        for cubie in self.animation_cubies:
            # 1. Update permanent transformation matrix
            cubie.matrix = np.dot(rot_matrix, cubie.matrix)
            # 2. Update logical position for future rotations
            new_pos = np.dot(rot_matrix[:3, :3], cubie.pos)
            
            # Robust solution for all N:
            steps = np.linspace(-(self.n-1)/2, (self.n-1)/2, self.n)
            cubie.pos = np.array([
                steps[np.argmin(np.abs(steps - new_pos[0]))],
                steps[np.argmin(np.abs(steps - new_pos[1]))],
                steps[np.argmin(np.abs(steps - new_pos[2]))]
            ])
        
        # Reset animation state
        self.is_animating = False
        self.animation_cubies = []
        
        logger.debug("✅ Move finished")

    def draw(self):
        """Draw the entire cube, applying animations if necessary."""
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Camera positioning and rotation
        glTranslatef(0, 0, -config.CAMERA_DISTANCE_MULTIPLIER * self.n)
        glRotatef(self.view_rot_x, 1, 0, 0)
        glRotatef(self.view_rot_y, 0, 1, 0)
        
        self.update_animation()

        # Temporary animation matrix that will be applied to moving cubies
        anim_matrix = self.get_rotation_matrix(self.animation_angle, self.animation_axis) if self.is_animating else None
        
        for cubie in self.cubies:
            # If cubie is part of current animation, pass temporary matrix
            if cubie in self.animation_cubies:
                cubie.draw(anim_matrix)
            else:
                cubie.draw()
    
    def reset_to_solved(self):
        """Reset the cube to solved state."""
        margin = (self.n - 1) / 2.0
        self.cubies = [Cubie((x, y, z), self.n)
                       for x in np.linspace(-margin, margin, self.n)
                       for y in np.linspace(-margin, margin, self.n)
                       for z in np.linspace(-margin, margin, self.n)]
        
        # Reset view rotation
        self.view_rot_x = config.INITIAL_ROTATION_X
        self.view_rot_y = config.INITIAL_ROTATION_Y
        
        logger.info("✅ Cube reset to solved state") 