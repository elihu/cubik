"""
main.py

This script renders a 3D Rubik's Cube (3x3x3) using Pygame and PyOpenGL.
No interaction yet, just a rotating cube for visualization.
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
import math

# Standard Rubik's Cube colors (U: white, D: yellow, F: red, B: orange, L: blue, R: green)
FACE_COLORS = [
    (1, 1, 1),      # Up - White
    (1, 1, 0),      # Down - Yellow
    (1, 0, 0),      # Front - Red
    (1, 0.5, 0),    # Back - Orange
    (0, 0, 1),      # Left - Blue
    (0, 1, 0),      # Right - Green
]

# Vertices of a unit cube centered at origin
CUBE_VERTICES = [
    (-0.5, -0.5, -0.5),
    ( 0.5, -0.5, -0.5),
    ( 0.5,  0.5, -0.5),
    (-0.5,  0.5, -0.5),
    (-0.5, -0.5,  0.5),
    ( 0.5, -0.5,  0.5),
    ( 0.5,  0.5,  0.5),
    (-0.5,  0.5,  0.5),
]

# Each face as a list of 4 vertex indices
CUBE_FACES = [
    (0, 1, 2, 3),  # Bottom
    (4, 5, 6, 7),  # Top
    (0, 1, 5, 4),  # Front
    (2, 3, 7, 6),  # Back
    (1, 2, 6, 5),  # Right
    (0, 3, 7, 4),  # Left
]

def draw_cubie(x, y, z, size=1.0, gap=0.05):
    """
    Draws a single cubie at (x, y, z) with the given size and gap.
    Faces are colored only if they are on the outer layer.
    """
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(size - gap, size - gap, size - gap)
    for i, face in enumerate(CUBE_FACES):
        # Only draw outer faces
        if (
            (i == 0 and y < 0) or (i == 1 and y > 0) or
            (i == 2 and z < 0) or (i == 3 and z > 0) or
            (i == 4 and x > 0) or (i == 5 and x < 0)
        ):
            glBegin(GL_QUADS)
            glColor3fv(FACE_COLORS[i])
            for vertex in face:
                glVertex3fv(CUBE_VERTICES[vertex])
            glEnd()
        else:
            # Draw black for internal faces
            glBegin(GL_QUADS)
            glColor3f(0.05, 0.05, 0.05)
            for vertex in face:
                glVertex3fv(CUBE_VERTICES[vertex])
            glEnd()
    glPopMatrix()

def draw_rubiks_cube():
    """
    Draws a 3x3x3 Rubik's Cube by drawing 27 cubies.
    """
    for x in [-1, 0, 1]:
        for y in [-1, 0, 1]:
            for z in [-1, 0, 1]:
                draw_cubie(x, y, z)

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -15)

    clock = pygame.time.Clock()
    angle = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glRotatef(angle, 1, 1, 0)
        draw_rubiks_cube()
        glPopMatrix()
        pygame.display.flip()
        clock.tick(60)
        angle += 0.5
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 