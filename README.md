# Game of Life example

This is an example implementation of the [Conway's Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life).

The main purpose of this code is illustration of a good object-oriented design. The code is organized as follows:

* `life.py` is the main file to run. It reads the game parameters from the command line (see below) and creates `Board`
  and `Display` class instances.
* `model.py` holds the `Board` class that is responsible for game logic (model).
* `view_mpl.py`  and `view_pygame.py` are hold classes responsible for display of the board and user interaction (views).
  They use different engines to demonstrate that the good code organization allows to easily change the engine. Only one
  of these files is imported, depending on the parameters.
* All the `*.txt` files contain sample patterns.


## Running the program

Open the command line console and type

```
python life.py [OPTIONS]
```

where `[OPTIONS]` are optional arguments and can be:

* `-h` or `--help` show help message and exit,
* `-r RULE` or `--rule RULE` game rule (see below),
* `-b WIDTH HEIGHT` or `--board WIDTH HEIGHT` size of the board,
* `-p PATTERN` or `--pattern PATTERN` filename of the pattern,
* `-d DENSITY` or `--density DENSITY` density of live cells in a random board,
* `-s STEPS` or `--steps STEPS` number of color steps showing cell age,
* `-f FPS` or `--fps FPS` number of animation frames per second,
* `-c COLORMAP` or `--colormap COLORMAP` display color map,
* `-v ENGINE` or `--view ENGINE` view engine (can be `mpl` or `pg2`, `pg3`, or `gl`),
* `-F` or `--fullscreen` start in fullscreen mode.

## Other interesting rules

The default Game of life rule set is `B3/S23`, which means that a new cell is born if it has exactly 3 neighbors and any alive
cell survives only if it has 2 or 3 neighbors.
However, [different rules](https://www.conwaylife.com/wiki/List_of_Life-like_cellular_automata) are possible. Some particularly interesting behaviors are summarized below:

| Rule           | Description            |
| -------------- | ---------------------- |
| `B45678/S2345` | walled cities          |
| `B345/S4567`   | diamond shape patterns |
