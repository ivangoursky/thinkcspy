import copy
import random


def poss2list(poss):
    res = []
    for row in poss:
        tmp = []
        for cell in row:
            tmp.append(list(cell)[0])
        res.append(tmp)

    return res


def make_possibilities_undo(poss, undo):
    for (rc, restore) in undo.items():
        (r, c) = rc
        poss[r][c] = restore


def max_index(x):
    best = x[0]
    best_idx = 0
    for i in range(len(x) - 1):
        if (x[i + 1] > best):
            best = x[i + 1]
            best_idx = i + 1

    return best_idx

def is_solved(poss):
    for r in range(9):
        for c in range(9):
            if len(poss[r][c])>1:
                return False

    return True


class Sudoku:
    """ Class for 9x9 Sudoku board manipulation (standard rules) """

    def __init__(self, init_state=None):
        """ Initialize Sudoku board """
        # By default fill the board with 0, which will denote empty cell
        if init_state == None:
            self.clear()
        else:
            # check for wrong values in the provided init_state, and raise an exception, if they are
            for row in init_state:
                for cell in row:
                    if not (cell in range(10)):
                        my_error = ValueError("{0} is not a valid Sudoku cell content!".format(cell))
                        raise my_error

            self.state = copy.deepcopy(init_state)

        # initialize RNG
        rng = random.Random()
        self.rnd_seed = rng.randrange(1000000000)

    def clear(self):
        self.state = []
        for i in range(9):
            self.state.append([0] * 9)

    def my_rng(self):
        self.rnd_seed = (self.rnd_seed * 1103515245) % 2147483648
        return self.rnd_seed

    def my_shuffle(self, x):
        l = len(x)
        for i in range(len(x) * 2):
            i1 = self.my_rng() % l
            i2 = self.my_rng() % l
            tmp = x[i1]
            x[i1] = x[i2]
            x[i2] = tmp

    def empty_cells_count(self):
        """ Count empty cells on board, denoted by 0s """
        cnt = 0
        for row in self.state:
            for cell in row:
                if cell == 0:
                    cnt += 1

        return cnt

    def cell_get_possibilities(self, row, col):
        """ Get the list of possible values for the cell """

        res = set(range(1, 10))
        # check for conflicting values in the row
        for i in range(9):
            if i != col:
                if self.state[row][i] != 0 and (self.state[row][i] in res):
                    res.remove(self.state[row][i])

        # check for conflicting values in the column
        for i in range(9):
            if i != row:
                if self.state[i][col] != 0 and (self.state[i][col] in res):
                    res.remove(self.state[i][col])

        if len(res) == 0:
            return res

        # check for conflicting values in the 3x3 square
        sq_row = row // 3
        sq_col = col // 3
        for r in range(sq_row * 3, sq_row * 3 + 3):
            for c in range(sq_col * 3, sq_col * 3 + 3):
                if not (r == row and c == col):
                    if self.state[r][c] != 0 and (self.state[r][c] in res):
                        res.remove(self.state[r][c])

        return list(res)

    def cell_has_no_conflicts(self, row, col):
        """ Check if the value in a given cell has no conflicts with the values of other cells """
        if self.state[row][col] == 0:
            return True

        # check for conflicting values in the row
        for i in range(9):
            if i != col:
                if self.state[row][i] == self.state[row][col]:
                    return False

        # check for conflicting values in the column
        for i in range(9):
            if i != row:
                if self.state[i][col] == self.state[row][col]:
                    return False

        # check for conflicting values in the 3x3 square
        sq_row = row // 3
        sq_col = col // 3
        for r in range(sq_row * 3, sq_row * 3 + 3):
            for c in range(sq_col * 3, sq_col * 3 + 3):
                if not (r == row and c == col):
                    if self.state[r][c] == self.state[row][col]:
                        return False

        return True

    def board_has_no_conflicts(self):
        """ Check if the whole board has no conflicts """
        for r in range(9):
            for c in range(9):
                if not self.cell_has_no_conflicts(r, c):
                    return False

        return True

    def remove_possibility(self, poss, row, col, cell_val, undo):
        if undo.get((row, col)) is None:
            undo[(row, col)] = set(poss[row][col])  # make a copy!

        poss[row][col].remove(cell_val)
        if len(poss[row][col]) == 0:
            return False
        elif len(poss[row][col]) == 1:
            return self.update_possibilities(poss, row, col, undo)

        return True

    def update_possibilities(self, poss, row, col, undo):
        """ Update sets of possible values, after setting the cell at row and col """
        cur_val = list(poss[row][col])[0]

        # check for conflicting values in the row
        for i in range(9):
            if i != col:
                if cur_val in poss[row][i]:
                    if not self.remove_possibility(poss, row, i, cur_val, undo):
                        return False  # setting cell makes the solution impossible

        # check for conflicting values in the column
        for i in range(9):
            if i != row:
                if cur_val in poss[i][col]:
                    if not self.remove_possibility(poss, i, col, cur_val, undo):
                        return False

        # check for conflicting values in the 3x3 square
        sq_row = row // 3
        sq_col = col // 3
        for r in range(sq_row * 3, sq_row * 3 + 3):
            for c in range(sq_col * 3, sq_col * 3 + 3):
                if not (r == row and c == col):
                    if cur_val in poss[r][c]:
                        if not self.remove_possibility(poss, r, c, cur_val, undo):
                            return False

        return True

    def solve_board(self, shuffle_idx=True, shuffle_possibilities=True, nsolutions=1, old_behaviour = False):
        """ Find solution(s) for the board"""

        def try_cell(n, poss):
            """ Resursively walk the empty cells and try different values """

            # look for the cell with minimum possibilities
            min_poss = 10
            min_poss_idx = -1
            for i in range(n, len(empty_idx)):
                r = empty_idx[i] // 9
                c = empty_idx[i] % 9
                l = len(poss[r][c])
                if l < min_poss:
                    min_poss = l
                    min_poss_idx = i

                if l <= 2:
                    break

            tmp = empty_idx[n]
            empty_idx[n] = empty_idx[min_poss_idx]
            empty_idx[min_poss_idx] = tmp

            # decode index
            r = empty_idx[n] // 9
            c = empty_idx[n] % 9

            # values to try for the cell
            possibilities = list(poss[r][c])

            if (not old_behaviour) and len(possibilities) == 1:
                #no need for excessive loops and calls, when we have only 1 possibility
                if n < len(empty_idx) - 1:
                    # try substituting numbers to the next cell
                    try_cell(n + 1, poss)
                else:
                    # solution found
                    res.append(poss2list(poss))
                return

            if shuffle_possibilities:
                self.my_shuffle(possibilities)

            for i in possibilities:
                undo = {}
                undo[(r, c)] = poss[r][c]
                poss[r][c] = set()
                poss[r][c].add(i)

                if not self.update_possibilities(poss, r, c, undo):
                    make_possibilities_undo(poss, undo)
                    continue

                if n < len(empty_idx) - 1:
                    # try substituting numbers to the next cell
                    try_cell(n + 1, poss)
                else:
                    # solution found
                    res.append(poss2list(poss))
                    # stop, if we have to found only the first solution
                    if len(res) >= nsolutions:
                        make_possibilities_undo(poss, undo)
                        break

                make_possibilities_undo(poss, undo)

                # stop trying possibilities, if we need only one solution, and have found it deeper in the recursion
                if len(res) >= nsolutions:
                    break

        # initialize the list of results
        res = []

        # can't solve the board, that already has conflicts
        if not self.board_has_no_conflicts():
            return res

        # find indices of the empty cells: idx=9*row+col
        empty_idx = []
        for r in range(9):
            for c in range(9):
                if self.state[r][c] == 0:
                    empty_idx.append(r * 9 + c)

        # return the current board, if it has no conflicts and empty cells
        if len(empty_idx) == 0:
            res.append(copy.deepcopy(self.state))
            return res

        # shuffle indices, if randomization is allowed
        if shuffle_idx:
            self.my_shuffle(empty_idx)

        possibilities = []
        for r in range(9):
            tmp = []
            for c in range(9):
                if self.state[r][c] != 0:
                    cell_poss = set()
                    cell_poss.add(self.state[r][c])
                    tmp.append(cell_poss)
                else:
                    cell_poss = set(self.cell_get_possibilities(r, c))
                    if len(cell_poss) == 0:
                        return res  # can't solve this board
                    tmp.append(cell_poss)

            possibilities.append(tmp)

        for r in range(9):
            for c in range(9):
                if len(possibilities[r][c]) == 1:
                    dummy = {}
                    if not self.update_possibilities(possibilities, r, c, dummy):
                        return res

        if is_solved(possibilities):
            #return the solution, if the board has been successfully solved
            #using the above simple exclusion of possibilities
            res.append(poss2list(possibilities))
            return res

        if not old_behaviour:
            #rebuild empty cells index, if we don't retain old behaviour needed to maintain sudoku numbering
            empty_idx = []
            for r in range(9):
                for c in range(9):
                    if len(possibilities[r][c])>1:
                        empty_idx.append(r * 9 + c)

        try_cell(0, possibilities)

        return res

    def clear_issolvable_cache(self):
        self.issolvable = {}

    def memo_nsolutions(self):
        tmp = []
        for row in self.state:
            for cell in row:
                tmp.append(cell)
        k = tuple(tmp)
        nsol = self.issolvable.get(k)
        if nsol is None:
            solutions = self.solve_board(False, False, 2)
            nsol = len(solutions)
            self.issolvable[k] = nsol
        else:
            return (nsol, True)

        return (nsol, False)

    def generate_board(self, ncells_leave=40, nboards=1, max_solve_calls=10000, fast_remove=0):
        """
        Generate a board with one solution, by removing cells one by one from the current board.
        Current board should have no empty cells
        """
        solve_calls = 0
        res = []

        def remove_cell(n):
            """ Remove the cell at index n of the list """
            # decode index
            r = cells_idx[n] // 9
            c = cells_idx[n] % 9

            old_value = self.state[r][c]
            self.state[r][c] = 0
            (nsol, cache_hit) = self.memo_nsolutions()
            nonlocal solve_calls
            if not cache_hit:
                solve_calls += 1

            if nsol == 1:
                # board generated
                if 80 - n == ncells_leave:
                    res.append(copy.deepcopy(self.state))
                    # cleanup
                    self.state[r][c] = old_value
                    return n
            else:
                # cleanup
                self.state[r][c] = old_value
                # print("Reached cells: ",81-n)
                return n - 1

            if solve_calls > max_solve_calls:
                # print("Reached maximum allowed calls to solve_board")
                # cleanup
                self.state[r][c] = old_value
                return n

            # make few tries for the left cells
            recursion_depth = []
            ntries = 80 - n
            full_search = False

            if 80 - n <= 25:
                full_search = True

            if full_search and cache_hit:
                # cleanup
                self.state[r][c] = old_value
                return n  # don't try with the same board twice

            if not full_search:
                tmplist = cells_idx[(n + 1):]
                self.my_shuffle(tmplist)
                cells_idx[(n + 1):] = tmplist

            nsuccess = 0
            for i in range(ntries):
                tmp = cells_idx[n + 1]
                cells_idx[n + 1] = cells_idx[n + 1 + i]
                cells_idx[n + 1 + i] = tmp

                depth = remove_cell(n + 1)

                recursion_depth.append(depth)
                if solve_calls > max_solve_calls or len(res) == nboards:
                    # cleanup
                    self.state[r][c] = old_value
                    return max(recursion_depth)

                if not full_search:
                    if depth > n:
                        # stop if we aren't doing full search, and successfully tried to clear
                        # threshold amount of cells
                        nsuccess += 1
                        if nsuccess == 3:
                            break

            # cleanup
            self.state[r][c] = old_value
            return max(recursion_depth)

        self.clear_issolvable_cache()
        cells_idx = list(range(81))
        if fast_remove > 0 and fast_remove <= (81 - ncells_leave):
            success = False
            for i in range(100):
                bak = copy.deepcopy(self.state)

                self.my_shuffle(cells_idx)
                for j in range(fast_remove):
                    r = cells_idx[j] // 9
                    c = cells_idx[j] % 9
                    self.state[r][c] = 0

                solutions = self.solve_board(False, False, 2)
                solve_calls += 1
                self.state = bak

                if solve_calls > max_solve_calls:
                    return res

                if len(solutions) == 1:
                    success = True
                    break

            if success:
                bak = copy.deepcopy(self.state)
                for j in range(fast_remove):
                    r = cells_idx[j] // 9
                    c = cells_idx[j] % 9
                    self.state[r][c] = 0

                remove_cell(fast_remove)
                self.state = bak
            else:
                remove_cell(0)
        else:
            self.my_shuffle(cells_idx)
            remove_cell(0)
        return res
