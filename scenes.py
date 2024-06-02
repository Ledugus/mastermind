from manim import *
from mastermind_simul import *


class VideoTitle(Scene):
    def construct(self):
        title = Text("Résoudre MasterMind", color=BLUE).shift(1 * UP)
        subtitle = Text("Avec la théorie de l'information", color=WHITE).set_opacity(0.8).scale(0.8)
        subtitle.next_to(title, DOWN, buff=0.3)
        circle_radius_to_square_height = 0.4
        self.add(title)
        self.play(Write(subtitle))
        self.wait()


class MasterMindScene(Scene):
    grid_height = 9
    n_colums = 5
    grid_center = ORIGIN
    secret_code = None
    color_map = {
        "A": RED,
        "B": BLUE,
        "C": YELLOW,
        "D": GREEN,
        "E": ORANGE,
        "F": GREY,
        "G": WHITE,
        "H": PURPLE,
        0: BLACK,
        1: GREY,
        2: WHITE
    }

    def setup(self):
        self.all_codes = self.get_all_combi()
        if self.secret_code is None:
            all_codes = get_all_combinations(8)
            self.secret_code = random.choice(all_codes)
        self.guesses = []
        self.patterns = []
        self.possibilities = self.get_all_combi()

        self.add_grid()

    def get_all_combi(self):
        return get_all_combinations(8)

    def get_pattern(self, guess):
        return evaluate_pattern(guess, self.secret_code)

    def add_grid(self):
        buff = 0.1
        row = Square(side_length=1).get_grid()
        grid = row.get_grid(9)
        grid.set_height(self.grid_height)
        grid.move_to(self.grid_center)
        grid.set_stroke(WHITE, 2)
        grid.codes = VGroup()
        grid.pending_code = VGroup()
        grid.add(grid.codes, grid.pending_code)
        grid.pending_pattern = None
        grid.add_updater(lambda m: m)
        self.grid = grid
        self.add(grid)

    def add_pattern_grid(self):
        buff = 0
        row = Square(side_length=0.5).get_grid(1, 2, buff=buff)
        pattern_grid = row.get_grid(18, 0.5, buff=buff)
        pattern_grid.next_to(self.grid, RIGHT, buff=0.1)

    def get_curr_row(self):
        return self.grid[len(self.grid.codes)]

    def get_curr_square(self):
        row = self.get_curr_row()
        return row[len(self.grid.pending_code)]

    def add_letter(self, pawn_color):
        grid = self.grid
        if len(grid.pending_word) == len(grid[0])-1:
            return

        letter_mob = self.get_letter_in_square(pawn_color, self.get_curr_square())
        grid.pending_word.add(letter_mob)

    def get_letter_in_square(self, pawn_color, square):
        circle_radius = 0.4 * square.get_height()
        pawn_mob = Circle(fill_opacity=1, radius=circle_radius).fill_color(self.color_map[pawn_color])
        pawn_mob.move_to(square)
        return pawn_mob

    def show_pattern(self, pattern, animate=False, added_anims=[]):
        row = self.get_curr_row()
        colors = self.get_colors(pattern)
        if animate:
            self.animate_color_change(row, self.grid.pending_word, colors, added_anims)
        else:
            self.set_row_colors(row, colors)

        self.grid.pending_pattern = pattern

    def get_colors(self, pattern):
        return [self.color_map[key] for key in pattern_to_int_list(pattern)]

    def set_pattern_colors(self, row, colors):
        pass

    def construct(self):
        self.add_grid()
        self.add_pattern_grid()
