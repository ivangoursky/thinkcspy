import pygame
import sudoku
import time
import random
from tkinter import messagebox

def generate_one_field(ngiven=23, randseed = None):
    """Generate a field with number of given cells ngiven.
    Field is represented as 9x9 matrix of integers (as Sudoku.state).
    Optionally randseed could be set, to achive reproducible fields."""
    sud=sudoku.Sudoku()
    if randseed is not None:
        sud.rnd_seed = randseed
    for i in range(3):
        sud.clear()
        #fill 3 3x3 squares with random permutations of 1..9
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
        #find first solution for this field, using randomization in solve_board
        solutions = sud.solve_board(True, True, 1)
        sud.state = sudoku.copy_state(solutions[0])

        #try to remove some cells and leave ngiven cells, using simulated annealing-like method
        board = sud.generate_board_annealing(ngiven, 500, False)

        #return the generated field, or None if generation wasn't successful
        return board

    return None


def draw_square(surf,ulx,uly,col,sz,lwd):
    pygame.draw.polygon(surf, col, (
        (ulx, uly),
        (ulx + sz, uly),
        (ulx + sz, uly + sz),
        (ulx, uly + sz)), lwd)

def draw_possibilities(surf,cx,cy,poss,fnt):
    """Draw possible values (represented by set poss) for the cell at (cx,cy),
    using for fnt"""
    margin = 5
    txt_x = cx + margin
    txt_y = cy + margin
    cnt = 0
    for p in poss:
        txt_blit = fnt.render(str(p), True, (64,64,128))
        surf.blit(txt_blit, (txt_x, txt_y))
        (txt_w, txt_h) = txt_blit.get_size()
        txt_x += int(txt_w*1.5)
        cnt += 1
        if cnt == 3:
            cnt = 0
            txt_x = cx + margin
            txt_y += txt_h


def display_help():
    messagebox.showinfo(
        title = "How to play this game",
        message="""Mouse and keyboard shortcuts:
        Mouse click - select cell
        ESC - cancel selection
        a - solve the field
        c - reset field
        h - display this help
        n - create new field
        p - toggle "display possibilities" mode
        r - specify random number generator seed
        0 - clear selected cell
        1,2,3,4,5,6,7,8,9 - put corresponding value to the selected cell
        """
    )


