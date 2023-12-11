import numpy as np
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *

from view_pygame import Display as DisplayBase


class Display(DisplayBase):
    """OpenGL display class.

    This class implements OpenGL display using PyGame engine.
    """

    VERTICES = ((0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5),
                (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5))
    SURFACES = ((0, 1, 2, 3), (3, 2, 7, 6), (6, 7, 5, 4), (4, 5, 1, 0), (1, 5, 7, 2), (4, 0, 3, 6))
    SHADES = (1.0, 0.9, 0.8, 0.7, 0.6, 0.5)

    def __init__(self, board, cmap='viridis'):
        """Initialize OpenGL display.

        Args:
            board (Board): board instance providing game logic
            cmap (str): color map name
        """
        super().__init__(board, cmap)

        # Initialize screen for OpenGL display
        self._size = 24 * np.array(board.size[::-1])
        self._screen = pygame.display.set_mode(self._size, DOUBLEBUF | OPENGL | GL_DEPTH)
        glEnable(GL_DEPTH_TEST)

        gluPerspective(45, (self._size[0] / self._size[1]), 0.1, 500.0)
        glRotate(180, 1, 0, 0)
        glTranslate(0.0, 0.0, max(board.size))

    def _draw(self):
        """Draw the screen.
        """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_POLYGON_OFFSET_FILL)
        glBegin(GL_LINES)
        glColor3fv((0.5, 0.5, 0.5))
        nj, ni = self.board.size
        dx, dy = np.array(self.board.size) / 2 + 0.5
        for i in range(ni + 1):
            glVertex3fv((i - dy, -dx, 0.5))
            glVertex3fv((i - dy, dx - 1, 0.5))
        for j in range(nj + 1):
            glVertex3fv((-dy, j - dx, 0.5))
            glVertex3fv((dy - 1, j - dx, 0.5))
        glEnd()
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(1.0, 1.0)
        for y, row in enumerate(self.board.data):
            for x, val in enumerate(row):
                if val > 0:
                    self._draw_cube(x, y, self._colors[val])

    def _draw_cube(self, x, y, color):
        """Draw a single cube.

        Args:
            x (int): x coordinate of the cube
            y (int): y coordinate of the cube
            color (tuple[float, float, float]): color of the cube
        """
        glBegin(GL_QUADS)
        for surface, shade in zip(self.SURFACES, self.SHADES):
            glColor3fv(shade * np.array(color) / 255)
            for iv in surface:
                vertex = list(self.VERTICES[iv])
                vertex[0] += x - self.board.size[1] / 2
                vertex[1] += y - self.board.size[0] / 2
                glVertex3fv(vertex)
        glEnd()

    def _event(self, event):
        """Additional PyGame event handler.

        This method allows to rotate and drag the board inside the display window.

        Args:
            event (Event): PyGame event
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button in (2, 3):
            self._mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button in (2, 3):
            self._mouse_pos = None
        elif event.type == pygame.MOUSEMOTION:
            if event.buttons == (0, 1, 0):
                if self._mouse_pos is not None:
                    dx, dy = (0.1 * (event.pos[i] - self._mouse_pos[i]) for i in (0, 1))
                    glTranslate(dx, dy, 0.)
                self._mouse_pos = event.pos
            if event.buttons == (0, 0, 1):
                if self._mouse_pos is not None:
                    dx, dy = (0.1 * (event.pos[i] - self._mouse_pos[i]) for i in (0, 1))
                    mods = pygame.key.get_mods()
                    x = event.pos[0] - self._size[0] / 2
                    y = event.pos[1] - self._size[1] / 2
                    if mods & KMOD_CTRL:
                        da = 600. * (x * dy - y * dx) / (x**2 + y**2)
                        glRotate(da, 0, 0, 1)
                    else:
                        glRotate(dx, 0, -1, 0)
                        glRotate(dy, 1, 0, 0)
                self._mouse_pos = event.pos
        elif event.type == pygame.MOUSEWHEEL:
            m4 = glGetDoublev(GL_MODELVIEW_MATRIX)
            vec = m4[:3] @ m4[3]
            vec *= 1. / np.linalg.norm(vec)
            glTranslate(-vec[0] * event.y, -vec[1] * event.y, -vec[2] * event.y)
            if glGetDoublev(GL_MODELVIEW_MATRIX)[3, 2] < 0:
                glLoadMatrixd(m4)


if __name__ == '__main__':
    import sys

    import main

    sys.argv.append('-vgl')
    main.main()
