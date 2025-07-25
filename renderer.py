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
                if event.button == 1:  # Left mouse button
                    self.mouse_pressed = True
                    self.last_mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    self.mouse_pressed = False
            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_pressed:
                    # Calculate mouse movement
                    dx = event.pos[0] - self.last_mouse_pos[0]
                    dy = event.pos[1] - self.last_mouse_pos[1]
                    
                    # Apply rotation based on mouse movement
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