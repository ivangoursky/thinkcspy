from sudoku import *
import mytest

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

    ngiven = 25
    print("Trying to generate sudoku's with {0} given, using recursive algotithm".format(ngiven))
    for i in range(5):
        print("Iteration: ", i)
        sud.clear()
        sq1 = list(range(1, 10))
        sud.my_shuffle(sq1)
        sq2 = list(range(1, 10))
        sud.my_shuffle(sq2)
        sq3 = list(range(1, 10))
        sud.my_shuffle(sq3)

        sud.state = [
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
        solutions = sud.solve_board(True, True, 1)
        sud.state = copy.deepcopy(solutions[0])
        boards = sud.generate_board_recursive(ngiven, 1, 10000, 20, 30)
        for b in boards:
            print(b)
            tst_sud = Sudoku(b)
            print(sud.solve_board(False, False, 5))

    ngiven=21
    print("Trying to generate sudoku's with {0} given, using annealing".format(ngiven))
    for i in range(26):
        print("Iteration: ",i)
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
        solutions = sud.solve_board(True, True, 1)
        sud.state = copy.deepcopy(solutions[0])
        boards = sud.generate_board_annealing(ngiven, 1000)
        for b in boards:
            print(b)
            tst_sud = Sudoku(b)
            print(sud.solve_board(False, False, 5))