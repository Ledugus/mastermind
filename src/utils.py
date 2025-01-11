import os
import math
import numpy as np
import itertools as it

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def log2(x):
    return math.log2(x) if x > 0 else 0


def get_all_codes(nb_colors):
    colors = ["A", "B", "C", "D", "E", "F", "G", "H"]

    codes = [
        f"{w}{z}{y}{x}"
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


def get_clean_feedback():
    """If you play against someone, you enter yourself feedback.
    This function reads and cleans user input : return an integer between 0 and 40"""
    while True:
        feedback = input("Entrez le feedback : ")
        if feedback.isdigit():
            if feedback in list(str(x) + str(y) for x in range(5) for y in range(5)):
                return 5 * int(feedback[0]) + int(feedback[1])
        print(
            "Please respect format : 2 digits between 0 and 4 without spaces. "
            "First is nb of well placed colors, second is nb of misplaced"
        )


def get_all_codes_matching_pattern(code, feedback_pattern, pool):
    """Finds all codes that are still possible as an answer, based on the feedback pattern"""
    return list(filter(lambda x: evaluate_pattern(code, x) == feedback_pattern, pool))