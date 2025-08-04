"""
Sticker class for Rubik's Cube representation.
Each sticker represents a single colored square on the cube.
"""

class Sticker:
    def __init__(self, color, position, face, matrix_i=0, matrix_j=0):
        """
        Initialize a sticker.
        
        Args:
            color (str): Color of the sticker ('W', 'Y', 'R', 'O', 'B', 'G')
            position (tuple): 3D position (x, y, z) in the cube matrix
            face (str): Face this sticker belongs to ('U', 'D', 'F', 'B', 'L', 'R')
            matrix_i (int): Row index in the face matrix (0 to size-1)
            matrix_j (int): Column index in the face matrix (0 to size-1)
        """
        self.color = color
        self.position = position
        self.face = face
        self.matrix_i = matrix_i  # Position in face matrix
        self.matrix_j = matrix_j  # Position in face matrix
        self.is_selected = False
        self.is_adjacent = False  # Whether this sticker is adjacent to selected face
    
    def set_color(self, color):
        """Set the sticker color."""
        self.color = color
    
    def get_color(self):
        """Get the sticker color."""
        return self.color
    
    def set_position(self, position):
        """Set the sticker position."""
        self.position = position
    
    def get_position(self):
        """Get the sticker position."""
        return self.position
    
    def set_face(self, face):
        """Set the face this sticker belongs to."""
        self.face = face
    
    def get_face(self):
        """Get the face this sticker belongs to."""
        return self.face
    
    def set_selected(self, selected):
        """Set whether this sticker is selected."""
        self.is_selected = selected
    
    def is_sticker_selected(self):
        """Check if this sticker is selected."""
        return self.is_selected
    
    def set_adjacent(self, adjacent):
        """Set whether this sticker is adjacent to selected face."""
        self.is_adjacent = adjacent
    
    def is_sticker_adjacent(self):
        """Check if this sticker is adjacent to selected face."""
        return self.is_adjacent 
    
    def set_matrix_position(self, i, j):
        """Set the matrix position of this sticker."""
        self.matrix_i = i
        self.matrix_j = j
    
    def get_matrix_position(self):
        """Get the matrix position of this sticker."""
        return (self.matrix_i, self.matrix_j) 