import pygame
import sudoku
import copy

def generate_one_field(ngiven=23):
    sud=sudoku.Sudoku()
    for i in range(50):
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


class SudokuField:
    def __init__(self, sud, src_field, field_sz, sq_sz):
        self.sudoku = sud
        self.src_field = src_field
        self.field_sz = field_sz
        self.sq_sz = sq_sz
        self.selection = None
        self.pos = None

    def process_event(self, ev):
        if ev.type==pygame.KEYDOWN:
            key = ev.key
            if key==ord("c"):
                self.sudoku.state = copy.deepcopy(self.src_field)

            if key==pygame.K_ESCAPE:
                self.selection = None

            ch = pygame.key.name(key)
            if "0123456789".__contains__(ch):
                if self.selection is not None:
                    v = int(ch)
                    (r,c) = self.selection
                    self.sudoku.state[r][c]=v
                    self.selection = None

        if ev.type == pygame.MOUSEBUTTONDOWN:
            (cx,cy) = ev.dict["pos"]

            (ulx,uly) = self.pos
            r=(cy-uly)//self.cell_size
            c = (cx - ulx) // self.cell_size
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
        self.cell_size = small_sq_px
        big_sq_px = small_sq_px * self.sq_sz
        field_px = small_sq_px * self.field_sz

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


def main():

    field = generate_one_field(25)
    if len(field)>0:
        sud = sudoku.Sudoku(field)
    else:
        sud = sudoku.Sudoku()

    src_field = copy.deepcopy(sud.state)

    field = SudokuField(sud,src_field,9,3)

    pygame.init()
    surface_size = 800
    main_surface = pygame.display.set_mode((surface_size, surface_size))
    my_clock = pygame.time.Clock()

    anim_frame = 0

    while True:
        ev = pygame.event.poll()
        if ev.type==pygame.QUIT:
            break

        field.process_event(ev)

        if  field.sudoku.board_has_no_conflicts() and field.sudoku.empty_cells_count()==0:
            colors = [(255, 192, 192), (192, 255, 192), (192, 192, 255)]
            col = colors[(anim_frame//80)%3]
        else:
            col = (192, 192, 192)

        main_surface.fill(col)

        field.draw(main_surface)
        pygame.display.flip()
        my_clock.tick(240)
        anim_frame+=1

    pygame.quit()

main()