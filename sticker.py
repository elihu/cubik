"""
Sticker class for Rubik's Cube representation.
Each sticker represents a single colored square on the cube.
"""

class Sticker:
    def __init__(self, color, position, face):
        """
        Initialize a sticker.
        
        Args:
            color (str): Color of the sticker ('W', 'Y', 'R', 'O', 'B', 'G')
            position (tuple): 3D position (x, y, z) in the cube matrix
            face (str): Face this sticker belongs to ('U', 'D', 'F', 'B', 'L', 'R')
        """
        self.color = color
        self.position = position
        self.face = face
        self.is_selected = False
    
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