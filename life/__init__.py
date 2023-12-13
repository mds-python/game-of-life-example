from .model import Board


class defaults:
    rule = '23/3'
    board = 100, 70
    pattern = None
    density = 0.1
    steps = 4
    fps = 8
    colormap = 'viridis'
    view = 'gl'
    fallback_views = ['pg2', 'mpl']


def select_display(view):
    try:
        if view == 'mpl':
            from .view.mpl import Display
        elif view == 'pg2':
            from .view.pygame import Display2D as Display
        elif view == 'pg3':
            from .view.pygame import Display3D as Display
        elif view == 'gl':
            from .view.opengl import Display
        else:
            raise ValueError("Unrecognized view engine")
        return Display
    except ImportError:
        if view in defaults.fallback_views:
            defaults.fallback_views.remove(view)
        if not defaults.fallback_views:
            raise
        print("Falling back to {}".format(defaults.fallback_views[0]))
        return select_display(defaults.fallback_views[0])


def game(
    rule=defaults.rule,
    board=defaults.board,
    pattern=defaults.pattern,
    density=defaults.density,
    steps=defaults.steps,
    fps=defaults.fps,
    colormap=defaults.colormap,
    view=defaults.view
):
    """Show Game of Life.

    This shows a Conway's Game of Life.

    Args:
        rule (str): game rule in the form SSS/BB, where S is a number of neighbors of surviving cell and B of a new cell
        board (tuple[int,int]): size of the board
        pattern (str): filename of the pattern
        density (float): density of live cells in a random board
        steps (int): number of color steps showing cell age
        fps (float): number of animation frames per second
        colormap (str): display color map
        view {'mpl', 'pg2', 'pg3'}: view engine
    """

    board = Board(size=board, pattern=pattern, dens=density, rule=rule, steps=steps)

    Display = select_display(view)

    display = Display(board, colormap)
    display.animate(fps)


def main():
    import argparse

    class DensityStore(argparse.Action):

        def __call__(self, parser, namespace, values, option_string=None):
            if values < 0 or values > 1:
                raise argparse.ArgumentError(self, "Density must be in range [0, 1]")
            setattr(namespace, self.dest, values)

    parser = argparse.ArgumentParser()

    parser.description = "Show Conway's Game of Life. Play with the parameters and have fun!"

    parser.add_argument(
        '-r',
        '--rule',
        type=str,
        default=defaults.rule,
        help="game rule in the form SSS/BB, where S is a number of neighbors of surviving cell and B of a new cell"
    )
    parser.add_argument(
        '-b', '--board', type=int, nargs=2, metavar=('WIDTH', 'HEIGHT'), default=defaults.board, help="size of the board"
    )
    parser.add_argument('-p', '--pattern', type=str, default=defaults.pattern, help="filename of the pattern")
    parser.add_argument(
        '-d',
        '--density',
        type=float,
        action=DensityStore,
        default=defaults.density,
        help="density of live cells in a random board",
    )
    parser.add_argument('-s', '--steps', type=int, default=defaults.steps, help="number of color steps showing cell age")
    parser.add_argument('-f', '--fps', type=float, default=defaults.fps, help="number of animation frames per second")
    parser.add_argument('-c', '--colormap', type=str, default=defaults.colormap, help="display color map")
    parser.add_argument('-v', '--view', type=str, default=defaults.view, choices=('mpl', 'pg2', 'pg3', 'gl'), help="view engine")

    game(**vars(parser.parse_args()))


if __name__ == '__main__':
    main()
