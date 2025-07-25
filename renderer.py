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
        
        # Set initial camera position
        glTranslatef(0.0, 0.0, -config.CAMERA_DISTANCE)
        glRotatef(config.INITIAL_ROTATION_X, 1, 0, 0)
        glRotatef(config.INITIAL_ROTATION_Y, 0, 1, 0)
        
        self.clock = pygame.time.Clock()
        self.initialized = True
        
        print("✓ Renderer initialized successfully")
    
    def clear_screen(self):
        """Clear the screen and depth buffer."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    def render_frame(self, cube):
        """
        Render a single frame.
        
        Args:
            cube: RubiksCube instance to render
        """
        if not self.initialized:
            raise RuntimeError("Renderer not initialized. Call initialize() first.")
        
        self.clear_screen()
        cube.draw()
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