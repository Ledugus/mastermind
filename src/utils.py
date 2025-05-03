import os
import math
import numpy as np
import itertools as it

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def progress_bar(progress, total, bar_length=40):
    """Display a progress bar in the console."""
    percent = (progress / total) * 100
    filled_length = int(bar_length * progress // total)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)
    print(f"\r|{bar}| {percent:.2f}%", end="\r")
    if progress == total:
        print()


def log2(x):
    return math.log2(x) if x > 0 else 0


def get_all_codes(nb_colors):
    colors = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    codes = [
        f"{x}{y}{z}{w}"
        for x in colors[:nb_colors]
        for y in colors[:nb_colors]
        for z in colors[:nb_colors]
        for w in colors[:nb_colors]
    ]
    return codes


def evaluate_pattern(code1, code2):
    """Evaluate the correction pattern got from the comparison of code1 and code2
    This function is symmetric, i.e. evaluate_pattern(code1, code2) == evaluate_pattern(code2, code1)
    Returns an integer between 0 and 80 (3**4 possible patterns)"""
    pattern = [0, 0, 0, 0]
    for i in range(len(code1)):
        if code1[i] == code2[i] and pattern[i] == 0:
            pattern[i] = 2
            code2 = code2[0:i] + " " + code2[i + 1 : 4]
    for i in range(len(code1)):
        if code1[i] in code2 and pattern[i] == 0:
            pattern[i] = 1
            for j in range(len(code2)):
                if code2[j] == code1[i]:
                    code2 = code2[0:j] + " " + code2[j + 1 : 4]
                    break

    return 5 * (pattern.count(2)) + (pattern.count(1))


def evaluate_patterns(pool):
    """Evaluate naively all patterns between all codes in the pool"""
    pattern_matrix = np.zeros((len(pool), len(pool)), dtype=np.uint8)
    for i, code1 in enumerate(pool):
        for j, code2 in enumerate(pool[i:]):
            pattern_matrix[i, j] = evaluate_pattern(code1, code2)
            pattern_matrix[j, i] = pattern_matrix[i, j]
    return pattern_matrix


def get_patterns_distribution(code, pool):
    """Return for each pattern the number of codes that get it as feedback
    when testing against all possibilities in the pool"""
    distribution = np.zeros(21, dtype=np.uint16)
    for x in pool:
        distribution[evaluate_pattern(code, x)] += 1
    return distribution


def get_patterns_probability_distribution(code, pool):
    """Return for each pattern the probability of getting it as feedback
    when testing against all possibilities in the pool"""
    distribution = get_patterns_distribution(code, pool)
    return distribution / np.sum(distribution)


def get_patterns_distribution_matrix(pool):
    pattern_matrix = evaluate_pattern_matrix(pool)
    n = len(pool)
    distributions = np.zeros((n, 21), dtype=np.float32)
    n_range = np.arange(n)
    for j in range(n):
        distributions[n_range, pattern_matrix[:, j]] += 1
    return distributions


def get_patterns_probability_distribution_matrix(pool):
    distributions = get_patterns_distribution_matrix(pool)
    return distributions / len(pool)


def pattern_int_to_list(pattern):
    return [pattern // 5, pattern % 5]


def code_to_int_array(code):
    return np.array([ord(c) - 65 for c in code], dtype=np.uint8)


def int_to_int_array(code, nb_colors):
    """Convert an integer representation back to an array of integers based on the number of colors"""
    int_array = np.zeros(4, dtype=np.uint8)
    for i in range(4)[::-1]:
        int_array[3 - i] = code // nb_colors**i
        code -= int_array[3 - i] * nb_colors**i

    return int_array


def code_to_int(code, nb_colors):
    """Convert a code to an integer representation based on the number of colors"""
    return sum((ord(c) - 65) * (nb_colors ** (3 - i)) for i, c in enumerate(code))


def int_to_code(code, nb_colors):
    """Convert an integer representation back to a code based on the number of colors"""
    colors = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join(colors[(code // (nb_colors**i)) % nb_colors] for i in range(4)[::-1])


def evaluate_pattern_matrix(pool):
    """Evaluate all patterns between all codes in the pool using vectorized operations"""
    pattern_matrix = np.zeros((len(pool), len(pool)), dtype=np.uint8)
    nl = 4
    pool = np.array([code_to_int_array(code) for code in pool])
    ncode = len(pool)
    equality_grid = np.zeros((ncode, ncode, nl, nl), dtype=bool)
    for i, j in it.product(range(nl), range(nl)):
        equality_grid[:, :, i, j] = np.equal.outer(pool[:, i], pool[:, j])
    for i in range(nl):
        matches = equality_grid[:, :, i, i].flatten()
        pattern_matrix.flat[matches] += 5
        for k in range(nl):
            equality_grid[:, :, k, i].flat[matches] = False
            equality_grid[:, :, i, k].flat[matches] = False
    for i, j in it.product(range(nl), range(nl)):
        matches = equality_grid[:, :, i, j].flatten()
        pattern_matrix.flat[matches] += 1
        for k in range(nl):
            equality_grid[:, :, k, j].flat[matches] = False
            equality_grid[:, :, i, k].flat[matches] = False

    return pattern_matrix


def get_int_input(prompt, bounds, error_message):
    """Get an integer input from the user within specified bounds"""
    while True:
        user_input = input(prompt)
        try:
            value = int(user_input)
            if bounds[0] <= value <= bounds[1]:
                return value
            print(error_message)
        except ValueError:
            print("Invalid input. Please enter a number or a valid command.")


def get_clean_feedback():
    """If you play against someone, you enter yourself feedback.
    This function reads and cleans user input : return an integer between 0 and 40"""
    while True:
        feedback = input("Enter feedback : ")
        if feedback.isdigit():
            if feedback in list(str(x) + str(y) for x in range(5) for y in range(5)):
                return 5 * int(feedback[0]) + int(feedback[1])
        print(
            "Please respect format : 2 digits between 0 and 4 without spaces. "
            "First is nb of well placed colors, second is nb of misplaced"
        )


def get_all_codes_matching_pattern(code_indx, feedback_pattern, pool, pattern_matrix):
    """Finds all codes that are still possible as an answer, based on the feedback pattern"""
    return np.where(pattern_matrix[code_indx][pool] == feedback_pattern)[0].tolist()
