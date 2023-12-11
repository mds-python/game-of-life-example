#!/usr/bin/env python
from model import Board


class Defaults:
    rule = '23/3'
    board = 100, 70
    pattern = None
    density = 0.1
    steps = 4
    fps = 8
    colormap = 'viridis'
    view = 'pg2'


def game(rule=Defaults.rule, board=Defaults.board, pattern=Defaults.pattern, density=Defaults.density,
         steps=Defaults.steps, fps=Defaults.fps, colormap=Defaults.colormap, view=Defaults.view):
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

    if view == 'mpl':
        from view_mpl import Display
    elif view == 'pg2':
        from view_pygame import Display2D as Display
    elif view == 'pg3':
        from view_pygame import Display3D as Display
    elif view == 'gl':
        from view_opengl import Display
    else:
        raise ValueError("Unrecognized view engine")

    display = Display(board, colormap)
    display.animate(fps)


def main():
    import argparse

    parser = argparse.ArgumentParser()

    parser.description = "Show Conway's Game of Life. Play with the parameters and have fun!"

    parser.add_argument('-r', '--rule', type=str, default=Defaults.rule,
                        help="game rule in the form SSS/BB, where S is a number of neighbors of surviving cell and B of a new cell")
    parser.add_argument('-b', '--board', type=int, nargs=2, metavar=('WIDTH', 'HEIGHT'), default=Defaults.board,
                        help="size of the board")
    parser.add_argument('-p', '--pattern', type=str, default=Defaults.pattern,
                        help="filename of the pattern")
    parser.add_argument('-d', '--density', type=float, default=Defaults.density,
                        help="density of live cells in a random board")
    parser.add_argument('-s', '--steps', type=int, default=Defaults.steps,
                        help="number of color steps showing cell age")
    parser.add_argument('-f', '--fps', type=float, default=Defaults.fps,
                        help="number of animation frames per second")
    parser.add_argument('-c', '--colormap', type=str, default=Defaults.colormap,
                        help="display color map")
    parser.add_argument('-v', '--view', type=str, default=Defaults.view, choices=('mpl', 'pg2', 'pg3', 'gl'),
                        help="view engine")

    game(**vars(parser.parse_args()))


if __name__ == '__main__':
    main()
