import random
import time

bits2list_cache = []
bits2list_cache_l = []
pointing_cache = []

def get_finger(n):
    sq = [[0 for col in range(3)] for row in range(3)]
    cnt = 0
    cnt_row = [0] * 3
    cnt_col = [0] * 3
    for cell in bits2list_cache[n]:
        r = (cell - 1) // 3
        c = (cell - 1) % 3
        sq[r][c] = 1
        cnt += 1
        cnt_row[r] += 1
        cnt_col[c] += 1

    if cnt in (2, 3):
        for r in range(3):
            if cnt_row[r] == cnt:
                return(1, r)
        for c in range(3):
            if cnt_col[c] == cnt:
                return(2, c)
    return (0, 0)

def init_caches():
    for i in range(512):
        tmp = []
        for j in range(9):
            if (i & (1 << j)) !=0:
                tmp.append(j+1)
        bits2list_cache.append(tuple(tmp))
        bits2list_cache_l.append(len(tmp))

    for i in range(512):
        pointing_cache.append(get_finger(i))


# def bits2list(n):
#     return list(bits2list_cache[n])

def list2bits(vals):
    res = 0
    for i in vals:
        res = res | (1 << (i - 1))

    return res


def poss2list(poss):
    """ Covert a solution represented as a 9x9 matrix, elements of which are bit-encoded sets
     to the matrix of integers"""
    res = []
    for r in range(9):
        tmp = []
        for c in range(9):
            tmp.append(bits2list_cache[poss[r * 9 + c]][0])

        res.append(tmp)

    return res


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
            if bits2list_cache_l[poss[r * 9 + c]]>1:
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

def copy_state(state):
    return [[state[row][col] for col in range(9)] for row in range(9)]

def nfish_check(poss):
    nleft = [9] * 9
    poss_cols = [0] * 9
    poss_rows = [0] * 9
    for r in range(9):
        for c in range(9):
            p = poss[r * 9 + c]
            if bits2list_cache_l[p] == 1:
                val = bits2list_cache[p][0]
                nleft[val - 1] -= 1
            else:
                for val in bits2list_cache[p]:
                    poss_rows[val - 1] = poss_rows[val - 1] | (1 << r)
                    poss_cols[val - 1] = poss_cols[val - 1] | (1 << c)

    for var in range(9):
        if bits2list_cache_l[poss_rows[var]] < nleft[var]:
            return False
        if bits2list_cache_l[poss_cols[var]] < nleft[var]:
            return False

    return True

def search_naked_pair_or_triplet(poss):
    res = []
    for i in range(9):
        l = bits2list_cache_l[poss[i]]
        if l == 2:
            found = [i]
            for j in range(i + 1, 9):
                if poss[j] == poss[i]:
                    found.append(j)
            if len(found) == 2:
                res.append(found)
            elif len(found) > 2:
                return None
        elif l == 3:
            found = [i]
            for j in range(i + 1, 9):
                if poss[j] == poss[i]:
                    found.append(j)
            if len(found) == 3:
                res.append(found)
            elif len(found) > 3:
                return None

    return res


