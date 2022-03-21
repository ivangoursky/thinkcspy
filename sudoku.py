import copy
import random

bits2list_cache = []

def init_bits2list_cache():
    for i in range(512):
        tmp = []
        for j in range(9):
            if (i & (1 << j)) !=0:
                tmp.append(j+1)
        bits2list_cache.append(tuple(tmp))


def bits2list(n):
    return list(bits2list_cache[n])

def list2bits(vals):
    res = 0
    for i in vals:
        res = res | (1 << (i - 1))

    return res


def poss2list(poss):
    """ Covert a solution represented as a 9x9 matrix, elements of which are bit-encoded sets
     to the matrix of integers"""
    res = []
    for row in poss:
        tmp = []
        for cell in row:
            tmp.append(bits2list(cell)[0])
        res.append(tmp)

    return res


def make_possibilities_undo(poss, undo):
    """ Undo changes to the possibilities matrix poss, specified in the dictionary undo"""
    for (rc, restore) in undo.items():
        (r, c) = rc
        poss[r][c] = restore


def max_index(x):
    """ Find index of the maximal element in list"""
    best = x[0]
    best_idx = 0
    for i in range(len(x) - 1):
        if (x[i + 1] > best):
            best = x[i + 1]
            best_idx = i + 1

    return best_idx

def is_solved(poss):
    """ Given a matrix of possibilities (each element is a bit-encoded set, representing possible values for the cell),
    check if it is a solution (only one possibility for eac cell)"""
    for r in range(9):
        for c in range(9):
            if len(bits2list(poss[r][c]))>1:
                return False

    return True

