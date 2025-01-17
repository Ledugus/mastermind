import math
import os
import random
import numpy as np
import statistics
from utils import *

PATTERN_MATRIX = os.path.join(DATA_DIR, "pattern_matrix.npy")


def evaluate_pattern(code1, code2):
    pattern = np.zeros(4)
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
    pattern.sort()
    return pattern_to_integer(pattern)


def get_all_patterns_matrix(nb_colors):
    pool = get_all_combinations(nb_colors)
    pattern_matrix = np.zeros([nb_colors**4, nb_colors**4], dtype=np.uint8)
    for i in range(len(pool)):
        for j in range(i, len(pool)):
            pattern = evaluate_pattern(pool[i], pool[j])
            pattern_matrix[i][j] = pattern
            pattern_matrix[j][i] = pattern
    return pattern_matrix


def get_pattern(code1, code2, nb_colors):
    pass


# Gets all patterns of code w/ any elements of the pool (all combinations left).
# the pattern is an integer btw 0 and 80
# Returns a list of length of the pool
def get_all_patterns(code, pool, nb_colors):
    all_patterns = []
    pattern_matrix = np.load(os.path.join(DATA_DIR, f"pattern_matrix_{nb_colors}.npy"))
    code_index = combination_to_integer(code, nb_colors)
    for x in pool:
        all_patterns.append(
            pattern_matrix[code_index, combination_to_integer(x, nb_colors)]
        )

    return all_patterns


def all_patterns_distribution(code, pool, nb_colors):
    """
    Return for each pattern the number of codes that get it as feedback for each possibility in pool
    """
    pattern_matrix = np.load(os.path.join(DATA_DIR, f"pattern_matrix_{nb_colors}.npy"))
    code_index = combination_to_integer(code, nb_colors)
    distribution = np.zeros(81, dtype=np.uint16)
    for x in pool:
        distribution[
            pattern_matrix[code_index, combination_to_integer(x, nb_colors)]
        ] += 1
    return distribution


def expected_information(code, pool, nb_colors):
    """
    Sum for all patterns the entropy formula (exception if nb_patterns = 0
    Returns a number, the average information in bit that the code would get as guess
    """
    expected_information_of_code = 0
    for nb_of_this_pattern in all_patterns_distribution(code, pool, nb_colors):
        if nb_of_this_pattern != 0:
            expected_information_of_code += (nb_of_this_pattern / len(pool)) * (
                log2(len(pool) / nb_of_this_pattern)
            )
    return expected_information_of_code


def find_best_guess(pool, nb_colors):
    """
    Return a list of 3 terms
    1 : the string of the best guess
    2 : the entropy of the best
    3 : the remaining information on average
    """
    best = ""
    max_entropy = 0
    for code in pool:
        e_i = expected_information(code, pool, nb_colors)
        if e_i >= max_entropy:
            best = code
            max_entropy = e_i

    return [best, max_entropy, log2(len(pool)) - max_entropy]


def get_all_codes_matching_pattern(code, pattern, pool, nb_colors):
    """
    Gets all codes that are still possible as an answer
    """
    all_matches = []
    pattern_matrix = np.load(os.path.join(DATA_DIR, f"pattern_matrix_{nb_colors}.npy"))
    code_index = combination_to_integer(code, nb_colors)
    for x in pool:
        if pattern_matrix[code_index, combination_to_integer(x, nb_colors)] == pattern:
            all_matches.append(x)
    return all_matches


def get_clean_feedback():
    """
    If you play against someone, you enter yourself feedback. This function protects from type errors.
    """
    while True:
        feedback = input("Entrez le feedback : ")
        if len(feedback) == 4:
            digit = 0
            for x in feedback:
                if x in ["0", "1", "2"]:
                    digit += 1
            if digit == 4:
                feedback = list(map(int, feedback))
                feedback_sorted = sorted(feedback)
                if feedback == feedback_sorted:
                    return feedback
        print(
            "Please respect format : 4 characters, 0s, 1s and 2s without space, numbers are in ascending order !"
        )


def play_game(nb_colors, pool, alone=True, set_secret=False, secret=None):
    """
    Let the computer play a game, choosing randomly a secret_code and trying to guess it independently if alone == True.
    You can use this function to crack a game, using alone = False and setting the right number of colors.
    """
    current_pool = pool
    if alone:
        secret_code = secret if set_secret else random.choice(current_pool)
        print("Secret code", secret_code)
    correct = False
    nb_guess = 0
    while not correct:
        if nb_guess == 0:
            results = [
                ["AAAA", "BBBA", "CCBB", "DDCB", "EEDC", "FEDC", "GFED", "HGFE"][
                    nb_colors - 1
                ]
            ]
        else:
            results = find_best_guess(current_pool, nb_colors)
        if alone:
            pattern = evaluate_pattern(results[0], secret_code)
        else:
            pattern = pattern_to_integer(get_clean_feedback())
        new_pool = get_all_codes_matching_pattern(
            results[0], pattern, current_pool, nb_colors
        )
        nb_guess += 1
        current_pool = new_pool
        if pattern == 80:
            correct = True
    print("Number of guesses : ", nb_guess)
    return nb_guess


def play_game_with_prints(nb_colors, pool, alone=True, set_secret=False, secret=None):
    """
    Same, but prints some information about the resolution.
    """
    current_pool = pool
    if alone:
        secret_code = secret if set_secret else random.choice(current_pool)
        print("Secret code", secret_code)
    correct = False
    nb_guess = 0
    while not correct:
        if nb_guess == 0:
            results = [
                ["AAAA", "BBBA", "CCBB", "DDCB", "EEDC", "FEDC", "GFED", "HGFE"][
                    nb_colors - 1
                ]
            ]
        else:
            results = find_best_guess(current_pool, nb_colors)
        print(f"Guess n°{nb_guess + 1}: {results[0]}")
        if alone:
            pattern = evaluate_pattern(results[0], secret_code)
        else:
            pattern = pattern_to_integer(get_clean_feedback())

        print("FeedBack : ", pattern_to_int_list(pattern))
        new_pool = get_all_codes_matching_pattern(
            results[0], pattern, current_pool, nb_colors
        )
        print("Remaining possibilities : ", new_pool)
        print("Information got : ", log2(len(current_pool) / len(new_pool)))
        print("Number of RP : ", len(new_pool))
        nb_guess += 1
        current_pool = new_pool
        print()
        if pattern == 80:
            correct = True
            print("Answer : ", results[0])
    print("Found in", nb_guess, "guesses.")
    print()
    print()
    return nb_guess


# This simulates all possible games, en fonction of nb_colors you choose
def play_all_games_alone(nb_colors):
    all_nb_of_guesses = []
    pool = get_all_combinations(nb_colors)
    for secret_code in pool:
        all_nb_of_guesses.append(
            play_game(
                nb_colors, pool=pool, alone=True, set_secret=True, secret=secret_code
            )
        )
    return statistics.mean(all_nb_of_guesses)


# TODO: make a manim animation
# TODO: Optimize code, redondant calculation etc. (ca avance)