class SudokuField:
    def __init__(self, field_sz, sq_sz):
        self.field_sz = field_sz
        self.sq_sz = sq_sz
        self.selection = None
        self.pos = None
        self.randseed = None
        self.cell_px = None
        self.field_px = None
        self.sudoku_number=""
        self.display_possibilities = False

    def generate(self,ngiven=25):
        """ Try to generate sudoku with ngiven given cells.
        If self.randseed is set, use it to set RNG for reproducible result"""
        if self.randseed is not None:
            randseed = self.randseed
        else:
            rng = random.Random()
            randseed = rng.randrange(1000000000)

        #encode sudoku number as "RNG_seed/ngiven"
        sud_num = str(randseed)+"/"+str(ngiven)

        field = generate_one_field(ngiven, randseed)
        if field is not None:
            self.sudoku = sudoku.Sudoku(field)
            self.src_field = sudoku.copy_state(self.sudoku.state)
            self.sudoku_number=sud_num
        else:
            messagebox.showinfo(title = "Warning",message="Could not generate sudoku, try one more time")

        if self.sudoku is None:
            self.sudoku = sudoku.Sudoku()

    def process_event(self, ev):
        """ Process keyboard and mouse events, passed to the instance of SudokuField"""
        if ev.type==pygame.KEYDOWN:
            key = ev.key

            if key==pygame.K_ESCAPE:
                self.selection = None

            ch = pygame.key.name(key)

            if ch == "c":
                self.sudoku.state = sudoku.copy_state(self.src_field)

            if "0123456789".__contains__(ch):
                if self.selection is not None:
                    v = int(ch)
                    (r,c) = self.selection
                    self.sudoku.state[r][c]=v
                    self.selection = None

            if ch == "a":
                solutions = self.sudoku.solve_board(False, False, 2)
                if len(solutions)>=1:
                    self.sudoku.state = solutions[0]

                if len(solutions)>1:
                    messagebox.showinfo(title="Warning", message="More than one solution found!")

                if len(solutions)==0:
                    messagebox.showinfo(title="Warning", message="No solutions found!")

            if ch == "h":
                display_help()

            if ch == "p":
                self.display_possibilities = not self.display_possibilities

        if ev.type == pygame.MOUSEBUTTONDOWN:
            (cx,cy) = ev.dict["pos"]

            (ulx,uly) = self.pos
            r=(cy-uly)//self.cell_px
            c = (cx - ulx) // self.cell_px
            if r>=0 and r<self.field_sz and c>=0 and c<self.field_sz:
                if self.src_field[r][c]==0:
                    self.selection = (r,c)

    def draw(self, surf, pos, small_sq_px):
        """ Draw sudoku field: the grid, values of given cells, values of cells inputted by user,
        optionally - possibilities for each cell.
        Draw field at (x,y)=pos, using the size of small square small_sq_px"""
        my_font = pygame.font.SysFont("Arial", 72, False)
        my_font_bold = pygame.font.SysFont("Arial", 72, True)
        my_font_poss = pygame.font.SysFont("Arial", 20, False)

        margin = 5
        (ulx, uly) = pos
        self.pos = pos

        self.cell_px = small_sq_px
        big_sq_px = small_sq_px * self.sq_sz
        field_px = small_sq_px * self.field_sz
        self.field_px = field_px

        #set selr, selc to the selected row and column, if we have a selection,
        #or to -1, if we have no selection
        if self.selection is not None:
            (selr, selc) = self.selection
        else:
            selr = -1
            selc = -1

        #draw a border around the field
        draw_square(surf, ulx - 1, uly - 1, (64, 64, 64), field_px + 1, 1)
        draw_square(surf, ulx - 2, uly - 2, (128, 128, 128), field_px + 3, 1)
        draw_square(surf, ulx - 3, uly - 3, (192, 192, 192), field_px + 5, 1)

        for r in range(self.field_sz):
            for c in range(self.field_sz):
                cx = ulx + c * small_sq_px
                cy = uly + r * small_sq_px

                #if this square is selected, highlight it in light green
                if r == selr and c == selc:
                    surf.fill((64, 128, 64), (cx, cy, small_sq_px - 1, small_sq_px - 1))

                #draw a border around the small square
                draw_square(surf, cx, cy, (128, 128, 128), small_sq_px - 1, 1)

                #draw possible values for empty cells, if self.display_possibilities is set
                if self.sudoku.state[r][c] == 0:
                    if self.display_possibilities:
                        poss = self.sudoku.cell_get_possibilities(r,c)
                        draw_possibilities(surf,cx,cy,poss,my_font_poss)
                    continue
                else:
                    txt = str(self.sudoku.state[r][c])

                #choose different font and color for given cells (self.src_field[r][c] != 0),
                #and for inputted by user
                if self.src_field[r][c] != 0:
                    fnt = my_font_bold
                    if self.sudoku.cell_has_no_conflicts(r, c):
                        col = (0, 0, 0)
                    else:
                        col = (128, 0, 0)
                else:
                    fnt = my_font
                    if self.sudoku.cell_has_no_conflicts(r, c):
                        col = (64, 64, 128)
                    else:
                        col = (128, 64, 64)

                #draw the value in the cell
                txt_blit = fnt.render(txt, True, col)
                (txt_szx, txt_szy) = txt_blit.get_size()
                txt_x = cx + (small_sq_px - txt_szx) // 2
                txt_y = cy + (small_sq_px - txt_szy) // 2
                surf.blit(txt_blit, (txt_x, txt_y))

        #draw borders around 3x3 squares
        for r in range(self.field_sz // self.sq_sz):
            for c in range(self.field_sz // self.sq_sz):
                draw_square(surf, ulx + c * big_sq_px, uly + r * big_sq_px, (0, 0, 0), big_sq_px - 1, 1)


class TextInput:
    """ Class for receiving text input from user"""
    def __init__(self,rect,max_len,font_size,prompt):
        self.result = None
        self.prompt = prompt
        self.text = ""
        self.rect = rect
        self.max_len = max_len
        self.my_font = pygame.font.SysFont("Arial", font_size, False)

    def process_event(self, ev):
        if ev.type==pygame.KEYDOWN:
            key = ev.key

            if key==pygame.K_ESCAPE:
                self.result = "Cancel"
                return

            if key==pygame.K_RETURN:
                self.result = "OK"
                return

            if key==pygame.K_BACKSPACE:
                if len(self.text)>0:
                    self.text = self.text[:len(self.text)-1]

                return

            ch = pygame.key.name(key)
            if len(ch) > 1: #some special key
                return

            if len(self.text)<self.max_len:
                self.text = self.text + ch

    def draw(self, surf):
        (ulx,uly,w,h) = self.rect
        border_colors = [(192,192,192),(128,128,128),(64,64,64),(0,0,0)]
        margin = len(border_colors)
        for i in range(len(border_colors)):
            pygame.draw.polygon(surf, border_colors[i], (
                (ulx + i, uly + i),
                (ulx + w - 1 - i, uly + i),
                (ulx + w - 1 - i, uly + h - 1 - i),
                (ulx + i, uly + h - 1 - i)), 1)

        surf.fill((128,128,128),(ulx + margin, uly + margin, w - margin * 2, h - margin * 2))

        txt_blit = self.my_font.render(self.prompt + self.text, True, (64,64,128))
        txt_pos = (ulx + margin + 1, uly + margin + 1)
        surf.blit(txt_blit,txt_pos)


def process_text_input(field,text,text_type):
    if text_type == "ngiven":
        try:
            ngiven = int(text)
            if ngiven >= 21 and ngiven <= 50:
                field.generate(ngiven)
            else:
                my_error = ValueError("")
                raise my_error
        except:
            messagebox.showinfo(title="Error!",
                                message="Please enter a valid integer in range 21..50")

    elif text_type == "randseed":
        try:
            seed = int(text)
            if seed >= 0 and seed < 2**31:
                field.randseed = seed
            else:
                my_error = ValueError("")
                raise my_error
        except:
            messagebox.showinfo(title="Error!",
                                message="Please enter a valid integer in range 0..{0}".format(2**31))


def main():

    field = SudokuField(9,3)
    field.generate()

    pygame.init()
    surface_w = 800
    main_surface = pygame.display.set_mode((surface_w, surface_w + 50))
    pygame.display.set_caption("Sudoku game by Ivan Goursky")

    head_font = pygame.font.SysFont("Arial", 36, False)

    my_clock = pygame.time.Clock()

    help_displayed = False

    t0 = time.time()

    text_input = None
    text_input_type = ""

    while True:
        ev = pygame.event.poll()
        if ev.type==pygame.QUIT:
            break

        if text_input is not None:
            text_input.process_event(ev)
            if text_input.result is not None:
                if text_input.result == "OK":
                    process_text_input(field,text_input.text,text_input_type)
                text_input = None
        else:
            field.process_event(ev)

        if text_input is None and ev.type==pygame.KEYDOWN:
            key = ev.key
            ch = pygame.key.name(key)
            if ch == "n":
                if field.pos is not None:
                    w = 600
                    h = 70
                    (ulx,uly) = field.pos
                    txt_x = ulx + (field.field_px - w) // 2
                    txt_y = uly + (field.field_px - h) // 2
                    text_input = TextInput((txt_x, txt_y, w, h), 4, 32, "Number of given cells (21..50): ")
                    text_input_type = "ngiven"
                    field.selection = None

            if ch == "r":
                if field.pos is not None:
                    w = 600
                    h = 70
                    (ulx,uly) = field.pos
                    txt_x = ulx + (field.field_px - w) // 2
                    txt_y = uly + (field.field_px - h) // 2
                    text_input = TextInput((txt_x, txt_y, w, h), 10, 32,
                                           "RNG seed (0..{0}): ".format(2**31))
                    text_input_type = "randseed"
                    field.selection = None

        if  field.sudoku.board_has_no_conflicts() and field.sudoku.empty_cells_count()==0:
            anim_time = time.time() - t0
            colors = [(255, 192, 192), (192, 255, 192), (192, 192, 255)]
            col = colors[int(anim_time*3)%3]
        else:
            col = (192, 192, 192)

        main_surface.fill(col)

        field.draw(main_surface, (5, 55), 87)
        if text_input is not None:
            text_input.draw(main_surface)

        txt_blit = head_font.render("№"+field.sudoku_number, True, (0,0,0))
        txt_w = txt_blit.get_size()[0]
        main_surface.blit(txt_blit,((surface_w-txt_w)//2,5))

        pygame.display.flip()

        if not help_displayed:
            display_help()
            help_displayed = True

        my_clock.tick(240)

    pygame.quit()

main()