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
    def get_next_guess(self, pool, parallel=True) -> tuple[str, float]:
        """Return the best guess to make in the pool of possibilities
        and the score assigned to this guess by the solver."""

    @abstractmethod
    def print_guess_stats(self, result, current_pool, new_pool):
        """Print the stats of the last guess"""

    def load_first_guesses(self):
        with open(f"src/{self.alias}_first_guesses.json", "r") as f:
            first_guesses_dict = json.load(f)
        return first_guesses_dict

    def get_first_guess(self):
        return self.first_guesses[str(self.nb_colors)]

    def save_first_guess(self, guess, information_got):
        with open(f"src/{self.alias}_first_guesses.json", "r") as f:
            first_guesses_dict = json.load(f)
            first_guesses_dict[str(self.nb_colors)] = (guess, information_got)
        with open(f"src/{self.alias}_first_guesses.json", "w") as f:
            json.dump(first_guesses_dict, f)

    def solve(
        self,
        custom_pool=[],
        alone=True,
        secret=None,
        debug=False,
        parallel=True,
    ):
        """Solve the game Mastermind with a given number of colors.

        Args:
            custom_pool (list, optional): A list of all possible codes. Defaults to [].
            alone (bool, optional): If True, the function will generate a secret code and play against it. Defaults to True.
            secret (str, optional): The secret code to use if set_secret is True. Defaults to None.
            debug (bool, optional): If True, the function will print debug information. Defaults to False.
            parallel (bool, optional): If True, the function will use parallel processing. Defaults to True.


        Returns:
            tuple: A tuple containing the secret code, the list of guesses and the list of guesses' scores.
        """
        current_pool = custom_pool if custom_pool else get_all_codes(self.nb_colors)
        if alone:
            secret_code = secret if secret else random.choice(current_pool)
            print(secret_code)
        correct = False
        guesses = []
        scores = []
        while not correct:
            # Make the next guess
            results = self.get_next_guess(current_pool, parallel=parallel)
            current_guess = results[0]
            guesses.append(current_guess)
            scores.append(results[1])

            if debug or not alone:
                print(f"Guess n°{len(guesses)} : {current_guess}")

            # Get the feedback
            if alone:
                pattern = evaluate_pattern(results[0], secret_code)
            else:
                pattern = get_clean_feedback()

            # Evaluate the feedback
            new_pool = get_all_codes_matching_pattern(
                current_guess, pattern, current_pool
            )
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
                self.print_guess_stats(results, current_pool, new_pool)
                print("-----")
            current_pool = new_pool

        return secret_code, guesses, scores

    def solve_all_codes(self, parallel=True):
        """Solve the game Mastermind for all possible secret codes.
        Return a list of the result of each solve."""
        pool = get_all_codes(self.nb_colors)
        return [
            self.solve(
                custom_pool=pool,
                secret=code,
                debug=False,
                parallel=parallel,
            )
            for code in pool
        ]


