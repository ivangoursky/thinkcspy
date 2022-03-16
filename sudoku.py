import copy
import random
import mytest
import math


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
        self.rnd_seed = (self.rnd_seed*1103515245)%2147483648
        return self.rnd_seed


    def my_shuffle(self,x):
        l=len(x)
        for i in range(len(x)*2):
            i1=self.my_rng()%l
            i2=self.my_rng()%l
            tmp=x[i1]
            x[i1]=x[i2]
            x[i2]=tmp

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

        if len(res)==0:
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

    def remove_possibility(self, poss, row, col, cell_val):
        poss[row][col].remove(cell_val)
        if len(poss[row][col])==0:
            return False
        elif len(poss[row][col])==1:
            return self.update_possibilities(poss,row,col)

        return True


    def update_possibilities(self, poss, row, col):
        """ Update sets of possible values, after setting the cell at row and col """
        cur_val=list(poss[row][col])[0]

        # check for conflicting values in the row
        for i in range(9):
            if i != col:
                if cur_val in poss[row][i]:
                    if not self.remove_possibility(poss, row, i, cur_val):
                        return False #setting cell makes the solution impossible

        # check for conflicting values in the column
        for i in range(9):
            if i != row:
                if cur_val in poss[i][col]:
                    if not self.remove_possibility(poss, i, col, cur_val):
                        return False

        # check for conflicting values in the 3x3 square
        sq_row = row // 3
        sq_col = col // 3
        for r in range(sq_row * 3, sq_row * 3 + 3):
            for c in range(sq_col * 3, sq_col * 3 + 3):
                if not (r == row and c == col):
                    if cur_val in poss[r][c]:
                        if not self.remove_possibility(poss, r, c, cur_val):
                            return False

        return True

    def poss2list(self,poss):
        res=[]
        for row in poss:
            tmp=[]
            for cell in row:
                tmp.append(list(cell)[0])
            res.append(tmp)

        return res

    def solve_board(self, shuffle_idx=True, shuffle_possibilities=True, nsolutions=1):
        """ Find solution(s) for the board"""

        def try_cell(n,poss):
            """ Resursively walk the empty cells and try different values """

            # decode index
            r = empty_idx[n] // 9
            c = empty_idx[n] % 9

            # values to try for the cell
            possibilities = list(poss[r][c])
            if shuffle_possibilities:
                self.my_shuffle(possibilities)

            for i in possibilities:
                if len(possibilities)>1:
                    new_poss = copy.deepcopy(poss)
                    new_poss[r][c] = set()
                    new_poss[r][c].add(i)

                    if not self.update_possibilities(new_poss,r,c):
                        continue
                else:
                    new_poss=poss #!!!Assume we won't try to substitute other values

                if n < len(empty_idx) - 1:
                    # try substituting numbers to the next cell
                    try_cell(n + 1,new_poss)
                else:
                    # solution found
                    res.append(self.poss2list(new_poss))
                    # stop, if we have to found only the first solution
                    if len(res) >= nsolutions:
                        break

                # stop trying possibilities, if we need only one solution, and have found it deeper in the recursion
                if len(res) >= nsolutions:
                    break

            # cleanup cell
            self.state[r][c] = 0

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

        possibilities=[]
        for r in range(9):
            tmp=[]
            for c in range(9):
                if self.state[r][c]!=0:
                    cell_poss=set()
                    cell_poss.add(self.state[r][c])
                    tmp.append(cell_poss)
                else:
                    cell_poss=set(self.cell_get_possibilities(r,c))
                    if len(cell_poss)==0:
                        return res #can't solve this board
                    tmp.append(cell_poss)

            possibilities.append(tmp)

        for r in range(9):
            for c in range(9):
                if len(possibilities[r][c])==1:
                    if not self.update_possibilities(possibilities,r,c):
                        return res

        try_cell(0,copy.deepcopy(possibilities))

        return res

    def max_index(self,x):
        best=x[0]
        best_idx=0
        for i in range(len(x)-1):
            if (x[i+1]>best):
                best=x[i+1]
                best_idx=i+1

        return best_idx

    def clear_issolvable_cache(self):
       self.issolvable={}

    def memo_nsolutions(self):
       tmp = []
       for row in self.state:
           for cell in row:
               tmp.append(cell)
       k = tuple(tmp)
       nsol = self.issolvable.get(k)
       if (nsol==None):
           solutions = self.solve_board(False, False, 2)
           nsol=len(solutions)
           self.issolvable[k]=nsol
       else:
           return (nsol, True)

       return (nsol, False)

    def generate_board(self, ncells_leave=40, nboards=1, max_solve_calls=10000,fast_remove=0):
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
            (nsol,cache_hit)=self.memo_nsolutions()
            nonlocal solve_calls
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
                #print("Reached cells: ",81-n)
                return n-1

            if solve_calls > max_solve_calls:
                # cleanup
                self.state[r][c] = old_value
                return n

            # make few tries for the left cells
            recursion_depth=[]
            cells_to_remove = 80 - n - ncells_leave
            if 80-n<=25:
                if cache_hit:
                    return n #full search on this combination already done
                ntries=80-n
                full_search=True
            else:
                ntries=2
                full_search=False

            for i in range(ntries):
                if not full_search:
                    tmp = cells_idx[(n + 1):]
                    self.my_shuffle(tmp)
                    cells_idx[(n + 1):] = tmp
                else:
                    tmp=cells_idx[n+1]
                    cells_idx[n+1]=cells_idx[n+1+i]
                    cells_idx[n+1+i]=tmp

                depth = remove_cell(n + 1)
                recursion_depth.append(depth)
                if solve_calls > max_solve_calls or len(res) == nboards:
                    # cleanup
                    self.state[r][c] = old_value
                    return max(recursion_depth)

            # cleanup
            self.state[r][c] = old_value
            return max(recursion_depth)

        self.clear_issolvable_cache()
        cells_idx = list(range(81))
        if fast_remove>0 and fast_remove<=(81-ncells_leave):
            success = False
            for i in range(100):
                bak = copy.deepcopy(self.state)

                self.my_shuffle(cells_idx)
                for j in range(fast_remove):
                    r = cells_idx[j] // 9
                    c = cells_idx[j] % 9
                    self.state[r][c]=0

                solutions = self.solve_board(False, False, 2)
                solve_calls+=1
                self.state = bak

                if solve_calls>max_solve_calls:
                    return res

                if len(solutions)==1:
                    success = True
                    break

            if success:
                bak = copy.deepcopy(self.state)
                for j in range(fast_remove):
                    r = cells_idx[j] // 9
                    c = cells_idx[j] % 9
                    self.state[r][c]=0

                remove_cell(fast_remove)
                self.state = bak
            else:
                remove_cell(0)
        else:
            self.my_shuffle(cells_idx)
            remove_cell(0)
        return res


