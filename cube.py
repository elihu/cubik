"""
Simplified Rubik's Cube implementation using a 9×6 matrix of Sticker objects.
"""

import numpy as np
from sticker import Sticker
import config
from OpenGL.GLU import gluUnProject
from OpenGL.GL import glReadPixels, GL_DEPTH_COMPONENT, GL_FLOAT

class Cube:
    def __init__(self, size=3):
        """
        Initialize a Rubik's Cube with the specified size.
        
        Args:
            size (int): Size of the cube (2, 3, 4, etc.)
        """
        self.size = size
        self.faces = {}  # Dictionary: face -> list of 9 stickers
        self.selected_face = None
        self.initialize_cube()
    
    def initialize_cube(self):
        """Initialize the cube with stickers in solved state."""
        # Initialize each face with 9 stickers
        for face in config.FACE_NAMES:
            self.faces[face] = []
            base_color = config.FACE_COLORS[face]
            
            # Create 9 stickers for this face (3x3 grid)
            for i in range(3):
                for j in range(3):
                    # Calculate position within the face
                    pos = self.calculate_sticker_position(face, i, j)
                    
                    # Create unique color for each position to see rotation clearly
                    # Use base color + position info
                    unique_color = f"{base_color}{i}{j}"  # e.g., "R00", "R01", "R02", etc.
                    
                    sticker = Sticker(unique_color, pos, face)
                    self.faces[face].append(sticker)
        
        # Setup adjacencies between stickers
        self.setup_adjacencies()
    
    def setup_adjacencies(self):
        """Setup adjacency relationships between stickers."""
        print("Setting up sticker adjacencies...")
        
        # Define face adjacency relationships
        # Each face has 4 adjacent faces: top, bottom, left, right
        face_adjacencies = {
            'U': {'top': 'B', 'bottom': 'F', 'left': 'L', 'right': 'R'},
            'D': {'top': 'F', 'bottom': 'B', 'left': 'L', 'right': 'R'},
            'F': {'top': 'U', 'bottom': 'D', 'left': 'L', 'right': 'R'},
            'B': {'top': 'U', 'bottom': 'D', 'left': 'R', 'right': 'L'},
            'L': {'top': 'U', 'bottom': 'D', 'left': 'B', 'right': 'F'},
            'R': {'top': 'U', 'bottom': 'D', 'left': 'F', 'right': 'B'}
        }
        
        # For each sticker, find its adjacent stickers
        for face in config.FACE_NAMES:
            face_stickers = self.get_face_stickers(face)
            for i, sticker in enumerate(face_stickers):
                row = i // 3
                col = i % 3
                
                adjacent_positions = []
                
                # Add adjacent stickers within the same face (8 adjacent positions)
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue  # Skip self
                        
                        new_row = row + dr
                        new_col = col + dc
                        
                        # Check if position is valid within the face
                        if 0 <= new_row < 3 and 0 <= new_col < 3:
                            adjacent_index = new_row * 3 + new_col
                            adjacent_sticker = face_stickers[adjacent_index]
                            adjacent_positions.append(adjacent_sticker.get_position())
                
                # Add adjacent stickers from other faces based on position
                adjacents = face_adjacencies[face]
                
                # Top edge stickers (row 0) are adjacent to top face
                if row == 0:
                    top_face = adjacents['top']
                    # Map the column to the correct position on the adjacent face
                    if face == 'F':
                        # F top edge connects to U bottom edge (row 2)
                        for j in range(3):
                            u_sticker = self.get_sticker_at(top_face, 2, j)
                            if u_sticker:
                                adjacent_positions.append(u_sticker.get_position())
                    elif face == 'L':
                        # L top edge connects to U left edge (col 0)
                        for i in range(3):
                            u_sticker = self.get_sticker_at(top_face, i, 0)
                            if u_sticker:
                                adjacent_positions.append(u_sticker.get_position())
                    elif face == 'R':
                        # R top edge connects to U right edge (col 2)
                        for i in range(3):
                            u_sticker = self.get_sticker_at(top_face, i, 2)
                            if u_sticker:
                                adjacent_positions.append(u_sticker.get_position())
                    elif face == 'B':
                        # B top edge connects to U top edge (row 0)
                        for j in range(3):
                            u_sticker = self.get_sticker_at(top_face, 0, j)
                            if u_sticker:
                                adjacent_positions.append(u_sticker.get_position())
                
                # Bottom edge stickers (row 2) are adjacent to bottom face
                elif row == 2:
                    bottom_face = adjacents['bottom']
                    if face == 'F':
                        # F bottom edge connects to D top edge (row 0)
                        for j in range(3):
                            d_sticker = self.get_sticker_at(bottom_face, 0, j)
                            if d_sticker:
                                adjacent_positions.append(d_sticker.get_position())
                    elif face == 'L':
                        # L bottom edge connects to D left edge (col 0)
                        for i in range(3):
                            d_sticker = self.get_sticker_at(bottom_face, i, 0)
                            if d_sticker:
                                adjacent_positions.append(d_sticker.get_position())
                    elif face == 'R':
                        # R bottom edge connects to D right edge (col 2)
                        for i in range(3):
                            d_sticker = self.get_sticker_at(bottom_face, i, 2)
                            if d_sticker:
                                adjacent_positions.append(d_sticker.get_position())
                    elif face == 'B':
                        # B bottom edge connects to D bottom edge (row 2)
                        for j in range(3):
                            d_sticker = self.get_sticker_at(bottom_face, 2, j)
                            if d_sticker:
                                adjacent_positions.append(d_sticker.get_position())
                
                # Left edge stickers (col 0) are adjacent to left face
                if col == 0:
                    left_face = adjacents['left']
                    if face == 'U':
                        # U left edge connects to L top edge (row 0)
                        for j in range(3):
                            l_sticker = self.get_sticker_at(left_face, 0, j)
                            if l_sticker:
                                adjacent_positions.append(l_sticker.get_position())
                    elif face == 'F':
                        # F left edge connects to L right edge (col 2)
                        for i in range(3):
                            l_sticker = self.get_sticker_at(left_face, i, 2)
                            if l_sticker:
                                adjacent_positions.append(l_sticker.get_position())
                    elif face == 'D':
                        # D left edge connects to L bottom edge (row 2)
                        for j in range(3):
                            l_sticker = self.get_sticker_at(left_face, 2, j)
                            if l_sticker:
                                adjacent_positions.append(l_sticker.get_position())
                    elif face == 'B':
                        # B left edge connects to L left edge (col 0)
                        for i in range(3):
                            l_sticker = self.get_sticker_at(left_face, i, 0)
                            if l_sticker:
                                adjacent_positions.append(l_sticker.get_position())
                
                # Right edge stickers (col 2) are adjacent to right face
                elif col == 2:
                    right_face = adjacents['right']
                    if face == 'U':
                        # U right edge connects to R top edge (row 0)
                        for j in range(3):
                            r_sticker = self.get_sticker_at(right_face, 0, j)
                            if r_sticker:
                                adjacent_positions.append(r_sticker.get_position())
                    elif face == 'F':
                        # F right edge connects to R left edge (col 0)
                        for i in range(3):
                            r_sticker = self.get_sticker_at(right_face, i, 0)
                            if r_sticker:
                                adjacent_positions.append(r_sticker.get_position())
                    elif face == 'D':
                        # D right edge connects to R bottom edge (row 2)
                        for j in range(3):
                            r_sticker = self.get_sticker_at(right_face, 2, j)
                            if r_sticker:
                                adjacent_positions.append(r_sticker.get_position())
                    elif face == 'B':
                        # B right edge connects to R right edge (col 2)
                        for i in range(3):
                            r_sticker = self.get_sticker_at(right_face, i, 2)
                            if r_sticker:
                                adjacent_positions.append(r_sticker.get_position())
                
                # Add all adjacent positions to the sticker
                for pos in adjacent_positions:
                    sticker.add_adjacent(pos)
                
                print(f"  {face}[{row},{col}] has {len(adjacent_positions)} adjacents")
        
        print("Adjacency setup complete!")
    
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
    
    def get_sticker_at(self, face, i, j):
        """Get sticker at position (i, j) on the given face."""
        if face in self.faces and 0 <= i < 3 and 0 <= j < 3:
            index = i * 3 + j
            return self.faces[face][index]
        return None
    
    def set_sticker_at(self, face, i, j, sticker):
        """Set sticker at position (i, j) on the given face."""
        if face in self.faces and 0 <= i < 3 and 0 <= j < 3:
            index = i * 3 + j
            self.faces[face][index] = sticker
            
            # Update the sticker's position to match its new location
            new_position = self.calculate_sticker_position(face, i, j)
            sticker.set_position(new_position)
            sticker.set_face(face)
    
    def get_face_stickers(self, face):
        """Get all stickers for a specific face."""
        return self.faces.get(face, [])
    
    def print_cube_state(self):
        """Print the current state of the cube in a visual format."""
        print("\n🎲 Current Cube State:")
        print("=" * 50)
        
        for face in config.FACE_NAMES:
            face_stickers = self.get_face_stickers(face)
            print(f"\n{face} face:")
            for i in range(3):
                row_colors = []
                for j in range(3):
                    index = i * 3 + j
                    color = face_stickers[index].get_color()
                    row_colors.append(color)
                print(f"  {row_colors}")
        print("=" * 50)
    
    def rotate_face(self, face, direction):
        """
        Rotate a face by 90 degrees.
        
        Args:
            face (str): Face to rotate ('U', 'D', 'F', 'B', 'L', 'R')
            direction (str): 'clockwise' or 'counterclockwise'
            
        """
        print(f"🔄 Rotating face {face} {direction}")
        
        # Show cube state before rotation
        self.print_cube_state()
        
        # Get all stickers on this face
        face_stickers = self.get_face_stickers(face)
        
        # Rotate the stickers on the face itself
        self.rotate_face_stickers(face_stickers, direction)
        
        # Update adjacent faces (we'll implement this later)
        self.update_adjacent_faces(face, direction)
        
        # Show cube state after rotation
        self.print_cube_state()
        
        print(f"✅ Face {face} rotated {direction}")
    
    def rotate_face_stickers(self, face_stickers, direction):
        """Rotate stickers on a face by 90 degrees."""
        # Create a 3x3 matrix from the list of stickers
        matrix = [[None for _ in range(3)] for _ in range(3)]
        
        # Fill the matrix
        for i, sticker in enumerate(face_stickers):
            row = i // 3
            col = i % 3
            matrix[row][col] = sticker
        
        print(f"  Before rotation:")
        for row in matrix:
            print(f"    {[sticker.get_color() for sticker in row]}")
        
        # Rotate the matrix
        if direction == "clockwise":
            # Rotate 90 degrees clockwise: transpose and reverse rows
            rotated_matrix = []
            for col in range(3):
                new_row = []
                for row in range(2, -1, -1):  # Reverse order
                    new_row.append(matrix[row][col])
                rotated_matrix.append(new_row)
        else:  # counterclockwise
            # Rotate 90 degrees counterclockwise: transpose and reverse columns
            rotated_matrix = []
            for col in range(2, -1, -1):  # Reverse order
                new_row = []
                for row in range(3):
                    new_row.append(matrix[row][col])
                rotated_matrix.append(new_row)
        
        print(f"  After {direction} rotation:")
        for row in rotated_matrix:
            print(f"    {[sticker.get_color() for sticker in row]}")
        
        # Update the face_stickers list with the rotated stickers in correct order
        # We need to flatten the rotated matrix back to a list
        new_face_stickers = []
        for row in rotated_matrix:
            for sticker in row:
                new_face_stickers.append(sticker)
        
        # Replace the original list with the rotated one
        face_stickers.clear()
        face_stickers.extend(new_face_stickers)
        
        # Update positions of all stickers in the face to match their new locations
        for i, sticker in enumerate(face_stickers):
            row = i // 3
            col = i % 3
            new_position = self.calculate_sticker_position(sticker.get_face(), row, col)
            sticker.set_position(new_position)
        
        print(f"  Rotated {len(face_stickers)} stickers on face")
    
    def update_adjacent_faces(self, rotated_face, direction):
        """Update stickers on adjacent faces after a rotation."""
        print(f"  Updating adjacent faces for {rotated_face} {direction} rotation")
        
        # Define which faces are adjacent and how stickers move
        if rotated_face == 'F':  # Front face
            # When F rotates, stickers move between U, R, D, L
            if direction == "clockwise":
                # U bottom edge (row 2) -> R right edge (column 2)
                # R right edge (column 2) -> D bottom edge (row 2)
                # D bottom edge (row 2) -> L right edge (column 2)
                # L right edge (column 2) -> U bottom edge (row 2)
                
                # Get the stickers that need to move
                u_bottom = [self.get_sticker_at('U', 2, j) for j in range(3)]
                r_right = [self.get_sticker_at('R', i, 2) for i in range(3)]
                d_bottom = [self.get_sticker_at('D', 2, j) for j in range(3)]
                l_right = [self.get_sticker_at('L', i, 2) for i in range(3)]
                
                # Move stickers with correct mapping (from old code)
                # U bottom -> R right (inverted: row to column)
                self.set_sticker_at('R', 0, 2, u_bottom[2])  # U(2,2) -> R(0,2)
                self.set_sticker_at('R', 1, 2, u_bottom[1])  # U(2,1) -> R(1,2)
                self.set_sticker_at('R', 2, 2, u_bottom[0])  # U(2,0) -> R(2,2)
                
                # R right -> D bottom (inverted: column to row)
                self.set_sticker_at('D', 2, 0, r_right[2])   # R(2,2) -> D(2,0)
                self.set_sticker_at('D', 2, 1, r_right[1])   # R(1,2) -> D(2,1)
                self.set_sticker_at('D', 2, 2, r_right[0])   # R(0,2) -> D(2,2)
                
                # D bottom -> L right (inverted: row to column)
                self.set_sticker_at('L', 0, 2, d_bottom[2])  # D(2,2) -> L(0,2)
                self.set_sticker_at('L', 1, 2, d_bottom[1])  # D(2,1) -> L(1,2)
                self.set_sticker_at('L', 2, 2, d_bottom[0])  # D(2,0) -> L(2,2)
                
                # L right -> U bottom (inverted: column to row)
                self.set_sticker_at('U', 2, 0, l_right[2])   # L(2,2) -> U(2,0)
                self.set_sticker_at('U', 2, 1, l_right[1])   # L(1,2) -> U(2,1)
                self.set_sticker_at('U', 2, 2, l_right[0])   # L(0,2) -> U(2,2)
                    
            else:  # counterclockwise
                # U bottom edge -> L right edge
                # L right edge -> D bottom edge
                # D bottom edge -> R right edge
                # R right edge -> U bottom edge
                
                u_bottom = [self.get_sticker_at('U', 2, j) for j in range(3)]
                l_right = [self.get_sticker_at('L', i, 2) for i in range(3)]
                d_bottom = [self.get_sticker_at('D', 2, j) for j in range(3)]
                r_right = [self.get_sticker_at('R', i, 2) for i in range(3)]
                
                # Move stickers with correct mapping (from old code)
                # U bottom -> L right (inverted: row to column)
                self.set_sticker_at('L', 0, 2, u_bottom[0])  # U(2,0) -> L(0,2)
                self.set_sticker_at('L', 1, 2, u_bottom[1])  # U(2,1) -> L(1,2)
                self.set_sticker_at('L', 2, 2, u_bottom[2])  # U(2,2) -> L(2,2)
                
                # L right -> D bottom (inverted: column to row)
                self.set_sticker_at('D', 2, 0, l_right[0])   # L(0,2) -> D(2,0)
                self.set_sticker_at('D', 2, 1, l_right[1])   # L(1,2) -> D(2,1)
                self.set_sticker_at('D', 2, 2, l_right[2])   # L(2,2) -> D(2,2)
                
                # D bottom -> R right (inverted: row to column)
                self.set_sticker_at('R', 0, 2, d_bottom[0])  # D(2,0) -> R(0,2)
                self.set_sticker_at('R', 1, 2, d_bottom[1])  # D(2,1) -> R(1,2)
                self.set_sticker_at('R', 2, 2, d_bottom[2])  # D(2,2) -> R(2,2)
                
                # R right -> U bottom (inverted: column to row)
                self.set_sticker_at('U', 2, 0, r_right[0])   # R(0,2) -> U(2,0)
                self.set_sticker_at('U', 2, 1, r_right[1])   # R(1,2) -> U(2,1)
                self.set_sticker_at('U', 2, 2, r_right[2])   # R(2,2) -> U(2,2)
        
        elif rotated_face == 'U':  # Up face
            # When U rotates, stickers move between F, L, B, R
            if direction == "clockwise":
                # F top row -> R top row
                # R top row -> B top row
                # B top row -> L top row
                # L top row -> F top row
                
                f_top = [self.get_sticker_at('F', 0, j) for j in range(3)]
                r_top = [self.get_sticker_at('R', 0, j) for j in range(3)]
                b_top = [self.get_sticker_at('B', 0, j) for j in range(3)]
                l_top = [self.get_sticker_at('L', 0, j) for j in range(3)]
                
                for j in range(3):
                    self.set_sticker_at('R', 0, j, f_top[j])
                    self.set_sticker_at('B', 0, j, r_top[j])
                    self.set_sticker_at('L', 0, j, b_top[j])
                    self.set_sticker_at('F', 0, j, l_top[j])
                    
            else:  # counterclockwise
                f_top = [self.get_sticker_at('F', 0, j) for j in range(3)]
                l_top = [self.get_sticker_at('L', 0, j) for j in range(3)]
                b_top = [self.get_sticker_at('B', 0, j) for j in range(3)]
                r_top = [self.get_sticker_at('R', 0, j) for j in range(3)]
                
                for j in range(3):
                    self.set_sticker_at('L', 0, j, f_top[j])
                    self.set_sticker_at('B', 0, j, l_top[j])
                    self.set_sticker_at('R', 0, j, b_top[j])
                    self.set_sticker_at('F', 0, j, r_top[j])
        
        print(f"  Adjacent faces updated!")
    
    def set_selected_face(self, face):
        """Set the selected face for highlighting."""
        # Clear previous selection
        if self.selected_face:
            for sticker in self.get_face_stickers(self.selected_face):
                sticker.set_selected(False)
        
        # Set new selection
        self.selected_face = face
        if face:
            for sticker in self.get_face_stickers(face):
                sticker.set_selected(True)
    
    def get_cube_state(self):
        """Get the current state of the cube."""
        state = {}
        for face in config.FACE_NAMES:
            state[face] = []
            for sticker in self.get_face_stickers(face):
                state[face].append({
                    'color': sticker.get_color(),
                    'position': sticker.get_position(),
                    'selected': sticker.is_sticker_selected()
                })
        return state
    
    def reset_to_solved(self):
        """Reset the cube to solved state."""
        self.initialize_cube()
        print("✓ Cube reset to solved state") 

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
            print("Failed to unproject mouse coordinates")
            return None
        
        print(f"Mouse click at screen ({mouse_pos[0]}, {mouse_pos[1]}) -> world: {world_pos}")
        
        # Find the closest sticker to the clicked world position
        closest_sticker = None
        closest_distance = float('inf')
        
        for face in config.FACE_NAMES:
            face_stickers = self.get_face_stickers(face)
            for i, sticker in enumerate(face_stickers):
                sticker_pos = sticker.get_position()
                
                # Calculate distance from click to sticker center
                distance = ((world_pos[0] - sticker_pos[0])**2 + 
                           (world_pos[1] - sticker_pos[1])**2 + 
                           (world_pos[2] - sticker_pos[2])**2)**0.5
                
                print(f"  Sticker {face}[{i//3},{i%3}] at {sticker_pos}: distance = {distance:.3f}")
                
                if distance < closest_distance:
                    closest_distance = distance
                    closest_sticker = (sticker, face, i // 3, i % 3)
        
        # If we found a sticker within reasonable distance
        if closest_distance < config.STICKER_SIZE * 2:
            print(f"Selected sticker at distance {closest_distance:.3f}")
            return closest_sticker
        else:
            print(f"No sticker found within reasonable distance. Closest: {closest_distance:.3f}")
            return None 