class EntropicSolver(MastermindSolver):
    """A Mastermind solver based on maximising the entropy of the guess"""

    def __init__(self, nb_colors):
        super().__init__("Entropic Solver", "entr", nb_colors)
        self.first_guesses = self.load_first_guesses()

    def expected_information(self, code, pool):
        """Sum for all patterns the entropy formula (exception if nb_patterns = 0)
        Return a number, the average information in bits that the code would get as guess
        """
        patterns_probability_distribution = get_patterns_probability_distribution(
            code, pool
        )
        expected_information_of_code = sum(
            log2(1 / pattern_probability) * pattern_probability
            for pattern_probability in patterns_probability_distribution
            if pattern_probability != 0
        )
        return expected_information_of_code

    def find_best_guess_old(self, pool):
        """Return a tuple of 2 elements :
        1 : the string of the best guess
        2 : the entropy of this guess
        """
        ### if first guess, get it from the json file
        if len(pool) == self.nb_colors**4:
            if str(self.nb_colors) in self.first_guesses:
                results = self.get_first_guess()
                return results

        max_entropy = -np.inf
        best_guess = ""
        for guess in pool:
            guess_entropy = self.expected_information(guess, pool)
            if guess_entropy >= max_entropy:
                best_guess = guess
                max_entropy = guess_entropy

        results = (best_guess, max_entropy)
        ### if new first guess, save it in the json file
        if len(pool) == self.nb_colors**4:
            self.save_first_guess(*results)
        return results

    def get_entropy(self, distributions):
        """Return the entropy of the distributions"""
        axis = len(distributions.shape) - 1
        return stats.entropy(distributions, base=2, axis=axis)

    def find_best_guess(self, pool):
        """Return a tuple of 2 elements :
        1 : the string of the best guess
        2 : the entropy of this guess
        """
        if len(pool) == self.nb_colors**4:
            if str(self.nb_colors) in self.first_guesses:
                results = self.get_first_guess()
                return results
            print("Calculating first guess... (takes longer the first time)")
        distributions = get_patterns_probability_distribution_matrix(pool)
        entropies = self.get_entropy(distributions)
        results = pool[np.argmax(entropies)], float(np.max(entropies))
        if len(pool) == self.nb_colors**4:
            self.save_first_guess(*results)
        return results

    def get_next_guess(self, pool, parallel=True):
        if parallel:
            return self.find_best_guess(pool)
        return self.find_best_guess_old(pool)

    def print_guess_stats(self, result, current_pool, new_pool):
        """Print the stats of the last guess"""
        print(f"Expected information : {result[1]:.3f} bits")
        print(
            f"Actual information received : {log2(len(current_pool) / len(new_pool)):.3f} bits, {len(new_pool)} remaining possibilities"
        )


class KnuthMinMaxSolver(MastermindSolver):
    """A Mastermind solver based on Knuth's MinMax algorithm"""

    def __init__(self, nb_colors):
        super().__init__("Knuth MinMax Solver", "knuth", nb_colors)
        self.first_guesses = self.load_first_guesses()

    def print_guess_stats(self, result, current_pool, new_pool):
        """Print the stats of the last guess"""
        print(f"Maximum number of possibilities remaining : {result[1]}")

    def get_next_guess(self, pool, parallel=True):
        if len(pool) == self.nb_colors**4:
            if str(self.nb_colors) in self.first_guesses:
                results = self.get_first_guess()
                return results
            print("Calculating first guess... (takes longer the first time)")
        if self.nb_colors == 1:
            return "AAAA", 1
        full_pool = get_all_codes(self.nb_colors)
        best_guess = full_pool[0]
        best_score = np.inf
        for guess_indx in range(self.nb_colors**4):
            distribution = np.zeros(21)
            for code in pool:

                distribution[
                    self.pattern_matrix[code_to_int(code, self.nb_colors), guess_indx]
                ] += 1
            max_pattern = np.max(distribution)
            if max_pattern < best_score:
                best_guess = guess_indx
                best_score = max_pattern
            elif (
                max_pattern == best_score
                and int_to_code(guess_indx, self.nb_colors) in pool
            ):
                best_guess = guess_indx
                best_score = max_pattern
        results = (int_to_code(guess_indx, self.nb_colors), best_score)
        if len(pool) == self.nb_colors**4:
            self.save_first_guess(*results)
        return results


class RandomSolver(MastermindSolver):
    """A Mastermind solver based on random guesses"""

    def __init__(self, nb_colors):
        super().__init__("Random Solver", "rand", nb_colors)

    def print_guess_stats(self, result, current_pool, new_pool):
        """Print the stats of the last guess"""
        pass

    def get_next_guess(self, pool, parallel=True):
        return random.choice(pool), 1 / len(pool)


class UserSolver(MastermindSolver):
    """A Mastermind solver based on user input"""

    def __init__(self, nb_colors):
        super().__init__("User Solver", "user", nb_colors)

    def print_guess_stats(self, result, current_pool, new_pool):
        """Print the stats of the last guess"""
        pass

    def get_next_guess(self, pool, parallel=True):
        last_letter = chr(ord("A") + self.nb_colors - 1)
        guess = input(f"Enter your guess (between A and {last_letter}): ").upper()
        while len(guess) != 4 or not all(
            ord(c) in range(ord("A"), ord("A") + self.nb_colors) for c in guess
        ):
            guess = input(
                f"Invalid guess. Enter your guess (between A and {last_letter}): "
            ).upper()

        return guess, 1 / len(pool)
