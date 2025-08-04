"""
Simplified Rubik's Cube implementation using 3x3 matrices for each face.
"""

import numpy as np
from sticker import Sticker
import config
from OpenGL.GLU import gluUnProject
from OpenGL.GL import glReadPixels, GL_DEPTH_COMPONENT, GL_FLOAT
from utils import logger

class Cube:
    def __init__(self, size=None):
        """
        Initialize a Rubik's Cube with the specified size.
        
        Args:
            size (int): Size of the cube (2, 3, 4, etc.). If None, uses config.CUBE_SIZE
        """
        self.size = size if size is not None else config.CUBE_SIZE
        # Single data structure: face -> size x size matrix of Sticker objects
        self.faces = {}  # Dictionary: face -> size x size matrix of Sticker objects
        self.selected_face = None
        self.initialize_cube()
    
    def initialize_cube(self):
        """Initialize the cube with stickers in solved state."""
        for face in config.FACE_NAMES:
            base_color = config.FACE_COLORS[face]
            self.faces[face] = []
            
            for i in range(self.size):
                face_row = []
                for j in range(self.size):
                    # Calculate 3D position for rendering
                    pos = self.calculate_sticker_position(face, i, j)
                    
                    # Create sticker with color and matrix coordinates
                    sticker = Sticker(base_color, pos, face, i, j)
                    
                    face_row.append(sticker)
                self.faces[face].append(face_row)
        
        logger.info(f"🎲 {self.size}x{self.size} Cube initialized with solved state")
    
    def calculate_sticker_position(self, face, i, j):
        """
        Calculate the 3D position of a sticker based on its face and grid position.
        
        Args:
            face (str): Face identifier ('U', 'D', 'F', 'B', 'L', 'R')
            i (int): Row index (0 to size-1)
            j (int): Column index (0 to size-1)
        
        Returns:
            tuple: (x, y, z) coordinates
        """
        # Calculate sticker spacing based on current parameters
        sticker_spacing = config.STICKER_SIZE * 2
        
        # Convert grid position to offset from center of face
        center_offset = (self.size - 1) / 2  # For 2x2: 0.5, for 3x3: 1, etc.
        offset_i = (i - center_offset) * sticker_spacing
        offset_j = (j - center_offset) * sticker_spacing
        
        # Get face configuration
        face_config = config.FACE_CONFIGS[face]
        center_x, center_y, center_z = face_config['center']
        
        # Apply mapping based on face
        if face in ['U', 'D']:
            # For D face, invert the row mapping (i) to fix visual representation
            if face == 'D':
                map_x, map_y, map_z = offset_j, 0, -offset_i  # Note the -offset_i
            else:
                map_x, map_y, map_z = offset_j, 0, offset_i
        elif face in ['F', 'B']:
            # For B face, invert the column mapping (j) to fix visual representation
            if face == 'B':
                map_x, map_y, map_z = -offset_j, -offset_i, 0  # Note the -offset_j
            else:
                map_x, map_y, map_z = offset_j, -offset_i, 0
        elif face in ['L', 'R']:
            # For R face, invert the column mapping (j) to fix visual representation
            if face == 'R':
                map_x, map_y, map_z = 0, -offset_i, -offset_j  # Note the -offset_j
            else:
                map_x, map_y, map_z = 0, -offset_i, offset_j
        
        return (center_x + map_x, center_y + map_y, center_z + map_z)
    
    def get_face_state(self, face):
        """
        Get the current state of a face as a matrix of position-color strings.
        
        Args:
            face (str): Face identifier ('U', 'D', 'F', 'B', 'L', 'R')
        
        Returns:
            list: Matrix of strings in format "i.j-Color"
        """
        if face not in self.faces:
            return []
        
        face_matrix = []
        for i in range(self.size):
            row = []
            for j in range(self.size):
                sticker = self.faces[face][i][j]
                position_color = f"{sticker.matrix_i}.{sticker.matrix_j}-{sticker.get_color()}"
                row.append(position_color)
            face_matrix.append(row)
        
        return face_matrix
    
    def print_cube_state(self):
        """Print the current state of the cube in a visual format."""
        if logger.debug_enabled:
            logger.debug(f"🎲 Current {self.size}x{self.size} Cube State:")
            logger.debug("=" * 50)
            
            for face in config.FACE_NAMES:
                logger.debug(f"{face} face:")
                face_state = self.get_face_state(face)
                for row in face_state:
                    logger.debug(f"  {row}")
            
            logger.debug("=" * 50)
    
    def _rotate_face_clockwise(self, face):
        """Rotate a matrix clockwise by changing colors instead of moving references."""
        # Save original colors before any changes
        original_colors = []
        for i in range(self.size):
            row_colors = []
            for j in range(self.size):
                row_colors.append(self.faces[face][i][j].get_color())
            original_colors.append(row_colors)
        
        # Apply clockwise rotation by changing colors
        for i in range(self.size):
            for j in range(self.size):
                # Clockwise: (i,j) -> (j, size-1-i)
                new_i = j
                new_j = self.size - 1 - i
                self.faces[face][new_i][new_j].set_color(original_colors[i][j])
    
    def _rotate_face_counterclockwise(self, face):
        """Rotate a matrix counterclockwise by changing colors instead of moving references."""
        # Save original colors before any changes
        original_colors = []
        for i in range(self.size):
            row_colors = []
            for j in range(self.size):
                row_colors.append(self.faces[face][i][j].get_color())
            original_colors.append(row_colors)
        
        # Apply counterclockwise rotation by changing colors
        for i in range(self.size):
            for j in range(self.size):
                # Counterclockwise: (i,j) -> (size-1-j, i)
                new_i = self.size - 1 - j
                new_j = i
                self.faces[face][new_i][new_j].set_color(original_colors[i][j])
    
    def rotate_face_matrix(self, face, direction):
        """Rotate the face matrix by 90 degrees."""
        if direction == "clockwise":
            self._rotate_face_clockwise(face)
        else:  # counterclockwise
            self._rotate_face_counterclockwise(face)
    
    def rotate_face(self, face, direction):
        """
        Rotate a face by 90 degrees.
        
        Args:
            face (str): Face to rotate ('U', 'D', 'F', 'B', 'L', 'R')
            direction (str): 'clockwise' or 'counterclockwise'
        """
        logger.info(f"🔄 Rotating face {face} {direction}")
        
        # Show cube state before rotation
        self.print_cube_state()
        
        # First: Update adjacent faces (move stickers between faces)
        self.update_adjacent_faces(face, direction)
        
        # Second: Rotate the face itself
        self.rotate_face_matrix(face, direction)
        
        # # Third: Update all sticker positions to match their new matrix positions
        # self.update_sticker_positions()
        
        # Show cube state after rotation
        self.print_cube_state()
        
        logger.info(f"✅ Face {face} rotated {direction}")
    
    def update_adjacent_faces(self, rotated_face, direction):
        """Update stickers on adjacent faces after a rotation."""
        
        if rotated_face == 'F':  # Front face
            if direction == "clockwise":
                self._rotate_F_clockwise()
            else:  # counterclockwise
                self._rotate_F_counterclockwise()
        
        elif rotated_face == 'B':  # Back face
            if direction == "clockwise":
                self._rotate_B_clockwise()
            else:  # counterclockwise
                self._rotate_B_counterclockwise()

        elif rotated_face == 'U':  # Up face
            if direction == "clockwise":
                self._rotate_U_clockwise()
            else:  # counterclockwise
                self._rotate_U_counterclockwise()
        
        elif rotated_face == 'D':  # Down face
            if direction == "clockwise":
                self._rotate_D_clockwise()
            else:  # counterclockwise
                self._rotate_D_counterclockwise()
        
        elif rotated_face == 'L':  # Down face
            if direction == "clockwise":
                self._rotate_L_clockwise()
            else:  # counterclockwise
                self._rotate_L_counterclockwise()

        elif rotated_face == 'R':  # Down face
            if direction == "clockwise":
                self._rotate_R_clockwise()
            else:  # counterclockwise
                self._rotate_R_counterclockwise()
    
    def _rotate_F_clockwise(self):
        """
        Rotate F face clockwise according to exact specifications from GIROS.md - extensible to any cube size.
        
        """
        # Save original colors before any changes
        U_colors = [self.faces['U'][self.size-1][j].get_color() for j in range(self.size)]
        R_colors = [self.faces['R'][i][0].get_color() for i in reversed(range(self.size))]
        D_colors = [self.faces['D'][0][j].get_color() for j in range(self.size)]
        L_colors = [self.faces['L'][i][self.size-1].get_color() for i in reversed(range(self.size))]
                
        for j in range(self.size):
            self.faces['R'][j][0].set_color(U_colors[j])
        for i in range(self.size):
            self.faces['D'][0][i].set_color(R_colors[i])
        for i in range(self.size):
            self.faces['L'][i][self.size-1].set_color(D_colors[i])
        for j in range(self.size):
            self.faces['U'][self.size-1][j].set_color(L_colors[j])
    
    def _rotate_F_counterclockwise(self):
        """
        Rotate F face counterclockwise according to exact specifications - extensible to any cube size.
        
        """
        # Save original colors before any changes
        U_colors = [self.faces['U'][self.size-1][j].get_color() for j in reversed(range(self.size))]
        R_colors = [self.faces['R'][i][0].get_color() for i in range(self.size)]
        D_colors = [self.faces['D'][0][j].get_color() for j in reversed(range(self.size))]
        L_colors = [self.faces['L'][i][self.size-1].get_color() for i in range(self.size)]
        
        # Apply the exact movements from specifications
        for i in range(self.size):
            self.faces['R'][i][0].set_color(D_colors[i])
        for j in range(self.size):
            self.faces['D'][0][j].set_color(L_colors[j])
        for i in range(self.size):
            self.faces['L'][i][self.size-1].set_color(U_colors[i])
        for j in range(self.size):
            self.faces['U'][self.size-1][j].set_color(R_colors[j])
    
    def _rotate_B_clockwise(self):
        """
        Rotate B face clockwise according to exact specifications from GIROS.md - extensible to any cube size.
        
        """
        # Save original colors before any changes
        U_colors = [self.faces['U'][0][j].get_color() for j in reversed(range(self.size))]
        R_colors = [self.faces['R'][i][self.size-1].get_color() for i in range(self.size)]
        D_colors = [self.faces['D'][self.size-1][j].get_color() for j in reversed(range(self.size))]
        L_colors = [self.faces['L'][i][0].get_color() for i in range(self.size)]
                
        for i in range(self.size):
            self.faces['R'][i][self.size-1].set_color(D_colors[i])
        for j in range(self.size):
            self.faces['D'][self.size-1][j].set_color(L_colors[j])
        for i in range(self.size):
            self.faces['L'][i][0].set_color(U_colors[i])
        for j in range(self.size):
            self.faces['U'][0][j].set_color(R_colors[j])
    
    def _rotate_B_counterclockwise(self):
        """
        Rotate B face counterclockwise according to exact specifications from GIROS.md - extensible to any cube size.
        """
        # Save original colors before any changes
        U_colors = [self.faces['U'][0][j].get_color() for j in range(self.size)]
        R_colors = [self.faces['R'][i][self.size-1].get_color() for i in reversed(range(self.size))]
        D_colors = [self.faces['D'][self.size-1][j].get_color() for j in range(self.size)]
        L_colors = [self.faces['L'][i][0].get_color() for i in reversed(range(self.size))]
                
        for i in range(self.size):
            self.faces['R'][i][self.size-1].set_color(U_colors[i])
        for j in range(self.size):
            self.faces['D'][self.size-1][j].set_color(R_colors[j])
        for i in range(self.size):
            self.faces['L'][i][0].set_color(D_colors[i])
        for j in range(self.size):
            self.faces['U'][0][j].set_color(L_colors[j])

    def _rotate_U_clockwise(self):
        """
        Rotate U face clockwise according to exact specifications - extensible to any cube size.
        """
        # Save original colors before any changes
        F_colors = [self.faces['F'][0][j].get_color() for j in range(self.size)]
        R_colors = [self.faces['R'][0][j].get_color() for j in range(self.size)]
        B_colors = [self.faces['B'][0][j].get_color() for j in range(self.size)]
        L_colors = [self.faces['L'][0][j].get_color() for j in range(self.size)]

        # Apply the exact movements from specifications
        for j in range(self.size):
            self.faces['F'][0][j].set_color(R_colors[j])
        for j in range(self.size):
            self.faces['R'][0][j].set_color(B_colors[j])
        for j in range(self.size):
            self.faces['B'][0][j].set_color(L_colors[j])
        for j in range(self.size):
            self.faces['L'][0][j].set_color(F_colors[j])
        
    
    def _rotate_U_counterclockwise(self):
        """
        Rotate U face counterclockwise according to exact specifications - extensible to any cube size.
        """
        # Save original colors before any changes
        F_colors = [self.faces['F'][0][j].get_color() for j in range(self.size)]
        R_colors = [self.faces['R'][0][j].get_color() for j in range(self.size)]
        B_colors = [self.faces['B'][0][j].get_color() for j in range(self.size)]
        L_colors = [self.faces['L'][0][j].get_color() for j in range(self.size)]
        
        # Apply the exact movements from specifications
        for j in range(self.size):
            self.faces['F'][0][j].set_color(L_colors[j])
        for j in range(self.size):
            self.faces['R'][0][j].set_color(F_colors[j])
        for j in range(self.size):
            self.faces['B'][0][j].set_color(R_colors[j])
        for j in range(self.size):
            self.faces['L'][0][j].set_color(B_colors[j])  
    
    def _rotate_D_clockwise(self):
        """
        Rotate D face clockwise according to exact specifications - extensible to any cube size.
        """
        # Save original colors before any changes
        F_colors = [self.faces['F'][self.size-1][j].get_color() for j in range(self.size)]
        R_colors = [self.faces['R'][self.size-1][j].get_color() for j in range(self.size)]
        B_colors = [self.faces['B'][self.size-1][j].get_color() for j in range(self.size)]
        L_colors = [self.faces['L'][self.size-1][j].get_color() for j in range(self.size)]
        
        # Apply the exact movements from specifications
        for j in range(self.size):
            self.faces['F'][self.size-1][j].set_color(L_colors[j])
        for j in range(self.size):
            self.faces['R'][self.size-1][j].set_color(F_colors[j])
        for j in range(self.size):
            self.faces['B'][self.size-1][j].set_color(R_colors[j])
        for j in range(self.size):
            self.faces['L'][self.size-1][j].set_color(B_colors[j])
    
    def _rotate_D_counterclockwise(self):
        """
        Rotate D face counterclockwise according to exact specifications - extensible to any cube size.
        """
        # Save original colors before any changes
        F_colors = [self.faces['F'][self.size-1][j].get_color() for j in range(self.size)]
        R_colors = [self.faces['R'][self.size-1][j].get_color() for j in range(self.size)]
        L_colors = [self.faces['L'][self.size-1][j].get_color() for j in range(self.size)]
        B_colors = [self.faces['B'][self.size-1][j].get_color() for j in range(self.size)]
        
        
        # Apply the exact movements from specifications
        for j in range(self.size):
            self.faces['F'][self.size-1][j].set_color(R_colors[j])
        for j in range(self.size):
            self.faces['R'][self.size-1][j].set_color(B_colors[j])
        for j in range(self.size):
            self.faces['B'][self.size-1][j].set_color(L_colors[j])
        for j in range(self.size):
            self.faces['L'][self.size-1][j].set_color(F_colors[j])

    def _rotate_L_clockwise(self):
        """
        Rotate L face clockwise according to exact specifications - extensible to any cube size.
        """
        # Save original colors before any changes
        F_colors = [self.faces['F'][i][0].get_color() for i in range(self.size)]
        U_colors = [self.faces['U'][i][0].get_color() for i in range(self.size)]
        B_colors = [self.faces['B'][i][self.size-1].get_color() for i in reversed(range(self.size))]
        D_colors = [self.faces['D'][i][0].get_color() for i in reversed(range(self.size))]
        
        # Apply the exact movements from specifications
        for i in range(self.size):
            self.faces['F'][i][0].set_color(U_colors[i])
        for i in range(self.size):
            self.faces['U'][i][0].set_color(B_colors[i])
        for i in range(self.size):
            self.faces['B'][i][self.size-1].set_color(D_colors[i])
        for i in range(self.size):
            self.faces['D'][i][0].set_color(F_colors[i])

    def _rotate_L_counterclockwise(self):
        """
        Rotate L face counterclockwise according to exact specifications - extensible to any cube size.
        """
        # Save original colors before any changes
        F_colors = [self.faces['F'][i][0].get_color() for i in range(self.size)]
        U_colors = [self.faces['U'][i][0].get_color() for i in reversed(range(self.size))]
        B_colors = [self.faces['B'][i][self.size-1].get_color() for i in reversed(range(self.size))]
        D_colors = [self.faces['D'][i][0].get_color() for i in range(self.size)]
        
        # Apply the exact movements from specifications
        for i in range(self.size):
            self.faces['F'][i][0].set_color(D_colors[i])
        for i in range(self.size):
            self.faces['U'][i][0].set_color(F_colors[i])
        for i in range(self.size):
            self.faces['B'][i][self.size-1].set_color(U_colors[i])
        for i in range(self.size):
            self.faces['D'][i][0].set_color(B_colors[i])
    
    def _rotate_R_clockwise(self):
        """
        Rotate R face clockwise according to exact specifications - extensible to any cube size.
        """
        # Save original colors before any changes
        F_colors = [self.faces['F'][i][self.size-1].get_color() for i in range(self.size)]
        U_colors = [self.faces['U'][i][self.size-1].get_color() for i in reversed(range(self.size))]
        B_colors = [self.faces['B'][i][0].get_color() for i in reversed(range(self.size))]
        D_colors = [self.faces['D'][i][self.size-1].get_color() for i in range(self.size)]
        
        # Apply the exact movements from specifications
        for i in range(self.size):
            self.faces['F'][i][self.size-1].set_color(D_colors[i])
        for i in range(self.size):
            self.faces['U'][i][self.size-1].set_color(F_colors[i])
        for i in range(self.size):
            self.faces['B'][i][0].set_color(U_colors[i])
        for i in range(self.size):
            self.faces['D'][i][self.size-1].set_color(B_colors[i])

    def _rotate_R_counterclockwise(self):
        """
        Rotate R face counterclockwise according to exact specifications - extensible to any cube size.
        """
        # Save original colors before any changes
        F_colors = [self.faces['F'][i][self.size-1].get_color() for i in range(self.size)]
        U_colors = [self.faces['U'][i][self.size-1].get_color() for i in (range(self.size))]
        B_colors = [self.faces['B'][i][0].get_color() for i in reversed(range(self.size))]
        D_colors = [self.faces['D'][i][self.size-1].get_color() for i in reversed(range(self.size))]
        
        # Apply the exact movements from specifications
        for i in range(self.size):
            self.faces['F'][i][self.size-1].set_color(U_colors[i])
        for i in range(self.size):
            self.faces['U'][i][self.size-1].set_color(B_colors[i])
        for i in range(self.size):
            self.faces['B'][i][0].set_color(D_colors[i])
        for i in range(self.size):
            self.faces['D'][i][self.size-1].set_color(F_colors[i])

    def set_selected_face(self, face):
        """Set the selected face for highlighting."""
        # Clear previous selection
        if self.selected_face:
            self._clear_face_selection(self.selected_face)
        
        # Set new selection
        self.selected_face = face
        if face:
            self._set_face_selection(face)
    
    def _clear_face_selection(self, face):
        """Clear selection for a face and its adjacent stickers."""
        # Clear main face
        for i in range(self.size):
            for j in range(self.size):
                self.faces[face][i][j].set_selected(False)
                self.faces[face][i][j].set_adjacent(False)
        
        # Clear adjacent stickers
        adjacent_stickers = self._get_adjacent_stickers_for_face(face)
        for sticker in adjacent_stickers:
            sticker.set_selected(False)
            sticker.set_adjacent(False)
    
    def _set_face_selection(self, face):
        """Set selection for a face and its adjacent stickers."""
        # Set main face
        for i in range(self.size):
            for j in range(self.size):
                self.faces[face][i][j].set_selected(True)
                self.faces[face][i][j].set_adjacent(False)
        
        # Set adjacent stickers
        adjacent_stickers = self._get_adjacent_stickers_for_face(face)
        for sticker in adjacent_stickers:
            sticker.set_selected(True)
            sticker.set_adjacent(True)
    
    def _get_adjacent_stickers_for_face(self, face):
        """Get stickers from adjacent faces that will move during rotation."""
        adjacent_stickers = []
        
        if face == 'F':  # Front face
            # Top row of U face
            for j in range(self.size):
                adjacent_stickers.append(self.faces['U'][self.size-1][j])
            
            # Left column of R face
            for i in range(self.size):
                adjacent_stickers.append(self.faces['R'][i][0])
            
            # Bottom row of D face
            for j in range(self.size):
                adjacent_stickers.append(self.faces['D'][0][j])
            
            # Right column of L face
            for i in range(self.size):
                adjacent_stickers.append(self.faces['L'][i][self.size-1])
        
        elif face == 'U':  # Up face
            # Top row of F face
            for j in range(self.size):
                adjacent_stickers.append(self.faces['F'][0][j])
            
            # Top row of L face
            for j in range(self.size):
                adjacent_stickers.append(self.faces['L'][0][j])
            
            # Top row of B face
            for j in range(self.size):
                adjacent_stickers.append(self.faces['B'][0][j])
            
            # Top row of R face
            for j in range(self.size):
                adjacent_stickers.append(self.faces['R'][0][j])
        
        elif face == 'D':  # Down face
            # Bottom row of F face
            for j in range(self.size):
                adjacent_stickers.append(self.faces['F'][self.size-1][j])
            
            # Bottom row of L face
            for j in range(self.size):
                adjacent_stickers.append(self.faces['L'][self.size-1][j])
            
            # Bottom row of B face
            for j in range(self.size):
                adjacent_stickers.append(self.faces['B'][self.size-1][j])
            
            # Bottom row of R face
            for j in range(self.size):
                adjacent_stickers.append(self.faces['R'][self.size-1][j])
        
        elif face == 'L':  # Left face
            # Left column of U face
            for i in range(self.size):
                adjacent_stickers.append(self.faces['U'][i][0])
            
            # Left column of F face
            for i in range(self.size):
                adjacent_stickers.append(self.faces['F'][i][0])
            
            # Left column of D face
            for i in range(self.size):
                adjacent_stickers.append(self.faces['D'][i][0])
            
            # Right column of B face
            for i in range(self.size):
                adjacent_stickers.append(self.faces['B'][i][self.size-1])
        
        elif face == 'R':  # Right face
            # Right column of U face
            for i in range(self.size):
                adjacent_stickers.append(self.faces['U'][i][self.size-1])
            
            # Right column of F face
            for i in range(self.size):
                adjacent_stickers.append(self.faces['F'][i][self.size-1])
            
            # Right column of D face
            for i in range(self.size):
                adjacent_stickers.append(self.faces['D'][i][self.size-1])
            
            # Left column of B face
            for i in range(self.size):
                adjacent_stickers.append(self.faces['B'][i][0])
        
        elif face == 'B':  # Back face
            # Top row of U face
            for j in range(self.size):
                adjacent_stickers.append(self.faces['U'][0][j])
            
            # Right column of R face
            for i in range(self.size):
                adjacent_stickers.append(self.faces['R'][i][self.size-1])
            
            # Bottom row of D face
            for j in range(self.size):
                adjacent_stickers.append(self.faces['D'][self.size-1][j])
            
            # Left column of L face
            for i in range(self.size):
                adjacent_stickers.append(self.faces['L'][i][0])
        
        return adjacent_stickers
    
    def get_cube_state(self):
        """Get the current state of the cube."""
        state = {}
        for face in config.FACE_NAMES:
            state[face] = []
            for i in range(self.size):
                for j in range(self.size):
                    sticker = self.faces[face][i][j]
                    state[face].append({
                        'color': sticker.get_color(),
                        'position': sticker.get_position(),
                        'selected': sticker.is_sticker_selected()
                    })
        return state
    
    def reset_to_solved(self):
        """Reset the cube to solved state."""
        self.initialize_cube()
        logger.info("✓ Cube reset to solved state")

    def get_clicked_sticker(self, mouse_pos, viewport, modelview, projection):
        """
        Get the sticker that was clicked using ray casting.
        
        Args:
            mouse_pos (tuple): (x, y) screen coordinates
            viewport (tuple): OpenGL viewport
            modelview (tuple): OpenGL modelview matrix
            projection (tuple): OpenGL projection matrix
        
        Returns:
            tuple: (sticker, face, i, j) or None if no sticker clicked
        """
        x, y = mouse_pos
        y = viewport[3] - y  # Flip Y coordinate
        
        # Get the depth at the clicked pixel
        z = glReadPixels(x, y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)[0][0]
        
        # Unproject to get world coordinates
        world_pos = gluUnProject(x, y, z, modelview, projection, viewport)
        
        if world_pos is None:
            logger.warning("⚠️ Failed to unproject mouse coordinates")
            return None
        
        logger.debug(f"Mouse click at screen ({mouse_pos[0]}, {mouse_pos[1]}) -> world: {world_pos}")
        
        # Find the closest sticker to the clicked world position
        closest_sticker = None
        closest_distance = float('inf')
        
        for face in config.FACE_NAMES:
            for i in range(self.size):
                for j in range(self.size):
                    sticker = self.faces[face][i][j]
                    sticker_pos = sticker.get_position()
                    
                    # Calculate distance from click to sticker center
                    distance = ((world_pos[0] - sticker_pos[0])**2 + 
                               (world_pos[1] - sticker_pos[1])**2 + 
                               (world_pos[2] - sticker_pos[2])**2)**0.5
                    
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_sticker = (sticker, face, i, j)
        
        # If we found a sticker within reasonable distance
        if closest_distance < config.STICKER_SIZE * 2:
            logger.debug(f"Selected sticker at distance {closest_distance:.3f}")
            return closest_sticker
        else:
            logger.debug(f"No sticker found within reasonable distance. Closest: {closest_distance:.3f}")