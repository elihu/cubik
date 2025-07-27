"""
Simplified renderer that only handles rendering, without movement logic.
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import config
from cube import Cube

class Renderer:
    def __init__(self):
        """Initialize the renderer."""
        self.initialized = False
        self.cube_rotation_x = config.INITIAL_ROTATION_X
        self.cube_rotation_y = config.INITIAL_ROTATION_Y
        self.rotation_sensitivity = 0.5
        self.clock = pygame.time.Clock()
        
        # Mouse interaction variables
        self.mouse_pressed = False
        self.last_mouse_pos = None
        self.selected_sticker = None  # Changed from selected_face to selected_sticker
        self.face_rotation_drag = False
        self.face_rotation_start_pos = None
        self.face_rotation_threshold = 30  # pixels
        self.face_rotation_triggered = False
    
    def initialize(self):
        """Initialize Pygame and OpenGL."""
        pygame.init()
        pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Rubik's Cube - Simple Version")
        
        # Set up OpenGL
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)  # Draw all faces
        
        # Set up perspective
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(config.FOV, config.WINDOW_WIDTH / config.WINDOW_HEIGHT, 0.1, 100.0)
        
        # Set up modelview matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -config.CAMERA_DISTANCE)
        
        self.initialized = True
        print("✓ Renderer initialized")
    
    def clear_screen(self):
        """Clear the screen."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    def apply_cube_rotation(self):
        """Apply cube rotation transformations."""
        glRotatef(self.cube_rotation_x, 1, 0, 0)
        glRotatef(self.cube_rotation_y, 0, 1, 0)
    
    def render_frame(self, cube):
        """Render a single frame."""
        self.clear_screen()
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -config.CAMERA_DISTANCE)
        
        # Apply cube rotation
        self.apply_cube_rotation()
        
        # Draw the cube
        self.draw_cube(cube)
        
        pygame.display.flip()
    
    def draw_cube(self, cube):
        """Draw the cube using the simplified cube representation."""
        # Get all stickers from all faces
        for face in config.FACE_NAMES:
            face_stickers = cube.get_face_stickers(face)
            for sticker in face_stickers:
                x, y, z = sticker.get_position()
                color = sticker.get_color()
                is_selected = sticker.is_sticker_selected()
                
                # Draw the sticker
                self.draw_sticker(x, y, z, face, color, is_selected)
    
    def draw_sticker(self, x, y, z, face, color, is_selected):
        """Draw a single sticker at the specified position."""
        # Define sticker vertices (square)
        vertices = [
            (-config.STICKER_SIZE, -config.STICKER_SIZE, 0),
            ( config.STICKER_SIZE, -config.STICKER_SIZE, 0),
            ( config.STICKER_SIZE,  config.STICKER_SIZE, 0),
            (-config.STICKER_SIZE,  config.STICKER_SIZE, 0),
        ]
        
        glPushMatrix()
        
        # Position the sticker directly at the calculated position
        glTranslatef(x, y, z)
        
        # Apply rotation based on face using the same logic as original
        face_config = config.FACE_CONFIGS[face]
        self.apply_face_rotation(face_config['rotation'])
        
        # Set color
        if is_selected:
            # Make selected stickers brighter
            color_rgb = config.COLOR_RGB.get(color, config.COLOR_RGB.get(color[0], (1, 1, 1)))
            bright_color = tuple(min(1.0, c * 1.5) for c in color_rgb)
            glColor3fv(bright_color)
        else:
            color_rgb = config.COLOR_RGB.get(color, config.COLOR_RGB.get(color[0], (1, 1, 1)))
            glColor3fv(color_rgb)
        
        # Draw sticker face
        glBegin(GL_QUADS)
        for v in vertices:
            glVertex3fv(v)
        glEnd()
        
        # Draw border using thicker lines or multiple lines
        if is_selected:
            glColor3f(*config.SELECTION_BORDER_COLOR)
            border_width = config.BORDER_WIDTH * 1.5  # Slightly thicker for selected
        else:
            glColor3f(*config.NORMAL_BORDER_COLOR)
            border_width = config.BORDER_WIDTH
        
        # Draw border as a thicker outline by drawing multiple lines
        num_lines = max(1, int(border_width * 20))  # Scale up for visibility
        for offset in range(num_lines):
            offset_val = offset * 0.005  # Small offset for each line
            border_vertices = [
                (-config.STICKER_SIZE - offset_val, -config.STICKER_SIZE - offset_val, 0),
                ( config.STICKER_SIZE + offset_val, -config.STICKER_SIZE - offset_val, 0),
                ( config.STICKER_SIZE + offset_val,  config.STICKER_SIZE + offset_val, 0),
                (-config.STICKER_SIZE - offset_val,  config.STICKER_SIZE + offset_val, 0),
            ]
            
            glBegin(GL_LINE_LOOP)
            for v in border_vertices:
                glVertex3fv(v)
            glEnd()
        
        glPopMatrix()
    
    def apply_face_rotation(self, rotation_type):
        """Apply rotation to orient the sticker correctly for its face."""
        # Same logic as the original working code
        if rotation_type == 'none':
            pass
        elif rotation_type == '180_x':
            glRotatef(180, 1, 0, 0)
        elif rotation_type == '180_y':
            glRotatef(180, 0, 1, 0)
        elif rotation_type == '90_x':
            glRotatef(90, 1, 0, 0)
        elif rotation_type == '-90_x':
            glRotatef(-90, 1, 0, 0)
        elif rotation_type == '90_y':
            glRotatef(90, 0, 1, 0)
        elif rotation_type == '-90_y':
            glRotatef(-90, 0, 1, 0)
        elif rotation_type == '90_z':
            glRotatef(90, 0, 0, 1)
        elif rotation_type == '-90_z':
            glRotatef(-90, 0, 0, 1)
        elif rotation_type == '90_y_90_x':
            glRotatef(90, 0, 1, 0)
            glRotatef(90, 1, 0, 0)
        elif rotation_type == '-90_y_90_x':
            glRotatef(-90, 0, 1, 0)
            glRotatef(90, 1, 0, 0)
    
    def handle_events(self, cube):
        """Handle Pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r:
                    cube.reset_to_solved()
                    print("✓ Cube reset")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button - cube rotation or face rotation
                    self.mouse_pressed = True
                    self.last_mouse_pos = event.pos
                    
                    # If a face is selected, start face rotation mode
                    if self.selected_sticker:
                        self.face_rotation_drag = True
                        self.face_rotation_start_pos = event.pos
                        print(f"✓ Started face rotation for {self.selected_sticker}")
                elif event.button == 3:  # Right mouse button - sticker selection
                    # Check if we clicked on a specific sticker
                    clicked_sticker_info = self.get_clicked_sticker_info(event.pos, cube)
                    if clicked_sticker_info:
                        sticker, face, i, j = clicked_sticker_info
                        self.selected_sticker = face
                        cube.set_selected_face(face)
                        print(f"✓ Selected sticker: Face {face}, Position ({i},{j})")
                        print(f"  Color: {sticker.get_color()}")
                        print(f"  Position: {sticker.get_position()}")
                        print(f"  Adjacents: {sticker.get_adjacents()}")
                    else:
                        self.selected_sticker = None
                        cube.set_selected_face(None)
                        print("No sticker selected")
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    self.mouse_pressed = False
                    if self.face_rotation_drag:
                        self.face_rotation_drag = False
                        self.face_rotation_triggered = False  # Reset for next rotation
                        print(f"✓ Finished face rotation for {self.selected_sticker}")
            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_pressed:
                    if self.face_rotation_drag and self.selected_sticker:
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
                            cube.rotate_face(self.selected_sticker, direction)
                            self.face_rotation_triggered = True
                        
                        self.last_mouse_pos = event.pos
                    else:
                        # Handle cube rotation
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

    def get_clicked_sticker_info(self, mouse_pos, cube):
        """Get the sticker that was clicked by calling the cube's method."""
        # Get viewport and modelview/projection matrices
        viewport = glGetIntegerv(GL_VIEWPORT)
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        
        # Call the cube's method to detect which sticker was clicked
        return cube.get_clicked_sticker(mouse_pos, viewport, modelview, projection) 