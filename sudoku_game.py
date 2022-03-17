import pygame
import sudoku
import copy
import time
from tkinter import messagebox

def generate_one_field(ngiven=23, randseed = None):
    sud=sudoku.Sudoku()
    if randseed is not None:
        sud.rnd_seed = randseed
    for i in range(3):
        #print("Iteration: ",i)
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
        boards = sud.generate_board(ngiven,1,10000,10)

        if len(boards)==1:
            return boards[0]

    return []

def draw_square(surf,ulx,uly,col,sz,lwd):
    pygame.draw.polygon(surf, col, (
        (ulx, uly),
        (ulx + sz, uly),
        (ulx + sz, uly + sz),
        (ulx, uly + sz)), lwd)

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

    def generate(self,ngiven=25):
        field = generate_one_field(ngiven,self.randseed)
        if len(field) > 0:
            self.sudoku = sudoku.Sudoku(field)
            self.src_field = copy.deepcopy(self.sudoku.state)
        else:
            messagebox.showinfo(title = "Warning",message="Could not generate sudoku, try one more time")

        if self.sudoku is None:
            self.sudoku = sudoku.Sudoku()

    def process_event(self, ev):
        if ev.type==pygame.KEYDOWN:
            key = ev.key

            if key==pygame.K_ESCAPE:
                self.selection = None

            ch = pygame.key.name(key)

            if ch == "c":
                self.sudoku.state = copy.deepcopy(self.src_field)

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

        if ev.type == pygame.MOUSEBUTTONDOWN:
            (cx,cy) = ev.dict["pos"]

            (ulx,uly) = self.pos
            r=(cy-uly)//self.cell_px
            c = (cx - ulx) // self.cell_px
            if r>=0 and r<self.field_sz and c>=0 and c<self.field_sz:
                if self.src_field[r][c]==0:
                    self.selection = (r,c)

    def draw(self, surf):
        my_font = pygame.font.SysFont("Arial", 72, False)
        my_font_bold = pygame.font.SysFont("Arial", 72, True)
        (sx, sy) = surf.get_size()
        surf_px = min(sx, sy)

        margin = 5
        ulx = margin
        uly = margin
        self.pos = (ulx, uly)

        small_sq_px = (surf_px - margin * 2) // self.field_sz
        self.cell_px = small_sq_px
        big_sq_px = small_sq_px * self.sq_sz
        field_px = small_sq_px * self.field_sz
        self.field_px = field_px

        if self.selection is not None:
            (selr, selc) = self.selection
        else:
            selr = -1
            selc = -1

        draw_square(surf, ulx - 1, uly - 1, (64, 64, 64), field_px + 1, 1)
        draw_square(surf, ulx - 2, uly - 2, (128, 128, 128), field_px + 3, 1)
        draw_square(surf, ulx - 3, uly - 3, (192, 192, 192), field_px + 5, 1)

        for r in range(self.field_sz):
            for c in range(self.field_sz):
                cx = ulx + c * small_sq_px
                cy = uly + r * small_sq_px
                if r == selr and c == selc:
                    surf.fill((64, 128, 64), (cx, cy, small_sq_px - 1, small_sq_px - 1))

                draw_square(surf, cx, cy, (128, 128, 128), small_sq_px - 1, 1)
                if self.sudoku.state[r][c] == 0:
                    continue
                else:
                    txt = str(self.sudoku.state[r][c])

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

                txt_blit = fnt.render(txt, True, col)
                (txt_szx, txt_szy) = txt_blit.get_size()
                txt_x = cx + (small_sq_px - txt_szx) // 2
                txt_y = cy + (small_sq_px - txt_szy) // 2
                surf.blit(txt_blit, (txt_x, txt_y))

        for r in range(self.field_sz // self.sq_sz):
            for c in range(self.field_sz // self.sq_sz):
                draw_square(surf, ulx + c * big_sq_px, uly + r * big_sq_px, (0, 0, 0), big_sq_px - 1, 1)

class TextInput:
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
            if ngiven >= 23 and ngiven <= 50:
                field.generate(ngiven)
            else:
                my_error = ValueError("")
                raise my_error
        except:
            messagebox.showinfo(title="Error!",
                                message="Please enter a valid integer in range 23..50")

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
    surface_size = 800
    main_surface = pygame.display.set_mode((surface_size, surface_size))
    pygame.display.set_caption("Sudoku game by Ivan Goursky")
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
                    text_input = TextInput((txt_x, txt_y, w, h), 4, 32, "Number of given cells (23..50): ")
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

        field.draw(main_surface)
        if text_input is not None:
            text_input.draw(main_surface)
        pygame.display.flip()

        if not help_displayed:
            display_help()
            help_displayed = True

        my_clock.tick(240)

    pygame.quit()

main()