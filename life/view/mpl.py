import numpy as np

import matplotlib.pyplot as plt
import matplotlib.animation as animation

from ..model import Board


class Display:
    """Class responsible for display using Matplotlib.

    This class has identical interface as any other display class, so they can be used interchangeably.
    The constructor takes the board object that controls the logic of the game and the optional color map
    name.

    The class itself provides a method to start animation and is responsible for handling the user interaction
    i.e. starting or stopping the animation with SPACE and cell editing.

    Attributes:
        board (Board): board instance providing game logic
        running (bool): whether the animation is running or held
    """

    def __init__(self, board, cmap='viridis', fullscreen=False):
        """Initialize display.

        Args:
            board (Board): board instance providing game logic
            cmap (str): color map name
            fullscreen (bool): whether to show the display in fullscreen mode
        """
        self.running = True
        self.board = board

        # Create the plot
        self._figure, self._axes = plt.subplots()
        self._image = self._axes.matshow(np.log(board.data+1), cmap=cmap, interpolation='nearest')
        self._axes.xaxis.set_major_locator(plt.NullLocator())
        self._axes.yaxis.set_major_locator(plt.NullLocator())
        plt.tight_layout()

        self._figure.canvas.manager.set_window_title("Game of Life (matplotlib)")

        # Add Matplotlib event handlers
        self._figure.canvas.mpl_connect('key_press_event', self._key_press_event)
        self._figure.canvas.mpl_connect('button_press_event', self._click_event)

        if fullscreen:
            self._figure.canvas.manager.full_screen_toggle()

    def animate(self, fps):
        """Show the plot and start the animation.

        Args:
            fps (int): animation speed (frames per second)
        """
        self._animation = animation.FuncAnimation(self._figure, self._update, interval=1000/fps, blit=True)
        plt.show()

    def _update_plot(self):
        """Update the image data from the board data."""
        self._image.set_data(np.log(self.board.data+1))

    def _update(self, data):
        """This method is called by Matplotlib animation for each frame

        Args:
            data (ignored): data to update provided by Matplotlib; we ignore is, as it is kept in the board object

        Returns:
            tuple: 1-element tuple containg updated image
        """
        if self.running:
            self.board.update()
            self._update_plot()
        return self._image,

    def _key_press_event(self, event):
        """Key press event handler.

        Args:
            event (Event): Matplotlib event object holding e.g. the pressed key
        """
        if event.key == ' ':
            # Pause/unpause on SPACE
            self.running = not self.running
        else:
            # Shift board on arrows
            dir = {'left': Board.LEFT, 'right': Board.RIGHT, 'up': Board.UP, 'down': Board.DOWN}.get(event.key)
            if dir is not None:
                self.board.roll(dir)

    def _click_event(self, event):
        """Mouse click event handler.

        Args:
            event (Event): Matplotlib event object holding e.g. the mouse button and clicked coordinates
        """
        if event.button == 1:
            x, y = (int(round(xy)) for xy in (event.xdata, event.ydata))  # compute board coordinates
            self.board.toggle(y, x)  # change board state
            self._update_plot()
            plt.draw()
