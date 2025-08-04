"""
Renderer class for handling OpenGL rendering and Pygame events.
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import config
from cube import RubiksCube
from utils import logger

class Renderer:
    """Handles OpenGL rendering and Pygame event processing."""
    
    def __init__(self):
        """Initialize the renderer."""
        self.initialized = False
        self.clock = pygame.time.Clock()
        
        # Mouse interaction variables
        self.mouse_down = False
        self.last_mouse_pos = (0, 0)
    
    def initialize(self):
        """Initialize Pygame and OpenGL."""
        pygame.init()
        display = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption(f"Rubik's Cube {config.CUBE_SIZE}x{config.CUBE_SIZE} | Controls: Arrows,F,B (+Shift)")

        # Set up OpenGL perspective
        glMatrixMode(GL_PROJECTION)
        gluPerspective(config.FOV, (display[0] / display[1]), config.NEAR_PLANE, config.FAR_PLANE)
        
        self.initialized = True
        logger.info("🎮 Renderer initialized")
    
    def handle_events(self, cube):
        """
        Handle Pygame events.
        
        Args:
            cube (RubiksCube): The cube instance to control
            
        Returns:
            bool: True if application should continue running, False to quit
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r:
                    cube.reset_to_solved()
                    logger.info("✅ Cube reset")
                elif event.key == pygame.K_d:
                    logger.toggle_debug()
                else:
                    # Handle cube movement keys
                    self._handle_movement_key(event, cube)
            
            # Handle mouse camera controls
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.mouse_down = True
                self.last_mouse_pos = event.pos
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.mouse_down = False
            if event.type == pygame.MOUSEMOTION and self.mouse_down:
                self._handle_mouse_motion(event.pos, cube)
        
        return True
    
    def _handle_movement_key(self, event, cube):
        """
        Handle movement key presses.
        
        Args:
            event: Pygame key event
            cube (RubiksCube): The cube instance
        """
        key_mappings = config.get_key_mappings()
        
        # Map pygame keys to our movement keys
        pygame_to_movement = {
            pygame.K_UP: 'UP',
            pygame.K_DOWN: 'DOWN', 
            pygame.K_RIGHT: 'RIGHT',
            pygame.K_LEFT: 'LEFT',
            pygame.K_f: 'FRONT',  # Keep F for front face
            pygame.K_b: 'BACK'    # Keep B for back face
        }
        
        if event.key in pygame_to_movement:
            movement_key = pygame_to_movement[event.key]
            if movement_key in key_mappings:
                mods = pygame.key.get_mods()
                direction = 1 if mods & pygame.KMOD_SHIFT else -1
                axis, slice_idx, base_dir = key_mappings[movement_key]
                cube.start_move(axis, slice_idx, direction * base_dir)
                
                # Log the face rotation with direction
                face_names = {
                    'UP': 'Up',
                    'DOWN': 'Down', 
                    'RIGHT': 'Right',
                    'LEFT': 'Left',
                    'FRONT': 'Front',
                    'BACK': 'Back'
                }
                face_name = face_names.get(movement_key, movement_key)
                # Calculate the actual rotation direction considering both direction and base_dir
                actual_direction = direction * base_dir
                rotation_direction = "clockwise" if actual_direction > 0 else "counterclockwise"
                logger.info(f"🔄 Rotating {face_name} face {rotation_direction}")
                
                logger.debug(f"🎯 Key pressed: {movement_key}, direction: {direction}")
    
    def _handle_mouse_motion(self, current_pos, cube):
        """
        Handle mouse motion for camera rotation.
        
        Args:
            current_pos (tuple): Current mouse position
            cube (RubiksCube): The cube instance
        """
        dx = current_pos[0] - self.last_mouse_pos[0]
        dy = current_pos[1] - self.last_mouse_pos[1]
        
        cube.view_rot_y += dx * config.MOUSE_ROTATION_SENSITIVITY
        cube.view_rot_x += dy * config.MOUSE_ROTATION_SENSITIVITY
        
        # Keep rotation within reasonable bounds
        cube.view_rot_x = max(-90, min(90, cube.view_rot_x))
        
        self.last_mouse_pos = current_pos
    
    def render_frame(self, cube):
        """
        Render a single frame.
        
        Args:
            cube (RubiksCube): The cube to render
        """
        cube.draw()
        pygame.display.flip()
    
    def tick(self, fps=60):
        """
        Limit frame rate.
        
        Args:
            fps (int): Target frames per second
        """
        self.clock.tick(fps)
    
    def cleanup(self):
        """Clean up Pygame resources."""
        if self.initialized:
            pygame.quit()
            logger.info("🧹 Renderer cleaned up") 