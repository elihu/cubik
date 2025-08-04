# main_rubiks.py
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math

# ===============================================================
# --- CONFIGURACIÓN PRINCIPAL ---
# ¡Cambia este valor para tener un cubo 2x2, 3x3, 4x4, etc.!
N = 3
# ===============================================================

# --- Constantes ---
CUBIE_SIZE = 0.95  # Tamaño de un cubito individual (menor a 1 para ver los bordes)
ANIMATION_SPEED = 6  # Grados por fotograma (más alto = más rápido)

# Colores de las caras en formato RGB (0-1)
COLORS = {
    'U': (1, 1, 1),       # Blanco (Up)
    'D': (1, 1, 0),       # Amarillo (Down)
    'F': (0, 0.8, 0),     # Verde (Front)
    'B': (0, 0, 1),       # Azul (Back)
    'R': (1, 0, 0),       # Rojo (Right)
    'L': (1, 0.5, 0),     # Naranja (Left)
    'INSIDE': (0.1, 0.1, 0.1)  # Color interior de los cubies
}

# Define las caras de un cubie y a qué dirección normal apuntan
FACES = {
    (0, 1, 0): 'U', (0, -1, 0): 'D',
    (0, 0, 1): 'F', (0, 0, -1): 'B',
    (1, 0, 0): 'R', (-1, 0, 0): 'L'
}

# --- Clase para cada pieza del cubo ---

class Cubie:
    """Representa un único cubito del cubo de Rubik."""
    def __init__(self, pos):
        # La posición lógica (ej: (-1, 1, 1) para una esquina)
        self.pos = np.array(pos, dtype=float)
        # La matriz de transformación que guarda su posición y rotación en el espacio 3D
        self.matrix = np.identity(4)
        # Lo movemos a su posición inicial
        self.matrix[0:3, 3] = self.pos

    def draw(self, animating_matrix=None):
        """Dibuja el cubie aplicando su matriz de transformación y la de animación si existe."""
        glPushMatrix()

        # Si el cubie está en movimiento, aplicamos la rotación de la animación
        if animating_matrix is not None:
            glMultMatrixf(animating_matrix.T)

        # Aplicamos la transformación propia del cubie (su posición y orientación actual)
        glMultMatrixf(self.matrix.T)

        # Dibujamos las 6 caras del cubito
        glBegin(GL_QUADS)
        s = CUBIE_SIZE / 2.0
        for normal, face_name in FACES.items():
            # Solo coloreamos las caras que están en el exterior del cubo grande
            is_outer_face = round(np.dot(self.pos, normal)) == (N - 1) / 2.0
            color = COLORS[face_name] if is_outer_face else COLORS['INSIDE']
            glColor3fv(color)
            glNormal3fv(normal)

            # Creamos los 4 vértices de la cara usando un poco de álgebra vectorial
            p1 = np.array([-s, -s, s])
            p2 = np.array([s, -s, s])
            p3 = np.array([s, s, s])
            p4 = np.array([-s, s, s])
            
            # Rotamos los vértices para que coincidan con la orientación de la normal
            if normal[0] != 0: # Caras R/L
                rotation = self.get_rotation_matrix(90 * normal[0], (0, 1, 0))
            elif normal[1] != 0: # Caras U/D
                rotation = self.get_rotation_matrix(-90 * normal[1], (1, 0, 0))
            else: # Caras F/B
                rotation = self.get_rotation_matrix(180 if normal[2] < 0 else 0, (0, 1, 0))
            
            glVertex3fv(np.dot(rotation, p1))
            glVertex3fv(np.dot(rotation, p2))
            glVertex3fv(np.dot(rotation, p3))
            glVertex3fv(np.dot(rotation, p4))
        glEnd()

        glPopMatrix()

    def get_rotation_matrix(self, angle, axis):
        """Devuelve una matriz de rotación simple (sin numpy para simplicidad aquí)."""
        c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        x, y, z = axis
        return np.array([
            [c + x*x*(1-c),   x*y*(1-c) - z*s, x*z*(1-c) + y*s],
            [y*x*(1-c) + z*s, c + y*y*(1-c),   y*z*(1-c) - x*s],
            [z*x*(1-c) - y*s, z*y*(1-c) + x*s, c + z*z*(1-c)]
        ])

# --- Clase principal que gestiona el cubo ---

