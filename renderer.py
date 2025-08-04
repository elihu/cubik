"""
Renderer class for handling OpenGL rendering and Pygame events.
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
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
        
        # Face selection variables
        self.selected_face = None
        self.face_rotation_drag = False
        self.face_rotation_start_pos = None
        self.face_rotation_threshold = 30  # pixels
        self.face_rotation_triggered = False
    
    def initialize(self):
        """Initialize Pygame and OpenGL."""
        pygame.init()
        display = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption(f"Rubik's Cube {config.CUBE_SIZE}x{config.CUBE_SIZE} | Controls: Arrows,F,B (+Shift) | Right-click to select faces")

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
            
            # Handle mouse controls
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.mouse_down = True
                    self.last_mouse_pos = event.pos
                    
                    # If a face is selected, start face rotation mode
                    if self.selected_face:
                        self.face_rotation_drag = True
                        self.face_rotation_start_pos = event.pos
                        logger.info(f"🔄 Started face rotation for {self.selected_face}")
                elif event.button == 3:  # Right mouse button - face selection
                    # Check if we clicked on a specific cubie
                    clicked_cubie_info = self.get_clicked_cubie_info(event.pos, cube)
                    if clicked_cubie_info:
                        cubie, face = clicked_cubie_info
                        self.selected_face = face
                        cube.set_selected_face(face)
                        logger.info(f"🎯 Selected face: {face}")
                        logger.debug(f"Cubie position: {cubie.pos}")
                    else:
                        self.selected_face = None
                        cube.set_selected_face(None)
                        logger.info("❌ No face selected")
            
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    self.mouse_down = False
                    if self.face_rotation_drag:
                        self.face_rotation_drag = False
                        self.face_rotation_triggered = False  # Reset for next rotation
                        logger.info(f"✅ Finished face rotation for {self.selected_face}")
            
            if event.type == pygame.MOUSEMOTION and self.mouse_down:
                if self.face_rotation_drag and self.selected_face:
                    # Handle face rotation
                    self._handle_face_rotation(event.pos, cube)
                else:
                    # Handle cube rotation
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
                
                # Fix log direction for U, R, F faces (which have base_dir = 1)
                # L, D, B faces (base_dir = -1) work correctly
                if base_dir > 0:  # U, R, F faces
                    rotation_direction = "counterclockwise" if actual_direction > 0 else "clockwise"
                else:  # L, D, B faces
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
    
    def _handle_face_rotation(self, current_pos, cube):
        """
        Handle face rotation logic.
        
        Args:
            current_pos (tuple): Current mouse position
            cube (RubiksCube): The cube instance
        """
        # Calculate total distance moved from start position
        total_dx = current_pos[0] - self.face_rotation_start_pos[0]
        total_dy = current_pos[1] - self.face_rotation_start_pos[1]
        total_distance = (total_dx**2 + total_dy**2)**0.5
        
        # Check if we've moved enough to trigger rotation
        if total_distance > self.face_rotation_threshold and not self.face_rotation_triggered:
            # Determine rotation direction based on dominant movement
            if abs(total_dx) > abs(total_dy):
                # Horizontal movement dominates
                direction = 1 if total_dx > 0 else -1
            else:
                # Vertical movement dominates
                direction = 1 if total_dy > 0 else -1
            
            # Use the same system as keyboard controls
            face_to_axis = {
                'U': ('y', (cube.n - 1) / 2.0, 1),
                'D': ('y', -(cube.n - 1) / 2.0, -1),
                'R': ('x', (cube.n - 1) / 2.0, 1),
                'L': ('x', -(cube.n - 1) / 2.0, -1),
                'F': ('z', (cube.n - 1) / 2.0, 1),
                'B': ('z', -(cube.n - 1) / 2.0, -1)
            }
            
            if self.selected_face in face_to_axis:
                axis, slice_idx, base_dir = face_to_axis[self.selected_face]
                cube.start_move(axis, slice_idx, direction * base_dir)
                
                # Use the same logging logic as keyboard
                actual_direction = direction * base_dir
                if base_dir > 0:  # U, R, F faces
                    rotation_direction = "counterclockwise" if actual_direction > 0 else "clockwise"
                else:  # L, D, B faces
                    rotation_direction = "clockwise" if actual_direction > 0 else "counterclockwise"
                
                logger.info(f"🔄 Rotating {self.selected_face} face {rotation_direction}")
                self.face_rotation_triggered = True
        
        self.last_mouse_pos = current_pos
    
    def get_clicked_cubie_info(self, mouse_pos, cube):
        """
        Get the cubie that was clicked using ray casting.
        
        Args:
            mouse_pos (tuple): (x, y) screen coordinates
            cube (RubiksCube): The cube instance
            
        Returns:
            tuple: (cubie, face) or None if no cubie clicked
        """
        # Get viewport and modelview/projection matrices
        viewport = glGetIntegerv(GL_VIEWPORT)
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        
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
        
        # Find the closest cubie to the clicked world position
        closest_cubie = None
        closest_distance = float('inf')
        closest_face = None
        
        for cubie in cube.cubies:
            # Get cubie position in world coordinates
            cubie_world_pos = np.dot(cubie.matrix[:3, :3], cubie.pos) + cubie.matrix[:3, 3]
            
            # Calculate distance from click to cubie center
            distance = ((world_pos[0] - cubie_world_pos[0])**2 + 
                       (world_pos[1] - cubie_world_pos[1])**2 + 
                       (world_pos[2] - cubie_world_pos[2])**2)**0.5
            
            if distance < closest_distance:
                closest_distance = distance
                closest_cubie = cubie
                
                # Determine which face was clicked based on normal direction
                # This is a simplified approach - we'll use the face with the most visible color
                visible_faces = [face for face, color in cubie.colors.items() 
                               if color != config.COLORS['INSIDE']]
                if visible_faces:
                    closest_face = visible_faces[0]  # Take the first visible face
        
        # If we found a cubie within reasonable distance
        if closest_distance < config.CUBIE_SIZE * 2 and closest_face:
            logger.debug(f"Selected cubie at distance {closest_distance:.3f}, face: {closest_face}")
            return (closest_cubie, closest_face)
        else:
            logger.debug(f"No cubie found within reasonable distance. Closest: {closest_distance:.3f}")
            return None
    
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