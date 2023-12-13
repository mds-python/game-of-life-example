import os

import pygame
from matplotlib import cm as colormaps

from ..model import Board


class Display:
    """Class responsible for display using PyGame.

    This class has identical interface as any other display class, so they can be used interchangeably.
    The constructor takes the board object that controls the logic of the game and the optional color map
    name.

    The class itself provides a method to start animation and is responsible for handling the user interaction
    i.e. starting or stopping the animation with SPACE and cell editing.

    This is a base class for particular display codes (2D and pseudo-3D). It is so and ‘abstract class’, which
    means, you must not create object of this class, but only of the child classes.

    Attributes:
        board (Board): board instance providing game logic
        running (bool): whether the animation is running or held
    """

    def __init__(self, board, cmap):
        """Initialize display.

        Args:
            board (Board): board instance providing game logic
            cmap (str): color map name
        """
        self.running = True
        self.board = board

        # Initialize PyGame
        pygame.init()
        pygame.display.set_caption("Game of Life (PyGame)")

        # Get possible colors from Matplotlib and store them for future use as RGB tuples
        cmap = getattr(colormaps, cmap)
        self._colors = [
            tuple(int(c * 255) for c in color[:3]) for color in (cmap(val / board.steps) for val in range(board.steps + 1))
        ]

    def _draw(self):
        """Draw the screen.
        """
        raise NotImplementedError  # `_draw` method does not exits in this class, but must be present in the child classes

    def _getxy(self, pos):
        """Calculate board coordinates for provided mouse screen position.

        Args:
            pos (tuple[int, int]): mouse position in pixels

        Returns:
            tuple[int, int]: board coordinates in cells
        """

    def animate(self, fps):
        """Show the plot and start the animation.

        This method provides display/event loop.

        Args:
            fps (int): animation speed (frames per second)
        """
        clock = pygame.time.Clock()

        game_loop = True
        while game_loop:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Pause/unpause on SPACE
                        self.running = not self.running
                    elif event.key == pygame.K_q:
                        game_loop = False
                    else:
                        # Shift board on arrows
                        dir = {
                            pygame.K_LEFT: Board.LEFT,
                            pygame.K_RIGHT: Board.RIGHT,
                            pygame.K_UP: Board.UP,
                            pygame.K_DOWN: Board.DOWN
                        }.get(event.key)
                        if dir is not None:
                            self.board.roll(dir)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Toggle cell on mouse click
                    pos = pygame.mouse.get_pos()
                    xy = self._getxy(pos)
                    if xy is not None:
                        self.board.toggle(*xy)
                elif event.type == pygame.QUIT:
                    # In PyGame this event MUST be handled (terminating the game loop)
                    game_loop = False
                # Child class may provide additional events handling
                self._event(event)
            pygame.event.pump()

            # Update the board according to game logic
            if self.running:
                self.board.update()

            # Show changes
            self._draw()
            pygame.display.flip()

            clock.tick(fps)

    def _event(self, event):
        """Additional PyGame event handler.

        By default this method does nothing, as everything standard in handled in the `animate` method.

        Args:
            event (Event): PyGame event
        """
        pass


class Display2D(Display):
    """2D PyGame display class.

    This class implements 2D display using PyGame engine.

    Class attributes:
        CELL_SIZE (int): size of a single cell
    """

    CELL_SIZE = 12

    def __init__(self, board, cmap='viridis'):
        """Initialize 2D display.

        Args:
            board (Board): board instance providing game logic
            cmap (str): color map name
        """
        super().__init__(board, cmap)

        # Initialize screen for 2D display
        size = board.size[1] * self.CELL_SIZE, board.size[0] * self.CELL_SIZE
        self._screen = pygame.display.set_mode(size, pygame.SCALED | pygame.RESIZABLE)

    def _getxy(self, pos):
        """Calculate board coordinates for provided mouse screen position.

        Args:
            pos (tuple[int, int]): mouse position in pixels

        Returns:
            tuple[int, int]: board coordinates in cells
        """
        return pos[1] // self.CELL_SIZE, pos[0] // self.CELL_SIZE

    def _draw(self):
        """Draw the screen.
        """
        self._screen.fill((32, 48, 64))
        for y, row in enumerate(self.board.data):
            for x, val in enumerate(row):
                if val > 0:
                    pygame.draw.rect(
                        self._screen, (self._colors[val]), (x * self.CELL_SIZE, y * self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE)
                    )