def sudoku_state2str(state):
    """ Convert to the textual form the sudoku board, represented by 9x9 matrix of integers"""
    res = ""
    for r in range(9):
        for c in range(9):
            res = res + str(state[r][c])
        res = res + "\n"

    return res


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
        """ Clear sudoku board (this means, fill it with empty cells)"""
        self.state = []
        for i in range(9):
            self.state.append([0] * 9)

    def my_rng(self):
        """ Pseudo-random number generator, return current RNG state"""
        self.rnd_seed = (self.rnd_seed * 1103515245) % 2147483648
        return self.rnd_seed

    def my_rng_range(self, n):
        """ Pseudo-random number generator, returns value in range 0..(n-1)"""
        self.rnd_seed = (self.rnd_seed * 1103515245) % 2147483648
        return int((self.rnd_seed / 2147483648) * n)

    def my_shuffle(self, x):
        """ Shuffle the list"""
        l = len(x)
        for i in range(len(x) * 2):
            i1 = self.my_rng_range(l)
            i2 = self.my_rng_range(l)
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

    def given_cells_count(self):
        """ Count given cells on board, denoted by 1-9s """
        return 81 - self.empty_cells_count()

    def __str__(self):
        """ Represent the current board as text"""
        return sudoku_state2str(self.state)

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
                        return list(res)

        # check for conflicting values in the 3x3 square
        sq_row = row // 3
        sq_col = col // 3
        for r in range(sq_row * 3, sq_row * 3 + 3):
            for c in range(sq_col * 3, sq_col * 3 + 3):
                if not (r == row and c == col):
                    if self.state[r][c] != 0 and (self.state[r][c] in res):
                        res.remove(self.state[r][c])
                        if len(res) == 0:
                            return list(res)

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

    def remove_possibility(self, poss, row, col, cell_val_bit, undo):
        """Remove cell_val from the set of possible values of the cell at row and col,
        save data for undo in the undo dictionary.
        In case only 1 possibility is left, call update_possibilities for that cells.
        Return true if all updates were successful, and false if we met conflicts."""
        if undo.get((row, col)) is None:
            undo[(row, col)] = poss[row][col]  #just assign a value, we encode set as bits in integer

        poss[row][col] = poss[row][col] & (~cell_val_bit)
        l = len(bits2list(poss[row][col]))
        if l == 0:
            return False
        elif l == 1:
            return self.update_possibilities(poss, row, col, undo)

        return True

    def update_possibilities(self, poss, row, col, undo):
        """ Update sets of possible values, after setting the cell at row and col.
        Return true if all updates were successful, and false if we met conflicts."""
        cur_val_bit = poss[row][col]

        # check for conflicting values in the row
        for i in range(9):
            if i != col:
                if (poss[row][i] & cur_val_bit) != 0:
                    if not self.remove_possibility(poss, row, i, cur_val_bit, undo):
                        return False  # setting cell makes the solution impossible

        # check for conflicting values in the column
        for i in range(9):
            if i != row:
                if (poss[i][col] & cur_val_bit) != 0:
                    if not self.remove_possibility(poss, i, col, cur_val_bit, undo):
                        return False

        # check for conflicting values in the 3x3 square
        sq_row = row // 3
        sq_col = col // 3
        for r in range(sq_row * 3, sq_row * 3 + 3):
            for c in range(sq_col * 3, sq_col * 3 + 3):
                if not (r == row and c == col):
                    if (poss[r][c] & cur_val_bit) != 0:
                        if not self.remove_possibility(poss, r, c, cur_val_bit, undo):
                            return False

        return True

    def solve_board(self, shuffle_idx=True, shuffle_possibilities=True, nsolutions=1):
        """ Find solution(s) for the board"""

        def try_cell(n, poss):
            """ Resursively walk the empty cells and try different values """

            # look for the cell with minimum possibilities
            min_poss = 10
            min_poss_idx = -1
            for i in range(n, len(empty_idx)):
                r = empty_idx[i] // 9
                c = empty_idx[i] % 9
                l = len(bits2list(poss[r][c]))
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
            possibilities = bits2list(poss[r][c])

            if len(possibilities) == 1:
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
                poss[r][c] = 1 << (i-1)

                if not self.update_possibilities(poss, r, c, undo):
                    make_possibilities_undo(poss, undo)
                    continue

                if n < len(empty_idx) - 1:
                    # try substituting numbers to the next cell
                    try_cell(n + 1, poss)

                make_possibilities_undo(poss, undo)

                #exit, if we have found enough solutions
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
                    cell_poss = 1 << (self.state[r][c] - 1) #integer!
                    tmp.append(cell_poss)
                else:
                    cell_poss_list = set(self.cell_get_possibilities(r, c))
                    if len(cell_poss_list) == 0:
                        return res  # can't solve this board
                    cell_poss = list2bits(cell_poss_list)
                    tmp.append(cell_poss)

            possibilities.append(tmp)

        for r in range(9):
            for c in range(9):
                if len(bits2list(possibilities[r][c])) == 1:
                    dummy = {}
                    if not self.update_possibilities(possibilities, r, c, dummy):
                        return res

        if is_solved(possibilities):
            #return the solution, if the board has been successfully solved
            #using the above simple exclusion of possibilities
            res.append(poss2list(possibilities))
            return res

        #rebuild empty cells index
        empty_idx = []
        for r in range(9):
            for c in range(9):
                if len(bits2list(possibilities[r][c]))>1:
                    empty_idx.append(r * 9 + c)

        try_cell(0, possibilities)
        return res

    def clear_issolvable_cache(self):
        """Clear cache of number of solutions"""
        self.issolvable = {}

    def memo_nsolutions(self):
        """Calculate the number of solutions for the current board (up to 2).
        Uses self.issolvable dictionary to cache results"""
        k = tuple(tuple(row) for row in self.state)
        nsol = self.issolvable.get(k)
        if nsol is None:
            solutions = self.solve_board(False, False, 2)
            nsol = len(solutions)
            self.issolvable[k] = nsol
        else:
            return (nsol, True)

        return (nsol, False)

    def generate_board_recursive(self, ncells_leave=40, max_solve_calls=10000,
                                 fast_remove=0, full_search_thresh = 25):
        """
        Generate a board with one solution, by removing cells one by one from the current board.
        Current board should have no empty cells
        """
        solve_calls = 0
        res = None

        def remove_cell(n, cells_idx):
            """ Remove the cell at index n of the list """
            nonlocal res
            # make a local copy of cells_idx
            cells_idx = copy.deepcopy(cells_idx)
            #shuffle cells_idx for cells, not yet being tried to remove
            tmplist = cells_idx[(n + 1):]
            self.my_shuffle(tmplist)
            cells_idx[(n + 1):] = tmplist

            cache_hit = False
            if n>-1:
                # decode index
                r = cells_idx[n] // 9
                c = cells_idx[n] % 9

                old_value = self.state[r][c]
                self.state[r][c] = 0
                (nsol, cache_hit) = self.memo_nsolutions()
                nonlocal solve_calls
                if not cache_hit:
                    solve_calls += 1

                #if solve_calls > max_solve_calls:
                #    print("Reached maximum allowed calls to solve_board")

                if nsol == 1:
                    # board generated
                    if 80 - n == ncells_leave:
                        res = copy.deepcopy(self.state)
                        # cleanup
                        self.state[r][c] = old_value
                        return n
                else:
                    # cleanup
                    self.state[r][c] = old_value
                    # print("Reached cells: ",81-n)
                    return n - 1

                if solve_calls > max_solve_calls:
                    # cleanup
                    self.state[r][c] = old_value
                    return n

            # make few tries for the left cells
            recursion_depth = []
            ntries = 80 - n
            full_search = False

            #print("|" * (ntries - ncells_leave))

            if 80 - n <= full_search_thresh:
                full_search = True

            if full_search and cache_hit:
                # cleanup
                if n>-1:
                    self.state[r][c] = old_value
                return n  # don't try with the same board twice

            nsuccess = 0
            for i in range(ntries):
                tmp = cells_idx[n + 1]
                cells_idx[n + 1] = cells_idx[n + 1 + i]
                cells_idx[n + 1 + i] = tmp

                depth = remove_cell(n + 1, cells_idx)

                recursion_depth.append(depth)
                if solve_calls > max_solve_calls or res is not None:
                    # cleanup
                    if n>-1:
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
            if n>-1:
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

                remove_cell(fast_remove, cells_idx)
                self.state = bak
            else:
                remove_cell(-1, cells_idx)
        else:
            self.my_shuffle(cells_idx)
            remove_cell(-1, cells_idx)
        return res

    def generate_board_annealing(self, ncells_leave=40, max_rounds=10000, keep_solution = True):
        """
        Generate a board with one solution, by removing cells one by one from the current board.
        Current board could have empty cells
        """

        # backup copy of the current field
        src_board = copy.deepcopy(self.state)

        given_cells = set()
        empty_cells = set()
        for r in range(9):
            for c in range(9):
                if self.state[r][c]>0:
                    given_cells.add(r*9+c)
                # else:
                #     empty_cells.add(r*9+c)

        res = None

        if ncells_leave == len(given_cells):
            #nothing to remove
            res = src_board
            return res
        elif ncells_leave > len(given_cells):
            #couldn't complete the task
            return res

        for iter in range(max_rounds):
            #find cells, which we could remove
            could_remove = set()
            for cell in given_cells:
                r = cell // 9
                c = cell % 9
                old_value = self.state[r][c]
                self.state[r][c] = 0
                if len(self.solve_board(False, False, 2)) == 1:
                    could_remove.add(r * 9 + c)
                self.state[r][c] = old_value

            #shuffle list of removable cells
            could_remove_list = list(could_remove)
            if len(could_remove_list)>0:
                self.my_shuffle(could_remove_list)

            #remove the cells, until we reach the necessary amount of given cells,
            #or we can't remove cells anymore
            for cell in could_remove_list:
                r = cell // 9
                c = cell % 9
                old_value = self.state[r][c]
                self.state[r][c] = 0
                given_cells.remove(cell)
                empty_cells.add(cell)
                if len(self.solve_board(False, False, 2)) == 1:
                    #a board with required number of given cells successfully generated
                    if len(given_cells) == ncells_leave:
                        res = copy.deepcopy(self.state)
                        self.state = src_board
                        return res
                else:
                    #tried to remove this cell without success, cleanup
                    self.state[r][c] = old_value
                    given_cells.add(cell)
                    empty_cells.remove(cell)

            # we have remote the cells we could, no try to remove random cell,
            #and "open" random positions, until the board is solvable again
            board_bak_rmcell = copy.deepcopy(self.state)
            given_cells_bak = copy.deepcopy(given_cells)
            empty_cells_bak = copy.deepcopy(empty_cells)

            given_cells_list = list(given_cells)
            self.my_shuffle(given_cells_list)
            cell_to_remove = given_cells_list[0]
            r = cell_to_remove // 9
            c = cell_to_remove % 9
            self.state[r][c] = 0
            # remove the selected cell from the given cells set
            # but don't add to the free cells set yet, to avoid immediate return of that cell
            # while the next steps
            given_cells.remove(cell_to_remove)

            success = False
            empty_cells_list = list(empty_cells)
            self.my_shuffle(empty_cells_list)

            #if we can change the resulting solution, generate a new board,
            #but keep the values of given cells
            if not keep_solution:
                new_board = self.solve_board(True, True, 1)[0]

            for cell in empty_cells_list:
                r = cell // 9
                c = cell % 9
                if keep_solution:
                    self.state[r][c] = src_board[r][c]
                else:
                    if src_board[r][c]!=0:
                        self.state[r][c] = new_board[r][c]
                empty_cells.remove(cell)
                given_cells.add(cell)
                # check if the board is solvable now
                if len(self.solve_board(False, False, 2)) == 1:
                    success = True
                    break

            # now add the removed cell to the empty cells list
            empty_cells.add(cell_to_remove)

            # check if we successfully removed one cell, and added another one
            # if not, cleanup
            if not success:
                self.state = board_bak_rmcell
                given_cells = given_cells_bak
                empty_cells = empty_cells_bak

        self.state = src_board
        return res

init_bits2list_cache()