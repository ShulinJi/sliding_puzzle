from copy import deepcopy
from heapq import heappush, heappop
import time
import argparse
import sys

# ====================================================================================

char_goal = '1'
char_single = '2'


class Piece:
    """
    This represents a piece on the Hua Rong Dao puzzle.
    """

    def __init__(self, is_goal, is_single, coord_x, coord_y, orientation):
        """
        :param is_goal: True if the piece is the goal piece and False otherwise.
        :type is_goal: bool
        :param is_single: True if this piece is a 1x1 piece and False otherwise.
        :type is_single: bool
        :param coord_x: The x coordinate of the top left corner of the piece.
        :type coord_x: int
        :param coord_y: The y coordinate of the top left corner of the piece.
        :type coord_y: int
        :param orientation: The orientation of the piece (one of 'h' or 'v')
            if the piece is a 1x2 piece. Otherwise, this is None
        :type orientation: str
        """

        self.is_goal = is_goal
        self.is_single = is_single
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.orientation = orientation

    def __repr__(self):
        return '{} {} {} {} {}'.format(self.is_goal, self.is_single,
                                       self.coord_x, self.coord_y, self.orientation)


class Board:
    """
    Board class for setting up the playing board.
    """

    def __init__(self, pieces):
        """
        :param pieces: The list of Pieces
        :type pieces: List[Piece]
        """

        self.width = 4
        self.height = 5

        self.pieces = pieces

        # self.grid is a 2-d (size * size) array automatically generated
        # using the information on the pieces when a board is being created.
        # A grid contains the symbol for representing the pieces on the board.
        self.grid = []
        self.__construct_grid()

    def __construct_grid(self):
        """
        Called in __init__ to set up a 2-d grid based on the piece location information.

        """

        for i in range(self.height):
            line = []
            for j in range(self.width):
                line.append('.')
            self.grid.append(line)

        for piece in self.pieces:
            if piece.is_goal:
                self.grid[piece.coord_y][piece.coord_x] = char_goal
                self.grid[piece.coord_y][piece.coord_x + 1] = char_goal
                self.grid[piece.coord_y + 1][piece.coord_x] = char_goal
                self.grid[piece.coord_y + 1][piece.coord_x + 1] = char_goal
            elif piece.is_single:
                self.grid[piece.coord_y][piece.coord_x] = char_single
            else:
                if piece.orientation == 'h':
                    self.grid[piece.coord_y][piece.coord_x] = '<'
                    self.grid[piece.coord_y][piece.coord_x + 1] = '>'
                elif piece.orientation == 'v':
                    self.grid[piece.coord_y][piece.coord_x] = '^'
                    self.grid[piece.coord_y + 1][piece.coord_x] = 'v'

    def display(self):
        """
        Print out the current board.

        """
        for i, line in enumerate(self.grid):
            for ch in line:
                print(ch, end='')
            print()


class State:
    """
    State class wrapping a Board with some extra current state information.
    Note that State and Board are different. Board has the locations of the pieces.
    State has a Board and some extra information that is relevant to the search:
    heuristic function, f value, current depth and parent.
    """

    def __init__(self, board, f, depth, parent=None):
        """
        :param board: The board of the state.
        :type board: Board
        :param f: The f value of current state.
        :type f: int
        :param depth: The depth of current state in the search tree.
        :type depth: int
        :param parent: The parent of current state.
        :type parent: Optional[State]
        """
        self.board = board
        self.f = f
        self.depth = depth
        self.parent = parent
        self.id = hash(board)  # The id for breaking ties.
    """
    # overload operator to compare class based on their heuristic value
    def __lt__(self, other):
        if self.heuristic < other.heuristic:
            return self
        else:
            return other
    """


