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
    def __init__(self, size=3):
        """
        Initialize a Rubik's Cube with the specified size.
        
        Args:
            size (int): Size of the cube (2, 3, 4, etc.)
        """
        self.size = size
        self.cube = {}  # Dictionary: face -> 3x3 matrix of colors
        self.selected_face = None
        self.sticker_objects = {}  # Dictionary: face -> 3x3 matrix of Sticker objects for rendering
        self.initialize_cube()
    
    def initialize_cube(self):
        """Initialize the cube with colors in solved state."""
        # Initialize each face with 3x3 matrix of colors
        for face in config.FACE_NAMES:
            base_color = config.FACE_COLORS[face]
            self.cube[face] = [[base_color for _ in range(3)] for _ in range(3)]
            
            # Create corresponding Sticker objects for rendering
            self.sticker_objects[face] = []
            for i in range(3):
                face_stickers = []
                for j in range(3):
                    # Calculate position within the face
                    pos = self.calculate_sticker_position(face, i, j)
                    
                    # Create unique color for each position to see rotation clearly
                    unique_color = f"{base_color}{i}{j}"  # e.g., "R00", "R01", "R02", etc.
                    
                    sticker = Sticker(unique_color, pos, face)
                    face_stickers.append(sticker)
                self.sticker_objects[face].append(face_stickers)
        
        logger.info("🎲 Cube initialized with solved state")
    
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
    

    
    def update_sticker_objects(self):
        """Update sticker objects to match the current cube state."""
        for face in config.FACE_NAMES:
            for i in range(3):
                for j in range(3):
                    color = self.cube[face][i][j]
                    sticker = self.sticker_objects[face][i][j]
                    sticker.set_color(color)
        

    
    def print_cube_state(self):
        """Print the current state of the cube in a visual format."""
        logger.debug("🎲 Current Cube State:")
        logger.debug("=" * 50)
        
        for face in config.FACE_NAMES:
            logger.debug(f"{face} face:")
            for i, row in enumerate(self.cube[face]):
                # Create row with position information
                position_row = []
                for j, color in enumerate(row):
                    position_row.append(f"{i}.{j}-{color}")
                logger.debug(f"  {position_row}")
        
        logger.debug("=" * 50)
    
    def _rotate_face_clockwise(self, face):
        """Rotate a 3x3 matrix clockwise."""
        matrix = self.cube[face]
        new_matrix = [row[:] for row in matrix]  # Deep copy
        
        # Corners
        new_matrix[0][0] = matrix[2][0]
        new_matrix[0][2] = matrix[0][0]
        new_matrix[2][2] = matrix[0][2]
        new_matrix[2][0] = matrix[2][2]
        
        # Edges
        new_matrix[0][1] = matrix[1][0]
        new_matrix[1][2] = matrix[0][1]
        new_matrix[2][1] = matrix[1][2]
        new_matrix[1][0] = matrix[2][1]
        
        return new_matrix
    
    def _rotate_face_counterclockwise(self, face):
        """Rotate a 3x3 matrix counterclockwise."""
        matrix = self.cube[face]
        new_matrix = [row[:] for row in matrix]  # Deep copy
        
        # Corners
        new_matrix[2][0] = matrix[0][0]
        new_matrix[0][0] = matrix[0][2]
        new_matrix[0][2] = matrix[2][2]
        new_matrix[2][2] = matrix[2][0]
        
        # Edges
        new_matrix[1][0] = matrix[0][1]
        new_matrix[0][1] = matrix[1][2]
        new_matrix[1][2] = matrix[2][1]
        new_matrix[2][1] = matrix[1][0]
        
        return new_matrix
    
    def rotate_face_matrix(self, face, direction):
        """Rotate the 3x3 matrix of a face by 90 degrees."""
        if direction == "clockwise":
            self.cube[face] = self._rotate_face_clockwise(face)
        else:  # counterclockwise
            self.cube[face] = self._rotate_face_counterclockwise(face)
    

    
    def _rotate_F_clockwise(self):
        """Rotate F face clockwise and update adjacent faces."""
        # Save the bottom row of U
        bottom_row_U = self.cube['U'][2][:]
        
        # Left face (right column) -> Up face (bottom row)
        self.cube['U'][2] = [self.cube['L'][2][2], self.cube['L'][1][2], self.cube['L'][0][2]]
        
        # Down face (top row) -> Left face (right column)
        top_row_D = self.cube['D'][0][:]
        self.cube['L'][0][2] = top_row_D[0]
        self.cube['L'][1][2] = top_row_D[1]
        self.cube['L'][2][2] = top_row_D[2]
        
        # Right face (left column) -> Down face (top row)
        self.cube['D'][0] = [self.cube['R'][2][0], self.cube['R'][1][0], self.cube['R'][0][0]]
        
        # (Saved) Up face -> Right face (left column)
        self.cube['R'][0][0] = bottom_row_U[0]
        self.cube['R'][1][0] = bottom_row_U[1]
        self.cube['R'][2][0] = bottom_row_U[2]
    
    def _rotate_F_counterclockwise(self):
        """Rotate F face counterclockwise and update adjacent faces."""
        # Save the bottom row of U
        bottom_row_U = self.cube['U'][2][:]
        
        # Right face (left column) -> Up face
        self.cube['U'][2] = [self.cube['R'][0][0], self.cube['R'][1][0], self.cube['R'][2][0]]
        
        # Down face -> Right face
        top_row_D = self.cube['D'][0][:]
        self.cube['R'][0][0] = top_row_D[2]
        self.cube['R'][1][0] = top_row_D[1]
        self.cube['R'][2][0] = top_row_D[0]
        
        # Left face -> Down face
        self.cube['D'][0] = [self.cube['L'][0][2], self.cube['L'][1][2], self.cube['L'][2][2]]
        
        # (Saved) Up face -> Left face
        self.cube['L'][0][2] = bottom_row_U[2]
        self.cube['L'][1][2] = bottom_row_U[1]
        self.cube['L'][2][2] = bottom_row_U[0]
    
    def _rotate_U_clockwise(self):
        """Rotate U face clockwise and update adjacent faces."""
        # Save the top row of F
        top_row_F = self.cube['F'][0][:]
        
        self.cube['F'][0] = self.cube['L'][0]
        self.cube['L'][0] = self.cube['B'][0]
        self.cube['B'][0] = self.cube['R'][0]
        self.cube['R'][0] = top_row_F
    
    def _rotate_U_counterclockwise(self):
        """Rotate U face counterclockwise and update adjacent faces."""
        # Save the top row of F
        top_row_F = self.cube['F'][0][:]
        
        self.cube['F'][0] = self.cube['R'][0]
        self.cube['R'][0] = self.cube['B'][0]
        self.cube['B'][0] = self.cube['L'][0]
        self.cube['L'][0] = top_row_F
    
    def _rotate_D_clockwise(self):
        """Rotate D face clockwise and update adjacent faces."""
        # Save the bottom row of F
        bottom_row_F = self.cube['F'][2][:]
        
        self.cube['F'][2] = self.cube['L'][2]
        self.cube['L'][2] = self.cube['B'][2]
        self.cube['B'][2] = self.cube['R'][2]
        self.cube['R'][2] = bottom_row_F
    
    def _rotate_D_counterclockwise(self):
        """Rotate D face counterclockwise and update adjacent faces."""
        # Save the bottom row of F
        bottom_row_F = self.cube['F'][2][:]
        
        self.cube['F'][2] = self.cube['R'][2]
        self.cube['R'][2] = self.cube['B'][2]
        self.cube['B'][2] = self.cube['L'][2]
        self.cube['L'][2] = bottom_row_F
    
    def _rotate_L_clockwise(self):
        """Rotate L face clockwise and update adjacent faces."""
        # Save the left column of U
        left_col_U = [self.cube['U'][0][0], self.cube['U'][1][0], self.cube['U'][2][0]]
        
        # Back face -> Up face
        self.cube['U'][0][0] = self.cube['B'][2][2]
        self.cube['U'][1][0] = self.cube['B'][1][2]
        self.cube['U'][2][0] = self.cube['B'][0][2]
        
        # Down face -> Back face
        left_col_D = [self.cube['D'][0][0], self.cube['D'][1][0], self.cube['D'][2][0]]
        self.cube['B'][0][2] = left_col_D[0]
        self.cube['B'][1][2] = left_col_D[1]
        self.cube['B'][2][2] = left_col_D[2]
        
        # Front face -> Down face
        left_col_F = [self.cube['F'][0][0], self.cube['F'][1][0], self.cube['F'][2][0]]
        self.cube['D'][0][0] = left_col_F[0]
        self.cube['D'][1][0] = left_col_F[1]
        self.cube['D'][2][0] = left_col_F[2]
        
        # (Saved) Up face -> Front face
        self.cube['F'][0][0] = left_col_U[0]
        self.cube['F'][1][0] = left_col_U[1]
        self.cube['F'][2][0] = left_col_U[2]
    
    def _rotate_L_counterclockwise(self):
        """Rotate L face counterclockwise and update adjacent faces."""
        # Save the left column of U
        left_col_U = [self.cube['U'][0][0], self.cube['U'][1][0], self.cube['U'][2][0]]
        
        # Front face -> Up face
        self.cube['U'][0][0] = self.cube['F'][0][0]
        self.cube['U'][1][0] = self.cube['F'][1][0]
        self.cube['U'][2][0] = self.cube['F'][2][0]
        
        # Down face -> Front face
        left_col_D = [self.cube['D'][0][0], self.cube['D'][1][0], self.cube['D'][2][0]]
        self.cube['F'][0][0] = left_col_D[0]
        self.cube['F'][1][0] = left_col_D[1]
        self.cube['F'][2][0] = left_col_D[2]
        
        # Back face -> Down face
        self.cube['D'][0][0] = self.cube['B'][0][2]
        self.cube['D'][1][0] = self.cube['B'][1][2]
        self.cube['D'][2][0] = self.cube['B'][2][2]
        
        # (Saved) Up face -> Back face
        self.cube['B'][0][2] = left_col_U[2]
        self.cube['B'][1][2] = left_col_U[1]
        self.cube['B'][2][2] = left_col_U[0]
    
    def _rotate_R_clockwise(self):
        """Rotate R face clockwise and update adjacent faces."""
        # Save the right column of U
        right_col_U = [self.cube['U'][0][2], self.cube['U'][1][2], self.cube['U'][2][2]]
        
        # Front face -> Up face
        self.cube['U'][0][2] = self.cube['F'][0][2]
        self.cube['U'][1][2] = self.cube['F'][1][2]
        self.cube['U'][2][2] = self.cube['F'][2][2]
        
        # Down face -> Front face
        right_col_D = [self.cube['D'][0][2], self.cube['D'][1][2], self.cube['D'][2][2]]
        self.cube['F'][0][2] = right_col_D[0]
        self.cube['F'][1][2] = right_col_D[1]
        self.cube['F'][2][2] = right_col_D[2]
        
        # Back face -> Down face
        self.cube['D'][0][2] = self.cube['B'][2][0]
        self.cube['D'][1][2] = self.cube['B'][1][0]
        self.cube['D'][2][2] = self.cube['B'][0][0]
        
        # (Saved) Up face -> Back face
        self.cube['B'][0][0] = right_col_U[2]
        self.cube['B'][1][0] = right_col_U[1]
        self.cube['B'][2][0] = right_col_U[0]
    
    def _rotate_R_counterclockwise(self):
        """Rotate R face counterclockwise and update adjacent faces."""
        # Save the right column of U
        right_col_U = [self.cube['U'][0][2], self.cube['U'][1][2], self.cube['U'][2][2]]
        
        # Back face -> Up face
        self.cube['U'][0][2] = self.cube['B'][2][0]
        self.cube['U'][1][2] = self.cube['B'][1][0]
        self.cube['U'][2][2] = self.cube['B'][0][0]
        
        # Down face -> Back face
        right_col_D = [self.cube['D'][0][2], self.cube['D'][1][2], self.cube['D'][2][2]]
        self.cube['B'][0][0] = right_col_D[2]
        self.cube['B'][1][0] = right_col_D[1]
        self.cube['B'][2][0] = right_col_D[0]
        
        # Front face -> Down face
        right_col_F = [self.cube['F'][0][2], self.cube['F'][1][2], self.cube['F'][2][2]]
        self.cube['D'][0][2] = right_col_F[0]
        self.cube['D'][1][2] = right_col_F[1]
        self.cube['D'][2][2] = right_col_F[2]
        
        # (Saved) Up face -> Front face
        self.cube['F'][0][2] = right_col_U[0]
        self.cube['F'][1][2] = right_col_U[1]
        self.cube['F'][2][2] = right_col_U[2]
    
    def _rotate_B_clockwise(self):
        """Rotate B face clockwise and update adjacent faces."""
        # Save the top row of U
        top_row_U = self.cube['U'][0][:]
        
        # Right face -> Up face
        self.cube['U'][0] = [self.cube['R'][0][2], self.cube['R'][1][2], self.cube['R'][2][2]]
        
        # Down face -> Right face
        bottom_row_D = self.cube['D'][2][:]
        self.cube['R'][0][2] = bottom_row_D[2]
        self.cube['R'][1][2] = bottom_row_D[1]
        self.cube['R'][2][2] = bottom_row_D[0]
        
        # Left face -> Down face
        self.cube['D'][2] = [self.cube['L'][2][0], self.cube['L'][1][0], self.cube['L'][0][0]]
        
        # (Saved) Up face -> Left face
        self.cube['L'][0][0] = top_row_U[2]
        self.cube['L'][1][0] = top_row_U[1]
        self.cube['L'][2][0] = top_row_U[0]
    
    def _rotate_B_counterclockwise(self):
        """Rotate B face counterclockwise and update adjacent faces."""
        # Save the top row of U
        top_row_U = self.cube['U'][0][:]
        
        # Left face -> Up face
        self.cube['U'][0] = [self.cube['L'][2][0], self.cube['L'][1][0], self.cube['L'][0][0]]
        
        # Down face -> Left face
        bottom_row_D = self.cube['D'][2][:]
        self.cube['L'][0][0] = bottom_row_D[0]
        self.cube['L'][1][0] = bottom_row_D[1]
        self.cube['L'][2][0] = bottom_row_D[2]
        
        # Right face -> Down face
        self.cube['D'][2] = [self.cube['R'][2][2], self.cube['R'][1][2], self.cube['R'][0][2]]
        
        # (Saved) Up face -> Right face
        self.cube['R'][0][2] = top_row_U[0]
        self.cube['R'][1][2] = top_row_U[1]
        self.cube['R'][2][2] = top_row_U[2]
    
    def update_adjacent_faces(self, rotated_face, direction):
        """Update stickers on adjacent faces after a rotation."""
        
        if rotated_face == 'F':  # Front face
            if direction == "clockwise":
                self._rotate_F_clockwise()
            else:  # counterclockwise
                self._rotate_F_counterclockwise()
        
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
        
        elif rotated_face == 'L':  # Left face
            if direction == "clockwise":
                self._rotate_L_clockwise()
            else:  # counterclockwise
                self._rotate_L_counterclockwise()
        
        elif rotated_face == 'R':  # Right face
            if direction == "clockwise":
                self._rotate_R_clockwise()
            else:  # counterclockwise
                self._rotate_R_counterclockwise()
        
        elif rotated_face == 'B':  # Back face
            if direction == "clockwise":
                self._rotate_B_clockwise()
            else:  # counterclockwise
                self._rotate_B_counterclockwise()
        

    
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
        
        # Update sticker objects to match new state
        self.update_sticker_objects()
        
        # Show cube state after rotation
        self.print_cube_state()
        
        logger.info(f"✅ Face {face} rotated {direction}")
    
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
        for i in range(3):
            for j in range(3):
                self.sticker_objects[face][i][j].set_selected(False)
                self.sticker_objects[face][i][j].set_adjacent(False)
        
        # Clear adjacent stickers
        adjacent_stickers = self._get_adjacent_stickers_for_face(face)
        for sticker in adjacent_stickers:
            sticker.set_selected(False)
            sticker.set_adjacent(False)
    
    def _set_face_selection(self, face):
        """Set selection for a face and its adjacent stickers."""
        # Set main face
        for i in range(3):
            for j in range(3):
                self.sticker_objects[face][i][j].set_selected(True)
                self.sticker_objects[face][i][j].set_adjacent(False)
        
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
            for j in range(3):
                adjacent_stickers.append(self.sticker_objects['U'][2][j])
            
            # Left column of R face
            for i in range(3):
                adjacent_stickers.append(self.sticker_objects['R'][i][0])
            
            # Bottom row of D face
            for j in range(3):
                adjacent_stickers.append(self.sticker_objects['D'][0][j])
            
            # Right column of L face
            for i in range(3):
                adjacent_stickers.append(self.sticker_objects['L'][i][2])
        
        elif face == 'U':  # Up face
            # Top row of F face
            for j in range(3):
                adjacent_stickers.append(self.sticker_objects['F'][0][j])
            
            # Top row of L face
            for j in range(3):
                adjacent_stickers.append(self.sticker_objects['L'][0][j])
            
            # Top row of B face
            for j in range(3):
                adjacent_stickers.append(self.sticker_objects['B'][0][j])
            
            # Top row of R face
            for j in range(3):
                adjacent_stickers.append(self.sticker_objects['R'][0][j])
        
        elif face == 'D':  # Down face
            # Bottom row of F face
            for j in range(3):
                adjacent_stickers.append(self.sticker_objects['F'][2][j])
            
            # Bottom row of L face
            for j in range(3):
                adjacent_stickers.append(self.sticker_objects['L'][2][j])
            
            # Bottom row of B face
            for j in range(3):
                adjacent_stickers.append(self.sticker_objects['B'][2][j])
            
            # Bottom row of R face
            for j in range(3):
                adjacent_stickers.append(self.sticker_objects['R'][2][j])
        
        elif face == 'L':  # Left face
            # Left column of U face
            for i in range(3):
                adjacent_stickers.append(self.sticker_objects['U'][i][0])
            
            # Left column of F face
            for i in range(3):
                adjacent_stickers.append(self.sticker_objects['F'][i][0])
            
            # Left column of D face
            for i in range(3):
                adjacent_stickers.append(self.sticker_objects['D'][i][0])
            
            # Right column of B face
            for i in range(3):
                adjacent_stickers.append(self.sticker_objects['B'][i][2])
        
        elif face == 'R':  # Right face
            # Right column of U face
            for i in range(3):
                adjacent_stickers.append(self.sticker_objects['U'][i][2])
            
            # Right column of F face
            for i in range(3):
                adjacent_stickers.append(self.sticker_objects['F'][i][2])
            
            # Right column of D face
            for i in range(3):
                adjacent_stickers.append(self.sticker_objects['D'][i][2])
            
            # Left column of B face
            for i in range(3):
                adjacent_stickers.append(self.sticker_objects['B'][i][0])
        
        elif face == 'B':  # Back face
            # Top row of U face
            for j in range(3):
                adjacent_stickers.append(self.sticker_objects['U'][0][j])
            
            # Right column of R face
            for i in range(3):
                adjacent_stickers.append(self.sticker_objects['R'][i][2])
            
            # Bottom row of D face
            for j in range(3):
                adjacent_stickers.append(self.sticker_objects['D'][2][j])
            
            # Left column of L face
            for i in range(3):
                adjacent_stickers.append(self.sticker_objects['L'][i][0])
        
        return adjacent_stickers
    
    def get_cube_state(self):
        """Get the current state of the cube."""
        state = {}
        for face in config.FACE_NAMES:
            state[face] = []
            for i in range(3):
                for j in range(3):
                    sticker = self.sticker_objects[face][i][j]
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
            for i in range(3):
                for j in range(3):
                    sticker = self.sticker_objects[face][i][j]
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
            return None 