def is_same_sq(np):
    if len(np) == 2:
        if (np[0] // 3) != (np[1] // 3):
            return False
    else:
        if ((np[0] // 3) != (np[1] // 3)) or ((np[0] // 3) != (np[2] // 3)):
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

            self.state = copy_state(init_state)

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

    def do_tricks(self, poss):
        # check, if we have only one cell, were value is possible in a row, column, or 3x3 square
        # check for "one in row"
        while True:
            update_list = []
            for row in range(9):
                value_positions = [0] * 9
                vals = [0] * 9
                for i in range(9):
                    p = poss[row * 9 + i]
                    vals[i] = p
                    cell_poss = bits2list_cache[p]
                    for val in cell_poss:
                        value_positions[val - 1] = value_positions[val - 1] | (1 << i)

                for val in range(9):
                    curval_pos = bits2list_cache[value_positions[val]]
                    if len(curval_pos) == 1:
                        cur = curval_pos[0] - 1
                        if bits2list_cache_l[poss[row * 9 + cur]] != 1:
                            poss[row * 9 + cur] = 1 << val
                            update_list.append((row, cur))
                    elif len(curval_pos) == 0:
                        return False

                npt = search_naked_pair_or_triplet(vals)
                if npt is None:
                    return False

                for np in npt:
                    np_mask = ~vals[np[0]]
                    for i in range(9):
                        if not (i in np):
                            poss[row * 9 + i] = poss[row * 9 + i] & np_mask

                    if is_same_sq(np):
                        sq_row = row // 3
                        sq_col = np[0] // 3
                        for r in range(sq_row * 3, sq_row * 3 + 3):
                            for c in range(sq_col *3, sq_col *3 + 3):
                                if r != row:
                                    poss[r * 9 + c] = poss[r * 9 + c] & np_mask

            # check for "one in column"
            for col in range(9):
                value_positions = [0] * 9
                vals = [0] * 9
                for i in range(9):
                    p = poss[i * 9 + col]
                    vals[i] = p
                    cell_poss = bits2list_cache[p]
                    for val in cell_poss:
                        value_positions[val - 1] = value_positions[val - 1] | (1 << i)

                for val in range(9):
                    curval_pos = bits2list_cache[value_positions[val]]
                    if len(curval_pos) == 1:
                        cur = curval_pos[0] - 1
                        if bits2list_cache_l[poss[cur * 9 + col]] != 1:
                            poss[cur * 9 + col] = 1 << val
                            update_list.append((cur, col))
                    elif len(curval_pos) == 0:
                        return False

                npt = search_naked_pair_or_triplet(vals)
                if npt is None:
                    return False

                for np in npt:
                    np_mask = ~vals[np[0]]
                    for i in range(9):
                        if not (i in np):
                            poss[i * 9 + col] = poss[i * 9 + col] & np_mask

                    if is_same_sq(np):
                        sq_row = np[0] // 3
                        sq_col = col // 3
                        for r in range(sq_row * 3, sq_row * 3 + 3):
                            for c in range(sq_col *3, sq_col *3 + 3):
                                if c != col:
                                    poss[r * 9 + c] = poss[r * 9 + c] & np_mask

            # check for one in 3x3 square
            for sq_row in range(3):
                for sq_col in range(3):
                    value_positions = [0] * 9
                    vals = [0] * 9
                    for r in range(3):
                        for c in range(3):
                            p = poss[(sq_row * 3 + r) * 9 + (sq_col * 3 + c)]
                            vals[r * 3 + c] = p
                            cell_poss = bits2list_cache[p]
                            for val in cell_poss:
                                value_positions[val - 1] = value_positions[val - 1] | (1 << (r * 3 + c))

                    for val in range(9):
                        curval_pos = bits2list_cache[value_positions[val]]
                        if len(curval_pos) == 1:
                            cur = curval_pos[0] - 1
                            r = sq_row * 3 + cur // 3
                            c = sq_col * 3 + cur % 3
                            if bits2list_cache_l[poss[r * 9 + c]] != 1:
                                poss[r * 9 + c] = 1 << val
                                update_list.append((r, c))
                        elif len(curval_pos) == 0:
                            return False

                        finger = pointing_cache[value_positions[val]]
                        if finger[0] > 0:
                            val_bit = 1 << val
                            val_mask = ~val_bit
                            if finger[0] == 1:
                                r = sq_row * 3 + finger[1]
                                for c in range(9):
                                    if c // 3 != sq_col:
                                        idx = r * 9 + c
                                        if (poss[idx] & val_bit) != 0:
                                            poss[idx] = poss[idx] & val_mask
                                            l = bits2list_cache_l[poss[idx]]
                                            if l == 0:
                                                return False
                                            elif l == 1:
                                                update_list.append((r, c))
                            elif finger[0] == 2:
                                c = sq_col * 3 + finger[1]
                                for r in range(9):
                                    if r // 3 != sq_row:
                                        idx = r * 9 + c
                                        if (poss[idx] & val_bit) != 0:
                                            poss[idx] = poss[idx] & val_mask
                                            l = bits2list_cache_l[poss[idx]]
                                            if l == 0:
                                                return False
                                            elif l == 1:
                                                update_list.append((r, c))

                    npt = search_naked_pair_or_triplet(vals)
                    if npt is None:
                        return False

                    for np in npt:
                        np_mask = ~vals[np[0]]
                        for i in range(9):
                            if not (i in np):
                                r = sq_row * 3 + i // 3
                                c = sq_col * 3 + i % 3
                                poss[r * 9 + c] = poss[r * 9 + c] & np_mask

            if len(update_list) == 0:
                return True

            for (r,c) in update_list:
                if not self.update_possibilities(poss, r, c, False):
                    return False

        if not nfish_check(poss):
            return False

        return True


    def update_possibilities(self, poss, row, col, tricks):
        """ Update sets of possible values, after setting the cell at row and col.
        Return true if all updates were successful, and false if we met conflicts."""
        cur_val_bit = poss[row * 9 + col]
        cur_val_mask = ~cur_val_bit

        update_list = []

        # check for conflicting values in the row
        for i in range(9):
            if i != col:
                idx = row * 9 + i
                if (poss[idx] & cur_val_bit) != 0:
                    poss[idx] = poss[idx] & cur_val_mask
                    l = bits2list_cache_l[poss[idx]]
                    if l == 0:
                        return False
                    elif l == 1:
                        update_list.append((row, i))

        # check for conflicting values in the column
        for i in range(9):
            if i != row:
                idx = i * 9 + col
                if (poss[idx] & cur_val_bit) != 0:
                    poss[idx] = poss[idx] & cur_val_mask
                    l = bits2list_cache_l[poss[idx]]
                    if l == 0:
                        return False
                    elif l == 1:
                        update_list.append((i, col))

        # check for conflicting values in the 3x3 square
        sq_row = row // 3
        sq_col = col // 3
        for r in range(sq_row * 3, sq_row * 3 + 3):
            for c in range(sq_col * 3, sq_col * 3 + 3):
                if not (r == row and c == col):
                    idx = r * 9 + c
                    if (poss[idx] & cur_val_bit) != 0:
                        poss[idx] = poss[idx] & cur_val_mask
                        l = bits2list_cache_l[poss[idx]]
                        if l == 0:
                            return False
                        elif l == 1:
                            update_list.append((r, c))

        #update conflicts for recently found cells with 1 possibility
        #print(len(update_list))
        for (r,c) in update_list:
            if not self.update_possibilities(poss, r, c, False):
                return False

        if tricks:
            if not self.do_tricks(poss):
                return False

        return True


    def try_simple_solution(self,tricks = True):
        possibilities = [511] * 81
        for r in range(9):
            for c in range(9):
                if self.state[r][c] != 0:
                    possibilities[r * 9 + c] = 1 << (self.state[r][c] - 1)  # integer!

        for r in range(9):
            for c in range(9):
                if bits2list_cache_l[possibilities[r * 9 + c]] == 1:
                    if not self.update_possibilities(possibilities, r, c, False):
                        return None

        if tricks:
            if not self.do_tricks(possibilities):
                return None

        return possibilities

    def solve_board(self, shuffle_idx=True, shuffle_possibilities=True, nsolutions=1, tricks=True):
        """ Find solution(s) for the board"""

        def try_cell(n, poss):
            """ Resursively walk the empty cells and try different values """

            #skip cells with 1 possibility
            for i in range(n, len(empty_idx)):
                r = empty_idx[i] // 9
                c = empty_idx[i] % 9
                l = bits2list_cache_l[poss[r * 9 + c]]
                if l == 1:
                    tmp = empty_idx[n]
                    empty_idx[n] = empty_idx[i]
                    empty_idx[i] = tmp
                    n += 1

            if n == len(empty_idx):
                n = len(empty_idx) - 1

            # look for the cell with minimum possibilities
            min_poss = 10
            min_poss_idx = -1
            for i in range(n, len(empty_idx)):
                r = empty_idx[i] // 9
                c = empty_idx[i] % 9
                l = bits2list_cache_l[poss[r * 9 + c]]
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
            possibilities = bits2list_cache[poss[r * 9 + c]]

            if len(possibilities) == 1:
                #before we skiped all cells with 1 possibility, if only it isn't the last cell
                res.append(poss2list(poss))
                return

            if shuffle_possibilities:
                possibilities = list(possibilities)
                self.my_shuffle(possibilities)

            for i in possibilities:
                poss_bak = list(poss)
                poss[r * 9 + c] = 1 << (i-1)

                if not self.update_possibilities(poss, r, c, tricks):
                    poss = poss_bak
                    continue

                if n < len(empty_idx) - 1:
                    # try substituting numbers to the next cell
                    try_cell(n + 1, poss)

                poss = poss_bak

                #exit, if we have found enough solutions
                if len(res) >= nsolutions:
                    break

        #t0 = time.time()
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
            res.append(copy_state(self.state))
            return res

        possibilities = self.try_simple_solution(tricks)
        #t1 = time.time()

        if possibilities is None:
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
                if bits2list_cache_l[possibilities[r * 9 + c]]>1:
                    empty_idx.append(r * 9 + c)

        # shuffle indices, if randomization is allowed
        if shuffle_idx:
            self.my_shuffle(empty_idx)

        try_cell(0, possibilities)
        #t2 = time.time()
        #print("Time to complete try_simple_solution {0}, to complete all {1}.".format(t1-t0,t2-t0))
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
            cells_idx = list(cells_idx)
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
                        res = copy_state(self.state)
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
                bak = copy_state(self.state)

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
                bak = copy_state(self.state)
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

    def find_key_cells(self, randomize = False):
        """ Find cells which we couldn't solve using simple exclusion, and only one in... rule"""
        poss = self.try_simple_solution()
        cells_by_nposs = [[] for i in range(9)]
        for r in range(9):
            for c in range(9):
                l = bits2list_cache_l[poss[r * 9 + c]]
                if l > 1:
                    cells_by_nposs[l-1].append(r * 9 + c)

        res = []
        for i in range(8):
            if len(cells_by_nposs[8-i]) > 0:
                tmp = list(cells_by_nposs[8-i])
                if randomize:
                    self.my_shuffle(tmp)

                for j in tmp:
                    res.append(j)

        return res

    def generate_board_annealing(self, ncells_leave=40, max_rounds=10000, keep_solution=True):
        """
        Generate a board with one solution, by removing cells one by one from the current board.
        Current board could have empty cells
        """

        # backup copy of the current field
        src_board = copy_state(self.state)

        given_cells = set()
        empty_cells = set()
        for r in range(9):
            for c in range(9):
                if self.state[r][c]>0:
                    given_cells.add(r*9+c)

        res = None

        if ncells_leave == len(given_cells):
            #nothing to remove
            res = src_board
            return res
        elif ncells_leave > len(given_cells):
            #couldn't complete the task
            return res

        for iter in range(max_rounds):
            #print("|" * (len(given_cells) - ncells_leave))
            #find cells, which we could remove
            given_cells_list = list(given_cells)
            self.my_shuffle(given_cells_list)

            #try to remove the cells, until we reach the necessary amount of given cells,
            #or we can't remove cells anymore
            for cell in given_cells_list:
                r = cell // 9
                c = cell % 9
                old_value = self.state[r][c]
                self.state[r][c] = 0
                given_cells.remove(cell)
                empty_cells.add(cell)
                if len(self.solve_board(True, False, 2)) == 1:
                    #a board with required number of given cells successfully generated
                    if len(given_cells) == ncells_leave:
                        res = copy_state(self.state)
                        self.state = src_board
                        return res
                else:
                    #tried to remove this cell without success, cleanup
                    self.state[r][c] = old_value
                    given_cells.add(cell)
                    empty_cells.remove(cell)

            # we have remote the cells we could, no try to remove random cell,
            #and "open" random positions, until the board is solvable again
            board_bak_rmcell = copy_state(self.state)
            given_cells_bak = set(list(given_cells))
            empty_cells_bak = set(list(empty_cells))

            given_cells_list = list(given_cells)
            self.my_shuffle(given_cells_list)
            cell_to_remove = given_cells_list[0]
            r = cell_to_remove // 9
            c = cell_to_remove % 9
            self.state[r][c] = 0

            success = False

            #if we can change the resulting solution, generate a new board,
            #but keep the values of given cells
            if not keep_solution:
                new_solutions = self.solve_board(True, True, 1)
                new_board = new_solutions[0]
                self.state[r][c] = new_board[r][c]
                if len(self.solve_board(True, False, 2)) == 1:
                    continue
            else:
                # remove the selected cell from the given cells set
                # but don't add to the free cells set yet, to avoid immediate return of that cell
                # while the next steps
                given_cells.remove(cell_to_remove)

            #try open some cells, until the board is solvable again
            empty_cells_list = list(empty_cells)

            for cell in empty_cells_list:
                key_cells = self.find_key_cells(True)
                for i in key_cells:
                    if i in empty_cells: #could be False, if some cells were empty in the initial state
                        add_cell = i
                        break

                r = add_cell // 9
                c = add_cell % 9
                if keep_solution:
                    self.state[r][c] = src_board[r][c]
                else:
                    if src_board[r][c]!=0:
                        self.state[r][c] = new_board[r][c]
                empty_cells.remove(add_cell)
                given_cells.add(add_cell)
                # check if the board is solvable now
                if len(self.solve_board(True, False, 2)) == 1:
                    success = True
                    break

            if keep_solution:
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

    def generate_from_bottom(self, maxgiven=25):
        board_bak = copy_state(self.state)
        self.clear()
        gc = set()
        ec = set(range(81))
        res = None

        def generate(given_cells, empty_cells):
            if len(given_cells) >= maxgiven:
                return False

            new_solutions = self.solve_board(True, False, 1)
            new_board = new_solutions[0]
            key_cells = self.find_key_cells(True)
            rnd_iter = 1 + self.my_rng_range(3)
            for i in range(min(rnd_iter, len(key_cells))):
                add_cell = key_cells[i]
                r = add_cell // 9
                c = add_cell % 9

                self.state[r][c] = new_board[r][c]
                empty_cells.remove(add_cell)
                given_cells.add(add_cell)

                l = len(self.solve_board(False, False, 2))
                if l == 1:
                    nonlocal res
                    res = copy_state(self.state)
                    return True
                elif l == 0:
                    self.state[r][c] = 0
                    empty_cells.add(add_cell)
                    given_cells.remove(add_cell)
                    continue
                else:
                    if generate(set(given_cells), set(empty_cells)):
                        return True

                self.state[r][c] = 0
                empty_cells.add(add_cell)
                given_cells.remove(add_cell)

            return False

        generate(gc, ec)
        self.state = board_bak
        return res


init_caches()