def read_from_file(filename):
    """
    Load initial board from a given file.

    :param filename: The name of the given file.
    :type filename: str
    :return: A loaded board
    :rtype: Board
    """

    puzzle_file = open(filename, "r")

    line_index = 0
    pieces = []
    g_found = False

    for line in puzzle_file:

        for x, ch in enumerate(line):

            if ch == '^':  # found vertical piece
                pieces.append(Piece(False, False, x, line_index, 'v'))
            elif ch == '<':  # found horizontal piece
                pieces.append(Piece(False, False, x, line_index, 'h'))
            elif ch == char_single:
                pieces.append(Piece(False, True, x, line_index, None))
            elif ch == char_goal:
                if g_found == False:
                    pieces.append(Piece(True, False, x, line_index, None))
                    g_found = True
        line_index += 1

    puzzle_file.close()

    board = Board(pieces)

    return board


board_visited_set = set()
board_visited = []


def dfs(initial_state):
    # a list that contains all the visited board and if encounter the same situation, discard the one has more depth

    # the frontier queue used by the dfs (stack)
    # first_state = State(game_board, 0, 0, None)
    # board_visited.append(first_state)
    stack = [initial_state]

    while len(stack):
        next_state = stack.pop()
        # next_state.board.display()

        if str(next_state.board.grid) not in board_visited_set:
            board_visited_set.add(str(next_state.board.grid))
        game_board = next_state.board
        board_grid = next_state.board.grid
        # find the coordinate of two white space of two white space
        if board_grid[3][1] == char_goal and board_grid[3][2] == char_goal \
                and board_grid[4][1] == char_goal and board_grid[4][2] == char_goal:
            return next_state
        """
        coordinate_space = []
        for x in range(0, 4):
            for y in range(0, 5):
                if board_grid[x][y] is '.':
                    coordinate_space.append([x, y])
        white_space1 = coordinate_space[0]
        """
        for x in range(0, 5):
            for y in range(0, 4):
                if board_grid[x][y] == '^':
                    # move to the left for 2x1 (vertical)
                    if y != 0:
                        if board_grid[x][y - 1] == '.' and board_grid[x + 1][y - 1] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = '.'
                            game_board_copy.grid[x + 1][y] = '.'
                            game_board_copy.grid[x][y - 1] = '^'
                            game_board_copy.grid[x + 1][y - 1] = 'v'

                            # check duplicate
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, 0, next_state.depth + 1, next_state)
                                stack.append(new_state)
                    # move to the right for 2x1 (vertical)
                    if y != 3:
                        if board_grid[x][y + 1] == '.' and board_grid[x + 1][y + 1] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = '.'
                            game_board_copy.grid[x + 1][y] = '.'
                            game_board_copy.grid[x][y + 1] = '^'
                            game_board_copy.grid[x + 1][y + 1] = 'v'
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, 0, next_state.depth + 1, next_state)
                                stack.append(new_state)
                    # move to the top for 2x1 (vertical)
                    if x != 0:
                        if board_grid[x - 1][y] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = 'v'
                            game_board_copy.grid[x - 1][y] = '^'
                            game_board_copy.grid[x + 1][y] = '.'
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, 0, next_state.depth + 1, next_state)
                                stack.append(new_state)
                    # move down the 2x1 (vertical)
                    if x < 3:
                        if board_grid[x + 2][y] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = '.'
                            game_board_copy.grid[x + 1][y] = '^'
                            game_board_copy.grid[x + 2][y] = 'v'
                            # form a new state and add it into the stack for future search
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, 0, next_state.depth + 1, next_state)
                                stack.append(new_state)
                # if the grid is a single 1x1
                elif board_grid[x][y] == char_single:
                    if x != 4:
                        if board_grid[x + 1][y] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = '.'
                            game_board_copy.grid[x + 1][y] = char_single
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, 0, next_state.depth + 1, next_state)
                                stack.append(new_state)
                    if x != 0:
                        if board_grid[x - 1][y] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = '.'
                            game_board_copy.grid[x - 1][y] = char_single
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, 0, next_state.depth + 1, next_state)
                                stack.append(new_state)
                    if y != 3:
                        if board_grid[x][y + 1] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = '.'
                            game_board_copy.grid[x][y + 1] = char_single
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, 0, next_state.depth + 1, next_state)
                                stack.append(new_state)
                    if y != 0:
                        if board_grid[x][y - 1] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = '.'
                            game_board_copy.grid[x][y - 1] = char_single
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, 0, next_state.depth + 1, next_state)
                                stack.append(new_state)
                elif board_grid[x][y] == '<':
                    # move the 1x2 to the left
                    if y != 0:
                        if board_grid[x][y - 1] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = '>'
                            game_board_copy.grid[x][y + 1] = '.'
                            game_board_copy.grid[x][y - 1] = '<'
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, 0, next_state.depth + 1, next_state)
                                stack.append(new_state)
                    if y < 2:
                        if board_grid[x][y + 2] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = '.'
                            game_board_copy.grid[x][y + 1] = '<'
                            game_board_copy.grid[x][y + 2] = '>'
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, 0, next_state.depth + 1, next_state)
                                stack.append(new_state)
                    if x != 0:
                        if board_grid[x - 1][y] == '.' and board_grid[x - 1][y + 1] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = '.'
                            game_board_copy.grid[x][y + 1] = '.'
                            game_board_copy.grid[x - 1][y] = '<'
                            game_board_copy.grid[x - 1][y + 1] = '>'
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, 0, next_state.depth + 1, next_state)
                                stack.append(new_state)
                    if x != 4:
                        if board_grid[x + 1][y] == '.' and board_grid[x + 1][y + 1] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = '.'
                            game_board_copy.grid[x][y + 1] = '.'
                            game_board_copy.grid[x + 1][y] = '<'
                            game_board_copy.grid[x + 1][y + 1] = '>'
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, 0, next_state.depth + 1, next_state)
                                stack.append(new_state)
                # The grid is the top left corner of the 2x2
                elif x < 4 and y < 3:
                    if board_grid[x][y] == char_goal \
                            and board_grid[x + 1][y] == char_goal \
                            and board_grid[x][y + 1] == char_goal:
                        # move to the left
                        if y != 0:
                            if board_grid[x][y - 1] == '.' and board_grid[x + 1][y - 1] == '.':
                                game_board_copy = deepcopy(game_board)
                                game_board_copy.grid[x][y - 1] = char_goal
                                game_board_copy.grid[x + 1][y - 1] = char_goal
                                game_board_copy.grid[x][y + 1] = '.'
                                game_board_copy.grid[x + 1][y + 1] = '.'
                                if str(game_board_copy.grid) not in board_visited_set:
                                    board_visited_set.add(str(game_board_copy.grid))
                                    new_state = State(game_board_copy, 0, next_state.depth + 1, next_state)
                                    stack.append(new_state)
                        # move to the right
                        if y < 2:
                            if board_grid[x][y + 2] == '.' and board_grid[x + 1][y + 2] == '.':
                                game_board_copy = deepcopy(game_board)
                                game_board_copy.grid[x][y] = '.'
                                game_board_copy.grid[x + 1][y] = '.'
                                game_board_copy.grid[x][y + 2] = char_goal
                                game_board_copy.grid[x + 1][y + 2] = char_goal
                                if str(game_board_copy.grid) not in board_visited_set:
                                    board_visited_set.add(str(game_board_copy.grid))
                                    new_state = State(game_board_copy, 0, next_state.depth + 1, next_state)
                                    stack.append(new_state)
                        # move to the top
                        if x != 0:
                            if board_grid[x - 1][y] == '.' and board_grid[x - 1][y + 1] == '.':
                                game_board_copy = deepcopy(game_board)
                                game_board_copy.grid[x - 1][y] = char_goal
                                game_board_copy.grid[x - 1][y + 1] = char_goal
                                game_board_copy.grid[x + 1][y] = '.'
                                game_board_copy.grid[x + 1][y + 1] = '.'
                                if str(game_board_copy.grid) not in board_visited_set:
                                    board_visited_set.add(str(game_board_copy.grid))
                                    new_state = State(game_board_copy, 0, next_state.depth + 1, next_state)
                                    stack.append(new_state)
                        # move down the grid
                        if x < 3:
                            if board_grid[x + 2][y] == '.' and board_grid[x + 2][y + 1] == '.':
                                game_board_copy = deepcopy(game_board)
                                game_board_copy.grid[x][y] = '.'
                                game_board_copy.grid[x][y + 1] = '.'
                                game_board_copy.grid[x + 2][y] = char_goal
                                game_board_copy.grid[x + 2][y + 1] = char_goal
                                if str(game_board_copy.grid) not in board_visited_set:
                                    board_visited_set.add(str(game_board_copy.grid))
                                    new_state = State(game_board_copy, 0, next_state.depth + 1, next_state)
                                    stack.append(new_state)