class RubiksCube:
    """Gestiona el conjunto de cubies, las rotaciones y el dibujado."""
    def __init__(self, n):
        self.n = n
        # El margen nos ayuda a calcular las coordenadas de -X a +X
        margin = (self.n - 1) / 2.0
        # Creamos la lista de cubies en sus posiciones iniciales
        self.cubies = [Cubie((x, y, z))
                       for x in np.linspace(-margin, margin, self.n)
                       for y in np.linspace(-margin, margin, self.n)
                       for z in np.linspace(-margin, margin, self.n)]

        # Estado de la animación
        self.is_animating = False
        self.animation_cubies = []
        self.animation_axis = None
        self.animation_angle = 0
        self.animation_target_angle = 0

        # Rotación de la vista del cubo entero (controlada por el usuario)
        self.view_rot_x = -30
        self.view_rot_y = -45

    def get_rotation_matrix(self, angle, axis):
        """Genera una matriz de rotación 4x4 para OpenGL."""
        c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        if axis == 'x': return np.array([[1, 0, 0, 0], [0, c,-s, 0], [0, s, c, 0], [0, 0, 0, 1]], dtype=float)
        if axis == 'y': return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s,0, c, 0], [0, 0, 0, 1]], dtype=float)
        if axis == 'z': return np.array([[c,-s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=float)

    def start_move(self, axis, slice_index, direction):
        """Prepara una animación de giro si no hay otra en curso."""
        if self.is_animating: return

        self.is_animating = True
        self.animation_axis = axis
        self.animation_target_angle = 90 * direction
        self.animation_angle = 0
        
        # Selecciona los cubies que pertenecen a la capa (slice) a girar
        axis_map = {'x': 0, 'y': 1, 'z': 2}
        self.animation_cubies = [c for c in self.cubies if round(c.pos[axis_map[axis]]) == slice_index]

    def update_animation(self):
        """Avanza la animación un paso y la finaliza si llega al objetivo."""
        if not self.is_animating: return

        # Avanzamos el ángulo
        self.animation_angle += ANIMATION_SPEED * np.sign(self.animation_target_angle)
        
        # Si hemos llegado o pasado del ángulo objetivo, terminamos
        if abs(self.animation_angle) >= abs(self.animation_target_angle):
            self.animation_angle = self.animation_target_angle
            self.finish_move()

    def finish_move(self):
        """Finaliza la animación actualizando las matrices y posiciones lógicas de los cubies."""
        rot_matrix = self.get_rotation_matrix(self.animation_target_angle, self.animation_axis)
        
        for cubie in self.animation_cubies:
            # 1. Actualiza la matriz de transformación permanente
            cubie.matrix = np.dot(rot_matrix, cubie.matrix)
            # 2. Actualiza la posición lógica para futuros giros
            cubie.pos = np.round(np.dot(rot_matrix[:3, :3], cubie.pos))
        
        # Resetea el estado de animación
        self.is_animating = False
        self.animation_cubies = []

    def draw(self):
        """Dibuja el cubo entero, aplicando animaciones si es necesario."""
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Posicionamiento y rotación de la cámara/vista
        glTranslatef(0, 0, -5 * N) # Alejamos la cámara según el tamaño del cubo
        glRotatef(self.view_rot_x, 1, 0, 0)
        glRotatef(self.view_rot_y, 0, 1, 0)
        
        self.update_animation()

        # Matriz de animación temporal que se aplicará a los cubies en movimiento
        anim_matrix = self.get_rotation_matrix(self.animation_angle, self.animation_axis) if self.is_animating else None
        
        for cubie in self.cubies:
            # Si el cubie es parte de la animación actual, se le pasa la matriz temporal
            if cubie in self.animation_cubies:
                cubie.draw(anim_matrix)
            else:
                cubie.draw()

# --- Función Principal (Bucle de Pygame) ---

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption(f"Cubo de Rubik {N}x{N} | Controles: U,D,R,L,F,B (+Shift)")

    # Configuración de la perspectiva de OpenGL
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    
    cube = RubiksCube(N)
    clock = pygame.time.Clock()

    # Mapeo de teclas a movimientos (eje, capa, dirección base)
    margin = (N - 1) / 2.0
    key_map = {
        pygame.K_u: ('y', margin, 1),       # Up
        pygame.K_d: ('y', -margin, -1),     # Down
        pygame.K_r: ('x', margin, 1),       # Right
        pygame.K_l: ('x', -margin, -1),     # Left
        pygame.K_f: ('z', margin, 1),       # Front
        pygame.K_b: ('z', -margin, -1),     # Back
    }
    
    mouse_down = False
    last_mouse_pos = (0, 0)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key in key_map:
                    mods = pygame.key.get_mods()
                    direction = -1 if mods & pygame.KMOD_SHIFT else 1
                    axis, slice_idx, base_dir = key_map[event.key]
                    cube.start_move(axis, slice_idx, direction * base_dir)
            
            # Controles de la cámara con el ratón
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
                last_mouse_pos = event.pos
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_down = False
            if event.type == pygame.MOUSEMOTION and mouse_down:
                dx, dy = event.pos[0] - last_mouse_pos[0], event.pos[1] - last_mouse_pos[1]
                cube.view_rot_y += dx * 0.5
                cube.view_rot_x += dy * 0.5
                last_mouse_pos = event.pos

        cube.draw()
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()