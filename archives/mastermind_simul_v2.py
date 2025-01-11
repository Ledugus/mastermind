import math
import os
import random
import numpy as np
import statistics
from utils import *

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def log2(x):
    return math.log2(x) if x > 0 else 0


def get_all_combinations(nb_colors):
    colors = ["A", "B", "C", "D", "E", "F", "G", "H"]

    combinations = [
        f"{w}{z}{y}{x}"
        for x in colors[:nb_colors]
        for y in colors[:nb_colors]
        for z in colors[:nb_colors]
        for w in colors[:nb_colors]
    ]
    return combinations


def combination_to_integer(code, nb_colors):
    integer = 0
    for i in range(4):
        integer += (nb_colors**i) * int(ord(code[i]) - 65)
    return integer


def integer_to_combination(integer, nb_colors):
    result = ""
    curr = integer
    for x in range(4):
        result = result + chr((curr % nb_colors) + 65)
        curr = curr // nb_colors
    return result


def pattern_to_int_list(pattern):
    """Translate an int btw 0 and 40 into a list of 2 integers btw 0 and 2"""
    return [(pattern - (pattern % 10)) // 10, pattern % 10]


def evaluate_pattern(code1, code2):
    """Evaluate the correction pattern got from the comparison of code1 and code2
    Returns an integer btw 0 and 40"""
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

    return 10 * (pattern.count(2)) + (pattern.count(1))


# Return for each pattern the number of codes that get it as feedback for each possibility in pool
def all_patterns_distribution(code, pool):
    distribution = np.zeros(41, dtype=np.uint16)
    for x in pool:
        distribution[evaluate_pattern(code, x)] += 1
    return distribution


# Sum for all patterns the entropy formula (exception if nb_patterns = 0)
# Returns a number, the average information in bit that the code would get as guess
def expected_information(code, pool):
    expected_information_of_code = 0
    for nb_of_this_pattern in all_patterns_distribution(code, pool):
        if nb_of_this_pattern != 0:
            expected_information_of_code += (nb_of_this_pattern / len(pool)) * (
                log2(len(pool) / nb_of_this_pattern)
            )
    return expected_information_of_code


# Return a list of 3 terms
# 1 : the string of the best guess
# 2 : the entropy of the best
# 3 : the remaining information on average
def find_best_guess(pool):
    best = ""
    max_entropy = 0
    for code in pool:
        e_i = expected_information(code, pool)
        if e_i >= max_entropy:
            best = code
            max_entropy = e_i

    return [best, max_entropy, log2(len(pool)) - max_entropy]


# Gets all codes that are still possible as an answer
def get_all_codes_matching_pattern(code, pattern, pool):
    all_matches = []
    for x in pool:
        if evaluate_pattern(code, x) == pattern:
            all_matches.append(x)
    return all_matches


# If you play against someone, you enter yourself feedback. This function protects from type errors
def get_clean_feedback():
    while True:
        feedback = input("Entrez le feedback : ")
        if feedback.isdigit():
            if int(feedback) in [0, 1, 2, 3, 4, 10, 11, 12, 13, 20, 21, 22, 30, 40]:
                return int(feedback)
        print(
            "Please respect format : 2 digits between 0 and 4 without spaces. "
            "First is nb of well placed colors, second is nb of misplaced"
        )


def play_game(nb_colors, pool, alone=True, set_secret=False, secret=None):
    """
    Let the computer play a game, choosing randomly a secret_code and trying to guess it independently if alone == True.
    You can use this function to crack a game, using alone = False and setting the right number of colors.
    It prints some information at each iteration
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
            results = find_best_guess(current_pool)
        if alone:
            pattern = evaluate_pattern(results[0], secret_code)
        else:
            pattern = get_clean_feedback()
        new_pool = get_all_codes_matching_pattern(results[0], pattern, current_pool)
        nb_guess += 1
        current_pool = new_pool
        if pattern == 40:
            correct = True
    return nb_guess


def play_game_with_prints(nb_colors, pool, alone=True, set_secret=False, secret=None):
    """
    Let the computer play a game, choosing randomly a secret_code and trying to guess it independently if alone == True.
    You can use this function to crack a game, using alone = False and setting the right number of colors.
    It prints some information at each iteration
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
            results = find_best_guess(current_pool)
        print(f"Guess n°{nb_guess + 1}: {results[0]}")
        if alone:
            pattern = evaluate_pattern(results[0], secret_code)
        else:
            pattern = get_clean_feedback()

        print("FeedBack : ", pattern_to_int_list(pattern))
        new_pool = get_all_codes_matching_pattern(results[0], pattern, current_pool)
        print("Remaining possibilities : ", new_pool)
        print("Information got : ", log2(len(current_pool) / len(new_pool)))
        print("Number of RP : ", len(new_pool))
        nb_guess += 1
        current_pool = new_pool
        print()
        if pattern == 40:
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