def dfs_backtrace(final_state, initial_state):
    path = []
    while final_state != initial_state:
        path.append(final_state.board)
        final_state = final_state.parent
    path.append(initial_state.board)
    path.reverse()
    print(len(path))
    for graph in path:
        graph.display()
        print('\n')


def astar(initial_state):
    # try to use Manhattan distance heuristic for our function check the distance from the top left corner of 2x2
    # tile to the goal state, which is grid[3][1] for that specific tile (need to ignore fewer rules,
    # consider different shapes of the tile, how to deal with different shapes) also, could add up all the Manhattan
    # distance for the total four tiles a list that contains all the visited board and if encounter the same
    # situation, discard the one has more depth

    # the frontier queue used by the dfs (stack)
    # first_state = State(game_board, 0, 0, None)
    # board_visited.append(first_state)
    stack = []
    initial_list = [initial_state.f + initial_state.depth, initial_state.id, initial_state]
    heappush(stack, initial_list)

    while len(stack):
        next_list = heappop(stack)

        next_state = next_list[2]
        if str(next_state.board.grid) not in board_visited_set:
            board_visited_set.add(str(next_state.board.grid))
        game_board = next_state.board
        board_grid = next_state.board.grid
        # find the coordinate of two white space of two white space
        if board_grid[3][1] == char_goal and board_grid[3][2] == char_goal \
                and board_grid[4][1] == char_goal and board_grid[4][2] == char_goal:
            return next_state

        for x in range(0, 5):
            for y in range(0, 4):
                if board_grid[x][y] == '^':
                    # move to the left for 2x1 (vertical)
                    if y != 0:
                        if board_grid[x][y - 1] == '.' and board_grid[x + 1][y - 1] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = '.'
                            game_board_copy.grid[x + 1][y] = '.'
                            game_board_copy.grid[x][y - 1] = '^'
                            game_board_copy.grid[x + 1][y - 1] = 'v'

                            # check duplicate
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, next_state.f, next_state.depth + 1, next_state)
                                next_list = [next_state.f + next_state.depth, new_state.id, new_state]
                                heappush(stack, next_list)
                    # move to the right for 2x1 (vertical)
                    if y != 3:
                        if board_grid[x][y + 1] == '.' and board_grid[x + 1][y + 1] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = '.'
                            game_board_copy.grid[x + 1][y] = '.'
                            game_board_copy.grid[x][y + 1] = '^'
                            game_board_copy.grid[x + 1][y + 1] = 'v'
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, next_state.f, next_state.depth + 1, next_state)
                                next_list = [next_state.f + next_state.depth, new_state.id, new_state]
                                heappush(stack, next_list)
                    # move to the top for 2x1 (vertical)
                    if x != 0:
                        if board_grid[x - 1][y] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = 'v'
                            game_board_copy.grid[x - 1][y] = '^'
                            game_board_copy.grid[x + 1][y] = '.'
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, next_state.f, next_state.depth + 1, next_state)
                                next_list = [next_state.f + next_state.depth, new_state.id, new_state]
                                heappush(stack, next_list)
                    # move down the 2x1 (vertical)
                    if x < 3:
                        if board_grid[x + 2][y] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = '.'
                            game_board_copy.grid[x + 1][y] = '^'
                            game_board_copy.grid[x + 2][y] = 'v'
                            # form a new state and add it into the stack for future search
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, next_state.f, next_state.depth + 1, next_state)
                                next_list = [next_state.f + next_state.depth, new_state.id, new_state]
                                heappush(stack, next_list)
                # if the grid is a single 1x1
                elif board_grid[x][y] == char_single:
                    if x != 4:
                        if board_grid[x + 1][y] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = '.'
                            game_board_copy.grid[x + 1][y] = char_single
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, next_state.f, next_state.depth + 1, next_state)
                                next_list = [next_state.f + next_state.depth, new_state.id, new_state]
                                heappush(stack, next_list)
                    if x != 0:
                        if board_grid[x - 1][y] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = '.'
                            game_board_copy.grid[x - 1][y] = char_single
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, next_state.f, next_state.depth + 1, next_state)
                                next_list = [next_state.f + next_state.depth, new_state.id, new_state]
                                heappush(stack, next_list)
                    if y != 3:
                        if board_grid[x][y + 1] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = '.'
                            game_board_copy.grid[x][y + 1] = char_single
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, next_state.f, next_state.depth + 1, next_state)
                                next_list = [next_state.f + next_state.depth, new_state.id, new_state]
                                heappush(stack, next_list)
                    if y != 0:
                        if board_grid[x][y - 1] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = '.'
                            game_board_copy.grid[x][y - 1] = char_single
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, next_state.f, next_state.depth + 1, next_state)
                                next_list = [next_state.f + next_state.depth, new_state.id, new_state]
                                heappush(stack, next_list)
                elif board_grid[x][y] == '<':
                    # move the 1x2 to the left
                    if y != 0:
                        if board_grid[x][y - 1] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = '>'
                            game_board_copy.grid[x][y + 1] = '.'
                            game_board_copy.grid[x][y - 1] = '<'
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, next_state.f, next_state.depth + 1, next_state)
                                next_list = [next_state.f + next_state.depth, new_state.id, new_state]
                                heappush(stack, next_list)
                    if y < 2:
                        if board_grid[x][y + 2] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = '.'
                            game_board_copy.grid[x][y + 1] = '<'
                            game_board_copy.grid[x][y + 2] = '>'
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, next_state.f, next_state.depth + 1, next_state)
                                next_list = [next_state.f + next_state.depth, new_state.id, new_state]
                                heappush(stack, next_list)
                    if x != 0:
                        if board_grid[x - 1][y] == '.' and board_grid[x - 1][y + 1] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = '.'
                            game_board_copy.grid[x][y + 1] = '.'
                            game_board_copy.grid[x - 1][y] = '<'
                            game_board_copy.grid[x - 1][y + 1] = '>'
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, next_state.f, next_state.depth + 1, next_state)
                                next_list = [next_state.f + next_state.depth, new_state.id, new_state]
                                heappush(stack, next_list)
                    if x != 4:
                        if board_grid[x + 1][y] == '.' and board_grid[x + 1][y + 1] == '.':
                            game_board_copy = deepcopy(game_board)
                            game_board_copy.grid[x][y] = '.'
                            game_board_copy.grid[x][y + 1] = '.'
                            game_board_copy.grid[x + 1][y] = '<'
                            game_board_copy.grid[x + 1][y + 1] = '>'
                            if str(game_board_copy.grid) not in board_visited_set:
                                board_visited_set.add(str(game_board_copy.grid))
                                new_state = State(game_board_copy, next_state.f, next_state.depth + 1, next_state)
                                next_list = [next_state.f + next_state.depth, new_state.id, new_state]
                                heappush(stack, next_list)
                # The grid is the top left corner of the 2x2
                elif x < 4 and y < 3:
                    if board_grid[x][y] == char_goal \
                            and board_grid[x + 1][y] == char_goal \
                            and board_grid[x][y + 1] == char_goal:
                        # move to the left
                        if y != 0:
                            if board_grid[x][y - 1] == '.' and board_grid[x + 1][y - 1] == '.':
                                game_board_copy = deepcopy(game_board)
                                game_board_copy.grid[x][y - 1] = char_goal
                                game_board_copy.grid[x + 1][y - 1] = char_goal
                                game_board_copy.grid[x][y + 1] = '.'
                                game_board_copy.grid[x + 1][y + 1] = '.'

                                if str(game_board_copy.grid) not in board_visited_set:
                                    distance = abs(x - 3) + abs(y - 2)
                                    if distance < next_state.f:
                                        next_state.f = next_state.f - 1
                                    if distance > next_state.f:
                                        next_state.f = next_state.f + 1
                                    board_visited_set.add(str(game_board_copy.grid))
                                    new_state = State(game_board_copy, next_state.f, next_state.depth + 1, next_state)
                                    next_list = [new_state.f + next_state.depth, new_state.id, new_state]
                                    heappush(stack, next_list)
                        # move to the right
                        if y < 2:
                            if board_grid[x][y + 2] == '.' and board_grid[x + 1][y + 2] == '.':
                                game_board_copy = deepcopy(game_board)
                                game_board_copy.grid[x][y] = '.'
                                game_board_copy.grid[x + 1][y] = '.'
                                game_board_copy.grid[x][y + 2] = char_goal
                                game_board_copy.grid[x + 1][y + 2] = char_goal
                                if str(game_board_copy.grid) not in board_visited_set:
                                    distance = abs(x - 3) + abs(y)
                                    if distance < next_state.f:
                                        next_state.f = next_state.f - 1
                                    if distance > next_state.f:
                                        next_state.f = next_state.f + 1
                                    board_visited_set.add(str(game_board_copy.grid))
                                    new_state = State(game_board_copy, next_state.f, next_state.depth + 1, next_state)
                                    next_list = [new_state.f + next_state.depth, new_state.id, new_state]
                                    heappush(stack, next_list)
                        # move to the top
                        if x != 0:
                            if board_grid[x - 1][y] == '.' and board_grid[x - 1][y + 1] == '.':
                                game_board_copy = deepcopy(game_board)
                                game_board_copy.grid[x - 1][y] = char_goal
                                game_board_copy.grid[x - 1][y + 1] = char_goal
                                game_board_copy.grid[x + 1][y] = '.'
                                game_board_copy.grid[x + 1][y + 1] = '.'
                                if str(game_board_copy.grid) not in board_visited_set:
                                    board_visited_set.add(str(game_board_copy.grid))
                                    new_state = State(game_board_copy, next_state.f + 1, next_state.depth + 1, next_state)
                                    next_list = [next_state.f + 1 + next_state.depth, new_state.id, new_state]
                                    heappush(stack, next_list)
                        # move down the grid
                        if x < 3:
                            if board_grid[x + 2][y] == '.' and board_grid[x + 2][y + 1] == '.':
                                game_board_copy = deepcopy(game_board)
                                game_board_copy.grid[x][y] = '.'
                                game_board_copy.grid[x][y + 1] = '.'
                                game_board_copy.grid[x + 2][y] = char_goal
                                game_board_copy.grid[x + 2][y + 1] = char_goal
                                if str(game_board_copy.grid) not in board_visited_set:
                                    board_visited_set.add(str(game_board_copy.grid))
                                    new_state = State(game_board_copy, next_state.f - 1, next_state.depth + 1, next_state)
                                    next_list = [next_state.f - 1 + next_state.depth, new_state.id, new_state]
                                    heappush(stack, next_list)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The input file that contains the puzzle."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )
    parser.add_argument(
        "--algo",
        type=str,
        required=True,
        choices=['astar', 'dfs'],
        help="The searching algorithm."
    )
    args = parser.parse_args()
    # read the board from the file
    # redirect stdout to output file
    board = read_from_file(args.inputfile)
    sys.stdout = open(args.outputfile, 'w')

    if args.algo == 'dfs':
        first_state = State(board, 0, 0, None)
        board_visited.append(first_state)
        last_state = dfs(first_state)
        dfs_backtrace(last_state, first_state)

    if args.algo == 'astar':
        f_value = 0
        for x1 in range(0, 5):
            for y1 in range(0, 4):
                if x1 != 4 and y1 != 3:
                    if board.grid[x1][y1] == char_goal and board.grid[x1 + 1][y1] == char_goal and board.grid[x1][y1 + 1] == char_goal:
                        x_coor = x1
                        y_coor = y1
                        f_value = abs(x_coor - 3) + abs(y_coor - 1)
                        break
        first_state = State(board, 0, f_value, None)
        last_state = astar(first_state)
        dfs_backtrace(last_state, first_state)
