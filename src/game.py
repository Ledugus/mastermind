import random
from solvers import EntropicSolver, MastermindSolver, RandomSolver, UserSolver
from utils import get_all_codes, get_int_input


def play():
    print("Welcome to Mastermind!")
    print("Choose your mode:")
    print("1. Try to guess the code")
    print("2. Let the computer guess your code")
    mode = get_int_input(
        "Enter 1 or 2: ", (1, 2), "Invalid choice. Please enter 1 or 2."
    )
    nb_colors = get_int_input(
        "Enter the number of colors (between 2 and 8): ",
        (2, 8),
        "Invalid number of colors. Please enter a number between 2 and 8.",
    )
    if mode == 1:
        solver = UserSolver()
        pool = get_all_codes(nb_colors)
        secret_code = "".join(random.sample("ABCDEFGH"[:nb_colors], 4))
        solver.solve(
            nb_colors, secret=secret_code, custom_pool=pool, alone=True, debug=True
        )
    if mode == 2:
        solver = EntropicSolver()
        pool = get_all_codes(nb_colors)
        solver.solve(nb_colors, custom_pool=pool, alone=False)


if __name__ == "__main__":
    play()
