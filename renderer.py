"""
renderer.py

Renderer class that handles OpenGL initialization, window management, and rendering.
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
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
        
        # Face selection state
        self.selected_face = None
    
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
        
        cube.draw()
        
        glPopMatrix()
        pygame.display.flip()
    
    def handle_events(self):
        """
        Handle Pygame events.
        
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
                if event.button == 1:  # Left mouse button - cube rotation
                    self.mouse_pressed = True
                    self.last_mouse_pos = event.pos
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
                    self.selected_face = None
            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_pressed:
                    # Calculate mouse movement
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
        Detect which face of the cube was clicked using a simpler approach.
        
        Args:
            mouse_pos (tuple): Mouse position (x, y) in screen coordinates
            
        Returns:
            str or None: Face name ('U', 'D', 'F', 'B', 'L', 'R') or None if no face clicked
        """
        # Get screen center
        screen_center_x = self.display[0] // 2
        screen_center_y = self.display[1] // 2
        
        # Calculate relative position from center
        rel_x = mouse_pos[0] - screen_center_x
        rel_y = mouse_pos[1] - screen_center_y
        
        # Normalize to -1 to 1 range
        norm_x = rel_x / screen_center_x
        norm_y = rel_y / screen_center_y
        
        # Simple face detection based on screen position
        # This is a basic approximation - we'll refine it later
        if abs(norm_x) < 0.3 and abs(norm_y) < 0.3:
            # Center area - could be front or back face
            if norm_y > 0:
                return 'F'  # Front face
            else:
                return 'B'  # Back face
        elif norm_x > 0.3:
            return 'R'  # Right face
        elif norm_x < -0.3:
            return 'L'  # Left face
        elif norm_y > 0.3:
            return 'U'  # Up face
        elif norm_y < -0.3:
            return 'D'  # Down face
        
        return None