class Display3D(Display):
    """Pseudo-3D PyGame display class.

    This class implements pseudo-3D display using PyGame engine.
    """

    def __init__(self, board, cmap='viridis'):
        """Initialize pseudo-3D display.

        Args:
            board (Board): board instance providing game logic
            cmap (str): color map name
        """
        super().__init__(board, cmap)

        size = board.size[0] + board.size[1]
        self._size = 48 + 15 * size, 64 + 8 * size
        self._screen = pygame.display.set_mode(self._size, pygame.SCALED | pygame.RESIZABLE)

        self._dx = self._dy = 0
        self._mouse_pos = None

        colors = self._colors[1:]
        dirname = os.path.dirname(__file__)
        box = pygame.image.load(os.path.join(dirname, 'box.png'))
        self._boxes = [box.copy() for _ in colors]
        for i, c in enumerate(colors):
            self._boxes[i].fill(c, special_flags=pygame.BLEND_MULT)

    def _draw(self):
        """Draw the screen.
        """
        self._screen.fill((0, 0, 0))
        ni, nj = self.board.size
        xy = [(16 + 15 * (i + j) + self._dx, 38 + 8 * (nj - j + i) + self._dy) for i, j in ((0, 0), (0, nj), (ni, nj), (ni, 0))]
        pygame.draw.polygon(self._screen, (32, 48, 64), xy)
        for i in range(ni + 1):
            x0, y0 = 16 + 15 * (i) + self._dx, 38 + 8 * (nj + i) + self._dy
            x1, y1 = 16 + 15 * (i + nj) + self._dx, 38 + 8 * i + self._dy
            pygame.draw.line(self._screen, (32, 32, 32), (x0, y0), (x1, y1))
        for j in range(nj + 1):
            x0, y0 = 16 + 15 * j + self._dx, 38 + 8 * (nj - j) + self._dy
            x1, y1 = 16 + 15 * (ni + j) + self._dx, 38 + 8 * (nj - j + ni) + self._dy
            pygame.draw.line(self._screen, (32, 32, 32), (x0, y0), (x1, y1))
        for i, row in enumerate(self.board.data):
            for j, val in reversed(list(enumerate(row))):
                if val > 0:
                    x, y = 16 + 15 * (i + j) + self._dx, 16 + 8 * (nj - j + i) + self._dy
                    self._screen.blit(self._boxes[val - 1], (x, y, 31, 31))

    def _getxy(self, pos):
        """Calculate board coordinates for provided mouse screen position.

        Args:
            pos (tuple[int, int]): mouse position in pixels

        Returns:
            tuple[int, int]: board coordinates in cells
        """
        x, y = pos
        nj = self.board.size[1]
        i = (((x - self._dx - 32) / 15 + (y - self._dy - 32) / 8) - nj) / 2
        j = (((x - self._dx - 32) / 15 - (y - self._dy - 32) / 8) + nj) / 2
        return int(i), int(j)

    def _event(self, event):
        """Additional PyGame event handler.

        This method allows to drag the board inside the display window.

        Args:
            event (Event): PyGame event
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
            self._mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:
            self._mouse_pos = None
        elif event.type == pygame.MOUSEMOTION and event.buttons == (0, 1, 0):
            if self._mouse_pos is not None:
                dx, dy = (event.pos[i] - self._mouse_pos[i] for i in (0, 1))
                self._dx += dx
                self._dy += dy
            self._mouse_pos = event.pos
