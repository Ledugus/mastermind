import math
import os
import random

# import matplotlib.pyplot as plt
import numpy as np
import statistics
from utils import *


# Return for each pattern the number of codes that get it as feedback for each possibility in pool
def all_patterns_distribution(code, pool):
    distribution = np.zeros(41, dtype=np.uint16)
    for x in pool:
        distribution[evaluate_pattern(code, x)] += 1
    return distribution


# Sum for all patterns the entropy formula (exception if nb_patterns = 0)
# Returns a number, the average information in bit that the code would get as guess
def expected_information(code, pool):
    return max(all_patterns_distribution(code, pool))


# Return a list of 3 terms
# 1 : the string of the best guess
# 2 : the entropy of the best
# 3 : the remaining information on average
def find_best_guess(pool):
    best = ""
    minimax = len(pool) + 1
    for code in pool:
        e_i = expected_information(code, pool)
        if e_i < minimax:
            best = code
            minimax = e_i

    return [best, minimax]


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
                ["AAAA", "ABBB", "BCCC", "BCDD", "DDEE", "EEFF", "GFED", "HGFE"][
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

