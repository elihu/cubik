"""
renderer.py

Renderer class that handles OpenGL initialization, window management, and rendering.
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import config

class Renderer:
    """
    Handles OpenGL initialization, window management, and rendering.
    """
    
    def __init__(self):
        """Initialize the renderer with OpenGL and Pygame."""
        self.display = None
        self.clock = None
        self.initialized = False
        
        # Mouse rotation state
        self.mouse_pressed = False
        self.last_mouse_pos = (0, 0)
        self.cube_rotation_x = config.INITIAL_ROTATION_X
        self.cube_rotation_y = config.INITIAL_ROTATION_Y
        self.rotation_sensitivity = 0.5  # Adjust for faster/slower rotation
        
        # Face selection and rotation state
        self.selected_face = None
        self.face_rotation_drag = False  # True when dragging to rotate a face
        self.face_rotation_start_pos = (0, 0)  # Starting position for face rotation
        self.face_rotation_threshold = 50  # Minimum distance to trigger rotation
        self.face_rotation_triggered = False  # True when rotation has been triggered
    
    def initialize(self):
        """Initialize Pygame, OpenGL, and the display window."""
        pygame.init()
        self.display = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        
        # OpenGL setup
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1)
        glDisable(GL_CULL_FACE)
        
        # Set up perspective
        gluPerspective(config.FOV, (self.display[0] / self.display[1]), 
                      config.NEAR_PLANE, config.FAR_PLANE)
        
        # Set initial camera position and rotation
        glTranslatef(0.0, 0.0, -config.CAMERA_DISTANCE)
        glRotatef(self.cube_rotation_x, 1, 0, 0)
        glRotatef(self.cube_rotation_y, 0, 1, 0)
        
        self.clock = pygame.time.Clock()
        self.initialized = True
        
        print("✓ Renderer initialized successfully")
    
    def clear_screen(self):
        """Clear the screen and depth buffer."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    def apply_cube_rotation(self):
        """Apply the current cube rotation."""
        # Reset to base position and apply current rotation
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -config.CAMERA_DISTANCE)
        glRotatef(self.cube_rotation_x, 1, 0, 0)
        glRotatef(self.cube_rotation_y, 0, 1, 0)
    
    def render_frame(self, cube):
        """
        Render a single frame.
        
        Args:
            cube: RubiksCube instance to render
        """
        if not self.initialized:
            raise RuntimeError("Renderer not initialized. Call initialize() first.")
        
        self.clear_screen()
        
        # Apply cube rotation
        glPushMatrix()
        glRotatef(self.cube_rotation_x, 1, 0, 0)
        glRotatef(self.cube_rotation_y, 0, 1, 0)
        
        # Update cube's selected face
        cube.set_selected_face(self.selected_face)
        
        # Draw the cube
        cube.draw()
        
        glPopMatrix()
        pygame.display.flip()
    
    def handle_events(self, cube):
        """
        Handle Pygame events.
        
        Args:
            cube: RubiksCube instance to apply rotations to
            
        Returns:
            bool: True if the game should continue, False if it should quit
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r:
                    # Reset cube rotation
                    self.cube_rotation_x = config.INITIAL_ROTATION_X
                    self.cube_rotation_y = config.INITIAL_ROTATION_Y
                    print("✓ Cube rotation reset")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button - cube rotation or face rotation
                    self.mouse_pressed = True
                    self.last_mouse_pos = event.pos
                    
                    # If a face is selected, start face rotation mode
                    if self.selected_face:
                        self.face_rotation_drag = True
                        self.face_rotation_start_pos = event.pos
                        print(f"✓ Started face rotation for {self.selected_face}")
                elif event.button == 3:  # Right mouse button - face selection
                    # Check if we clicked on a specific face
                    clicked_face = self.get_clicked_face(event.pos)
                    if clicked_face:
                        self.selected_face = clicked_face
                        print(f"✓ Selected face: {clicked_face}")
                    else:
                        self.selected_face = None
                        print("No face selected")
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    self.mouse_pressed = False
                    if self.face_rotation_drag:
                        self.face_rotation_drag = False
                        self.face_rotation_triggered = False  # Reset for next rotation
                        print(f"✓ Finished face rotation for {self.selected_face}")
            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_pressed:
                    if self.face_rotation_drag and self.selected_face:
                        # Handle face rotation
                        dx = event.pos[0] - self.last_mouse_pos[0]
                        dy = event.pos[1] - self.last_mouse_pos[1]
                        
                        # Calculate total distance moved from start position
                        total_dx = event.pos[0] - self.face_rotation_start_pos[0]
                        total_dy = event.pos[1] - self.face_rotation_start_pos[1]
                        total_distance = (total_dx**2 + total_dy**2)**0.5
                        
                        # Check if we've moved enough to trigger rotation
                        if total_distance > self.face_rotation_threshold and not self.face_rotation_triggered:
                            # Determine rotation direction based on dominant movement
                            if abs(total_dx) > abs(total_dy):
                                # Horizontal movement dominates
                                if total_dx > 0:
                                    direction = "clockwise"
                                else:
                                    direction = "counterclockwise"
                            else:
                                # Vertical movement dominates
                                if total_dy > 0:
                                    direction = "clockwise"
                                else:
                                    direction = "counterclockwise"
                            
                            # Apply the rotation
                            self.rotate_selected_face(direction, cube)
                            self.face_rotation_triggered = True
                        
                        self.last_mouse_pos = event.pos
                    else:
                        # Handle cube rotation (existing code)
                        dx = event.pos[0] - self.last_mouse_pos[0]
                        dy = event.pos[1] - self.last_mouse_pos[1]
                        
                        # Apply cube rotation
                        self.cube_rotation_y += dx * self.rotation_sensitivity
                        self.cube_rotation_x += dy * self.rotation_sensitivity
                        
                        # Keep rotation within reasonable bounds
                        self.cube_rotation_x = max(-90, min(90, self.cube_rotation_x))
                        
                        # Update last mouse position
                        self.last_mouse_pos = event.pos
        
        return True
    
    def get_fps(self):
        """Get the current FPS."""
        return self.clock.get_fps()
    
    def tick(self, fps=60):
        """Limit the frame rate."""
        self.clock.tick(fps)
    
    def cleanup(self):
        """Clean up Pygame resources."""
        if self.initialized:
            pygame.quit()
            print("✓ Renderer cleaned up")
    
    def resize_window(self, width, height):
        """
        Resize the window.
        
        Args:
            width (int): New window width
            height (int): New window height
        """
        if self.initialized:
            self.display = (width, height)
            pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
            gluPerspective(config.FOV, (width / height), 
                          config.NEAR_PLANE, config.FAR_PLANE)
            print(f"✓ Window resized to {width}x{height}")

    def get_clicked_face(self, mouse_pos):
        """
        Detect which face of the cube was clicked using ray casting with cube rotation consideration.
        
        Args:
            mouse_pos (tuple): Mouse position (x, y) in screen coordinates
            
        Returns:
            str or None: Face name ('U', 'D', 'F', 'B', 'L', 'R') or None if no face clicked
        """
        # Get viewport and modelview/projection matrices
        viewport = glGetIntegerv(GL_VIEWPORT)
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        
        # Convert screen coordinates to normalized device coordinates
        x = mouse_pos[0]
        y = viewport[3] - mouse_pos[1]  # OpenGL uses bottom-left origin
        z = glReadPixels(x, y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)[0][0]
        
        # Unproject to get world coordinates
        world_pos = gluUnProject(x, y, z, modelview, projection, viewport)
        
        if world_pos is None:
            return None
        
        # Transform world coordinates to account for cube rotation
        # We need to apply the inverse of the cube rotation
        clicked_point = np.array(world_pos)
        
        # Create rotation matrices for the inverse transformations
        # Note: We apply rotations in reverse order (Y first, then X)
        cos_y = np.cos(np.radians(-self.cube_rotation_y))
        sin_y = np.sin(np.radians(-self.cube_rotation_y))
        cos_x = np.cos(np.radians(-self.cube_rotation_x))
        sin_x = np.sin(np.radians(-self.cube_rotation_x))
        
        # Y rotation matrix (inverse)
        rot_y = np.array([
            [cos_y, 0, sin_y],
            [0, 1, 0],
            [-sin_y, 0, cos_y]
        ])
        
        # X rotation matrix (inverse)
        rot_x = np.array([
            [1, 0, 0],
            [0, cos_x, -sin_x],
            [0, sin_x, cos_x]
        ])
        
        # Apply inverse rotations to get coordinates in cube's local space
        local_point = rot_x @ rot_y @ clicked_point
        
        # Find the closest face to the transformed point
        closest_face = None
        min_distance = float('inf')
        
        for face in config.FACE_NAMES:
            face_config = config.FACE_CONFIGS[face]
            face_center = np.array(face_config['center'])
            face_normal = np.array(face_config['normal'])
            
            # Calculate distance from transformed point to face plane
            distance = abs(np.dot(local_point - face_center, face_normal))
            
            # Check if point is within the face bounds (3x3 sticker grid)
            face_size = config.STICKER_SIZE * 2 + config.BORDER_WIDTH * 2
            face_bounds = face_size / 2 + 0.2  # Increased tolerance for better detection
            
            # Project point onto face plane
            to_point = local_point - face_center
            projected_point = to_point - np.dot(to_point, face_normal) * face_normal
            
            # Check if projected point is within face bounds
            if (abs(projected_point[0]) <= face_bounds and 
                abs(projected_point[1]) <= face_bounds and 
                abs(projected_point[2]) <= face_bounds):
                
                if distance < min_distance:
                    min_distance = distance
                    closest_face = face
        
        return closest_face
    
    def rotate_selected_face(self, direction, cube):
        """
        Rotate the selected face by 90 degrees in the specified direction.
        
        Args:
            direction (str): "clockwise" or "counterclockwise"
            cube: RubiksCube instance to apply rotation to
        """
        if not self.selected_face:
            return
        
        print(f"Rotating face {self.selected_face} {direction} by 90 degrees")
        
        # Call the cube's rotate_face method
        cube.rotate_face(self.selected_face, direction)