if __name__ == "__main__":
    test_board = [
        [2, 5, 7, 4, 8, 9, 3, 1, 6],
        [1, 9, 4, 6, 3, 2, 8, 5, 7],
        [3, 6, 8, 7, 5, 1, 4, 9, 2],
        [5, 7, 2, 9, 1, 8, 6, 3, 4],
        [8, 4, 3, 5, 2, 6, 1, 7, 9],
        [9, 1, 6, 3, 4, 7, 2, 8, 5],
        [4, 8, 5, 2, 9, 3, 7, 6, 1],
        [7, 3, 9, 1, 6, 4, 5, 2, 8],
        [6, 2, 1, 8, 7, 5, 9, 4, 3]
    ]

    sud = Sudoku(test_board)
    mytest.test(sud.board_has_no_conflicts())
    sud.state[2][8] = 7
    mytest.test(not sud.board_has_no_conflicts())

    # test_board = [
    #     [2, 5, 0, 0, 8, 9, 3, 1, 6],
    #     [1, 0, 0, 6, 0, 2, 0, 5, 7],
    #     [3, 0, 8, 7, 0, 1, 4, 0, 0],
    #     [5, 7, 2, 0, 1, 8, 6, 3, 0],
    #     [8, 0, 0, 5, 0, 0, 1, 0, 9],
    #     [9, 0, 6, 3, 4, 7, 2, 0, 5],
    #     [0, 8, 0, 2, 9, 3, 7, 6, 0],
    #     [0, 3, 0, 0, 6, 0, 5, 0, 0],
    #     [6, 2, 1, 0, 0, 5, 9, 4, 3]
    # ]
    field_hard = [
        [0, 0, 1, 0, 0, 0, 2, 0, 0],
        [0, 3, 0, 0, 0, 0, 0, 4, 0],
        [5, 0, 0, 0, 3, 0, 0, 0, 6],
        [0, 0, 0, 1, 0, 7, 0, 0, 0],
        [0, 4, 0, 0, 0, 0, 0, 8, 0],
        [0, 0, 0, 9, 0, 2, 0, 0, 0],
        [3, 0, 0, 0, 0, 0, 0, 0, 8],
        [0, 6, 0, 0, 5, 0, 0, 3, 0],
        [0, 0, 2, 0, 0, 0, 7, 0, 0],
    ]
    print("Solving field_hard")
    sud = Sudoku(field_hard)
    # sud.rng = random.Random(1234)
    solutions = sud.solve_board(False, False, 5)  # no randomization
    print(solutions)

    print("Solving field with more than 1 solution")
    test_board = [
        [2, 5, 0, 0, 8, 9, 3, 1, 6],
        [1, 0, 0, 6, 0, 2, 0, 5, 7],
        [3, 0, 8, 7, 0, 1, 4, 0, 0],
        [5, 7, 2, 0, 1, 8, 6, 3, 0],
        [8, 0, 0, 5, 0, 0, 1, 0, 9],
        [9, 0, 6, 3, 4, 7, 2, 0, 5],
        [0, 8, 0, 2, 9, 3, 7, 6, 0],
        [0, 0, 0, 0, 6, 0, 5, 0, 0],
        [6, 2, 1, 0, 0, 5, 9, 4, 3]
    ]
    sud = Sudoku(test_board)
    # sud.rng = random.Random(1234)
    solutions = sud.solve_board(False, False,
                                10)  # no randomization, and don't stop after the first solution (try to find up to 10)
    for s in solutions:
        print(s)

    print("try to generate new filled board from scratch")
    sud = Sudoku()
    sud.rnd_seed = 1234
    #sud.state[0]=list(range(1,10))
    #sud.my_shuffle(sud.state[0])
    solutions = sud.solve_board(False, True, 1)  # shuffle only possibilities, stop after the first solution
    print(solutions)

    print("Trying to generate sudoku's with 21 given")
    for i in range(50):
        print("Iteration: ",i)
        sud.clear()
        sud.state[0]=list(range(1,10))
        sud.my_shuffle(sud.state[0])
        solutions = sud.solve_board(True, True, 1)
        sud.state = copy.deepcopy(solutions[0])
        boards = sud.generate_board(21,1,100000,20);
        for b in boards:
            print(b)
            tst_sud = Sudoku(b)
            print(sud.solve_board(False, False, 5))