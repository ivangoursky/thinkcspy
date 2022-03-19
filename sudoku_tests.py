import copy

from sudoku import *
from data.test_data import *
import mytest

def generate_random_filled_board(sud, nboards):
    state_bak = copy.deepcopy(sud.state)
    sud.clear()
    sq1=list(range(1,10))
    sud.my_shuffle(sq1)
    sq2 = list(range(1, 10))
    sud.my_shuffle(sq2)
    sq3 = list(range(1, 10))
    sud.my_shuffle(sq3)

    sud.state=[
        [sq1[0], sq1[1], sq1[2], 0, 0, 0, 0, 0, 0],
        [sq1[3], sq1[4], sq1[5], 0, 0, 0, 0, 0, 0],
        [sq1[6], sq1[7], sq1[8], 0, 0, 0, 0, 0, 0],
        [0, 0, 0, sq2[0], sq2[1], sq2[2], 0, 0, 0],
        [0, 0, 0, sq2[3], sq2[4], sq2[5], 0, 0, 0],
        [0, 0, 0, sq2[6], sq2[7], sq2[8], 0, 0, 0],
        [0, 0, 0, 0, 0, 0, sq3[0], sq3[1], sq3[2]],
        [0, 0, 0, 0, 0, 0, sq3[3], sq3[4], sq3[5]],
        [0, 0, 0, 0, 0, 0, sq3[6], sq3[7], sq3[8]],
    ]
    solutions = sud.solve_board(True, True, nboards)
    sud.state = state_bak
    return solutions

def test_board(b, nsol = 1, ngiven = None):
    if b is None:
        print("The board is None")
        return

    print(sudoku_state2str(b))
    tst_sud = Sudoku(b)
    if ngiven is not None:
        given_cnt = tst_sud.given_cells_count()
        if given_cnt != ngiven:
            print("Test FAILED: this sudoku has {0} given cells, should be {1}".format(given_cnt, ngiven))
        else:
            print("Test PASSED: this sudoku has exactly {0} given cells".format(ngiven))

    solutions = tst_sud.solve_board(False, False, 5)
    if len(solutions) != nsol:
        print("Test FAILED: this sudoku has {0} solutions, should be {1}".format(len(solutions), nsol))
    else:
        print("Test PASSED: this sudoku has exactly {0} solution(s)".format(nsol))

    for s in solutions:
        print(sudoku_state2str(s))

if __name__ == "__main__":

    sud = Sudoku(board_1solution)
    mytest.test(sud.board_has_no_conflicts())
    sud.state[2][8] = 7
    mytest.test(not sud.board_has_no_conflicts())


    print("Solving field_hard")
    test_board(field_hard)

    print("Solving field with more than 1 solution")
    test_board(board_2solutions, 2)

    print("try to generate new filled board from scratch")
    sud = Sudoku()
    sud.rnd_seed = 1234
    solutions = generate_random_filled_board(sud, 1)
    for s in solutions:
        print(sudoku_state2str(s))

    ngiven = 25
    print("Trying to generate sudoku's with {0} given, using recursive algorithm".format(ngiven))
    for i in range(5):
        print("Iteration: ", i)
        solutions = generate_random_filled_board(sud, 1)
        sud.state = copy.deepcopy(solutions[0])
        board = sud.generate_board_recursive(ngiven, 10000, 20, 30)
        test_board(board,1,ngiven)

    ngiven=21
    print("Trying to generate sudoku's with {0} given, using annealing, with empty central 3x3 square".format(ngiven))
    for i in range(3):
        print("Iteration: ",i)
        solutions = generate_random_filled_board(sud, 1)
        sud.state = copy.deepcopy(solutions[0])
        for r in range(3,6):
            for c in range(3,6):
                sud.state[r][c] = 0
        board = sud.generate_board_annealing(ngiven, 1000)
        test_board(board,1,ngiven)

    ngiven = 20
    print("Trying to generate sudoku's with {0} given, using annealing".format(ngiven))
    for i in range(20):
        print("Iteration: ", i)
        solutions = generate_random_filled_board(sud, 1)
        sud.state = copy.deepcopy(solutions[0])
        board = sud.generate_board_annealing(ngiven, 1000)
        test_board(board,1,ngiven)