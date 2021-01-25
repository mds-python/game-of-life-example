import numpy as np


class Board:
    """Class responsible for holding the board state and updating it.

    This class creates and array holding the board and has the method `update`
    to update it according to game rules.

    Attributes:
        rise (set[int]): set containing possible numbers of neighbors of
                         an empty cell to make it alive
        fall (set[int]): set containing possible numbers of neighbors of
                         an alive cell to make it dead
        steps (int): number of color steps indicating cell age
        data (int): numpy array holding the board state

    Class attributes:
        UP, DOWN, LEFT, RIGHT: shift directions used by the `roll` method
    """


    UP = -1, 0
    DOWN = 1, 0
    LEFT = 0, -1
    RIGHT = 0, 1

    def __init__(self, size, pattern=None, dens=0.1, rule='23/3', steps=4):
        """Initialize board.

        Args:
            size (tuple[int, int]): size of the board
            pattern (str): basename of the pattern file to load; if missing, random board os generated
            dens (float): density of alive cells in random board
            rule (str): game rule in the form SSS/BB, where S is a number of neighbors of surviving cell and B of a new cell
            steps (int): number of color steps showing cell age
        """

        rule = rule.split('/')
        if rule[0].startswith('S') or rule[0].startswith('B'):
            rule = dict((r[0], r[1:]) for r in rule)
            rule = rule['S'], rule['B']

        self.rise = set(int(i) for i in rule[1])
        self.fall = set(range(9)) - set(int(i) for i in str(rule[0]))
        self.steps = steps
        vals = steps, 0
        size = size[1], size[0]  # numpy requires matrix dimensions as (ny, nx)
        if pattern is None:
            self.data = np.random.choice(vals, size, p=[dens, 1-dens])
        else:
            self.data = np.zeros(size, dtype=int)
            if pattern.endswith('.txt'):
                pattern = pattern[:-4]
            with open(f'{pattern}.txt') as source:
                loaded = np.array([list(line.rstrip()) for line in source.readlines() if not line.startswith('#')])
            stamp = np.zeros(loaded.shape, dtype=int)
            stamp[loaded != '.'] = steps
            if size[0] < stamp.shape[0] or size[1] < stamp.shape[1]:
                raise ValueError(f"Board too small, must be at least {stamp.shape}")
            d0, d1 = (np.random.randint(size[i] - stamp.shape[i]) for i in (0,1))
            self.data[d0:d0+stamp.shape[0],d1:d1+stamp.shape[1]] = stamp

    @property
    def size(self):
        """Board size
        """
        return self.data.shape

    def update(self):
        """Update the board.

        This method updates the board according to the rules defined in `rise` and `fall` atributes.
        """
        mask = np.zeros(self.size)
        mask[self.data != 0] = 1
        shifts = -1, 0, 1
        total = sum(np.roll(mask, (i,j), (0,1))
                    for i in shifts for j in shifts if i != 0 or j != 0)
        self.data[(self.data > 0) & (self.data < self.steps)] += 1
        for rise in self.rise:
            self.data[(mask == 0) & (total == rise)] = 1
        for fall in self.fall:
            self.data[(mask == 1) & (total == fall)] = 0

    def toggle(self, row, col):
        if 0 <= row < self.data.shape[0] and 0 <= col < self.data.shape[1]:
            if self.data[row, col] > 0:
                self.data[row, col] = 0
            else:
                self.data[row, col] = self.steps

    def roll(self, dir):
        """Shift the board.

        This method shifts the board in the specified direction. The board is wrapped along the edges.

        Args:
            dir (LEFT, RIGHT, UP, DOWN): shift direction
        """
        self.data = np.roll(self.data, dir, (0,1))
