import random
import json
from abc import ABC, abstractmethod

import numpy as np
from scipy import stats
from utils import *


class MastermindSolver(ABC):
    """Abstract class for a Mastermind solver"""

    def __init__(self, name, alias, nb_colors):
        self.name = name
        self.alias = alias
        self.nb_colors = nb_colors
        self.pattern_matrix = evaluate_pattern_matrix(get_all_codes(nb_colors))
        self.first_guesses = {}

    @abstractmethod
    def get_next_guess(self, pool, guesses_indx) -> tuple[str, np.number]:
        """Return the best guess to make in the pool of possibilities
        and the score assigned to this guess by the solver."""

    @abstractmethod
    def print_guess_stats(self, result, current_pool, new_pool):
        """Print the stats of the last guess"""

    def load_first_guesses(self):
        with open(f"src/{self.alias}_first_guesses.json", "r") as f:
            self.first_guesses = json.load(f)

    def save_first_guess(self, result):
        with open(f"src/{self.alias}_first_guesses.json", "r") as f:
            first_guesses_dict = json.load(f)
            first_guesses_dict[str(self.nb_colors)] = result
        with open(f"src/{self.alias}_first_guesses.json", "w") as f:
            json.dump(first_guesses_dict, f)

    def solve(
        self,
        custom_pool=[],
        alone=True,
        secret=None,
        debug=False,
    ):
        """Solve the game Mastermind with a given number of colors.

        Args:
            custom_pool (list, optional): A list of all possible codes. Defaults to [].
            alone (bool, optional): If True, the function will generate a secret code and play against it. Defaults to True.
            secret (str, optional): The secret code to use if set_secret is True. Defaults to None.
            debug (bool, optional): If True, the function will print debug information. Defaults to False.


        Returns:
            tuple: A tuple containing the secret code, the list of guesses and the list of guesses' scores.
        """
        current_pool = (
            [code_to_int(code, self.nb_colors) for code in custom_pool]
            if custom_pool
            else list(range(self.nb_colors**4))
        )
        current_pool = np.array(current_pool, dtype=np.uint16)
        if alone:
            secret_code = (
                secret
                if secret
                else int_to_code(random.choice(current_pool), self.nb_colors)
            )
            secret_indx = code_to_int(secret_code, self.nb_colors)
        correct = False
        guesses = []
        guesses_indx = []
        scores = []
        while not correct:
            # Make the next guess
            result = self.get_next_guess(current_pool, guesses_indx)
            current_guess = result[0]
            current_guess_indx = code_to_int(current_guess, self.nb_colors)
            guesses.append(current_guess)
            guesses_indx.append(current_guess_indx)
            scores.append(result[1])

            if debug or not alone:
                print(f"Guess n°{len(guesses)} : {current_guess}")

            # Get the feedback
            if alone:
                pattern = self.pattern_matrix[current_guess_indx, secret_indx]
            else:
                pattern = get_clean_feedback()

            # Evaluate the feedback
            new_pool = current_pool[
                self.pattern_matrix[current_guess_indx, current_pool] == pattern
            ]
            if pattern == 20:
                if debug or not alone:
                    print(f"Youhou ! Solution found in {len(guesses)} guesses !")
                secret_code = current_guess
                break
            if len(new_pool) == 0:
                print("No more possibilities left ! Did you enter the right feedback ?")
                break
            if debug or not alone:
                print(
                    f"FeedBack : {pattern_int_to_list(pattern)[0]} well placed, {pattern_int_to_list(pattern)[1]} misplaced"
                )
                self.print_guess_stats(result, current_pool, new_pool)
                print("-----")
            current_pool = new_pool

        return secret_code, guesses, scores

    def solve_all_codes(self):
        """Solve the game Mastermind for all possible secret codes.
        Return a list of the result of each solve."""
        print(f"Solving all {self.nb_colors} color codes with the", self.name)
        pool = get_all_codes(self.nb_colors)
        results = [0] * len(pool)
        for i, code in enumerate(pool):
            results[i] = self.solve(secret=code)
            progress_bar(i + 1, len(pool))

        return results


