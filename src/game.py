import random
from solvers import (
    EntropicSolver,
    KnuthMinMaxSolver,
    MastermindSolver,
    RandomSolver,
    UserSolver,
)
from utils import get_all_codes, get_int_input


def play():
    print("Welcome to Mastermind!")
    print("You can play against the computer or let the computer play against you.")
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
    letters_pool = "ABCDEFGH"[:nb_colors]
    if mode == 1:
        solver = UserSolver()
        pool = get_all_codes(nb_colors)
        secret_code = "".join(random.sample(letters_pool, 4))
        solver.solve(
            nb_colors, secret=secret_code, custom_pool=pool, alone=True, debug=True
        )
    if mode == 2:
        print(
            f"""Choose a secret code consisting of 4 letters between A and {letters_pool[-1]}. \
The solver will try to guess it using information theory."""
        )
        print("Let's play !")
        print("-----")
        solver = KnuthMinMaxSolver()
        pool = get_all_codes(nb_colors)
        solver.solve(nb_colors, custom_pool=pool, alone=False)


if __name__ == "__main__":
    play()