class EntropicSolver(MastermindSolver):
    """A Mastermind solver based on maximising the entropy of the guess"""

    def __init__(self, nb_colors, outside_pool=False):
        name = "Entropic Solver (outside pool)" if outside_pool else "Entropic Solver"
        alias = "entr_out" if outside_pool else "entr"
        super().__init__(name, alias, nb_colors)
        self.load_first_guesses()
        self.outside_pool = outside_pool

    def print_guess_stats(self, result, current_pool, new_pool):
        """Print the stats of the last guess"""
        print(f"Expected information : {result[1]:.3f} bits")
        print(
            f"Actual information received : {log2(len(current_pool) / len(new_pool)):.3f} bits, {len(new_pool)} remaining possibilities"
        )

    def get_entropy(self, distributions):
        """Return the entropy of the distributions"""
        axis = len(distributions.shape) - 1
        return stats.entropy(distributions, base=2, axis=axis)

    def get_next_guess(self, pool, guesses_indx):
        """Return a tuple of 2 elements :
        1 : the string of the best guess
        2 : the entropy of this guess
        """
        if guesses_indx == []:
            if str(self.nb_colors) in self.first_guesses:
                return self.first_guesses[str(self.nb_colors)]
            print("Calculating first guess... (takes longer the first time)")
        if len(pool) <= 2:
            return int_to_code(pool[0], self.nb_colors), 1
        n = self.nb_colors**4
        best_score = 0
        best_guess_indx = 0
        possible_guesses = list(range(n)) if self.outside_pool else pool
        for guess_indx in possible_guesses:
            if guess_indx in guesses_indx:
                continue
            distribution = np.zeros(21, dtype=np.uint16)
            distribution[self.pattern_matrix[guess_indx, pool]] += 1
            distribution = distribution / len(pool)
            entropy = stats.entropy(distribution, base=2)
            if entropy > best_score:
                best_guess_indx = guess_indx
                best_score = entropy
            elif entropy == best_score and guess_indx in pool:
                best_guess_indx = guess_indx
                best_score = entropy
        result = (int_to_code(best_guess_indx, self.nb_colors), best_score)
        if guesses_indx == []:
            self.save_first_guess(result)
            self.load_first_guesses()

            print("First guess saved : ", result[0])
        return result


class KnuthMinMaxSolver(MastermindSolver):
    """A Mastermind solver based on Knuth's MinMax algorithm"""

    def __init__(self, nb_colors):
        super().__init__("Knuth MinMax Solver", "knuth", nb_colors)
        self.load_first_guesses()

    def print_guess_stats(self, result, current_pool, new_pool):
        """Print the stats of the last guess"""
        print(f"Maximum number of possibilities remaining : {result[1]}")

    def get_next_guess(self, pool, guesses_indx):
        if len(pool) == self.nb_colors**4:
            if str(self.nb_colors) in self.first_guesses:
                return self.first_guesses[str(self.nb_colors)]
            print("Calculating first guess... (takes longer the first time)")
        if len(pool) <= 2:
            return int_to_code(pool[0], self.nb_colors), 1
        full_pool = list(range(self.nb_colors**4))
        best_guess = 0
        best_score = np.inf
        for guess_indx in full_pool:
            if guess_indx in guesses_indx:
                continue
            distribution = np.zeros(21)
            for i in pool:
                distribution[self.pattern_matrix[guess_indx, i]] += 1
            max_pattern = np.max(distribution)
            if max_pattern < best_score:
                best_guess = guess_indx
                best_score = max_pattern
            elif max_pattern == best_score and guess_indx in pool:
                best_guess = guess_indx
                best_score = max_pattern
        result = (int_to_code(best_guess, self.nb_colors), best_score)
        if len(pool) == self.nb_colors**4:
            self.save_first_guess(result)
            self.load_first_guesses()
            print("First guess saved : ", result[0])
            print(self.first_guesses)
        return result


class RandomSolver(MastermindSolver):
    """A Mastermind solver based on random guesses"""

    def __init__(self, nb_colors):
        super().__init__("Random Solver", "rand", nb_colors)

    def print_guess_stats(self, result, current_pool, new_pool):
        """Print the stats of the last guess"""
        pass

    def get_next_guess(self, pool, guesses_indx):
        return int_to_code(random.choice(pool), self.nb_colors), 1 / len(pool)


class UserSolver(MastermindSolver):
    """A Mastermind solver based on user input"""

    def __init__(self, nb_colors):
        super().__init__("User Solver", "user", nb_colors)

    def print_guess_stats(self, result, current_pool, new_pool):
        """Print the stats of the last guess"""
        pass

    def get_next_guess(self, pool, guesses_indx):
        last_letter = chr(ord("A") + self.nb_colors - 1)
        guess = input(f"Enter your guess (between A and {last_letter}): ").upper()
        while len(guess) != 4 or not all(
            ord(c) in range(ord("A"), ord("A") + self.nb_colors) for c in guess
        ):
            guess = input(
                f"Invalid guess. Enter your guess (between A and {last_letter}): "
            ).upper()

        return guess, 1 / len(pool)
