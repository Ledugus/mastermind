import random
import json
from abc import ABC, abstractmethod

import numpy as np
import scipy.stats as stats
from utils import (
    log2,
    get_all_codes,
    get_all_codes_matching_pattern,
    pattern_int_to_list,
    evaluate_pattern,
    get_clean_feedback,
    evaluate_pattern_matrix,
)


class MastermindSolver(ABC):
    """Abstract class for a Mastermind solver"""

    def __init__(self, name, alias):
        self.name = name
        self.alias = alias

    @abstractmethod
    def get_next_guess(self, pool, nb_colors, parallel=True) -> tuple[str, float]:
        """Return the best guess to make in the pool of possibilities
        and the expected information in the case of the Entropic Solver"""

    def solve(
        self,
        nb_colors,
        custom_pool=[],
        alone=True,
        secret=None,
        debug=False,
        parallel=True,
    ):
        """Solve the game Mastermind with a given number of colors.

        Args:
            nb_colors (int): The number of possible colors in the game.
            custom_pool (list, optional): A list of all possible codes. Defaults to [].
            alone (bool, optional): If True, the function will generate a secret code and play against it. Defaults to True.
            set_secret (bool, optional): If True, the function will use the secret code given in the secret argument. Defaults to False.
            secret (str, optional): The secret code to use if set_secret is True. Defaults to None.
            debug (bool, optional): If True, the function will print debug information. Defaults to False.


        Returns:
            tuple: A tuple containing the secret code, the list of guesses and the list of entropy values.
        """
        current_pool = custom_pool if custom_pool else get_all_codes(nb_colors)
        if alone:
            secret_code = secret if secret else random.choice(current_pool)
        correct = False
        guesses = []
        entropy_values = []
        while not correct:
            results = self.get_next_guess(current_pool, nb_colors, parallel=parallel)
            if alone:
                pattern = evaluate_pattern(results[0], secret_code)
            else:
                pattern = get_clean_feedback()
            current_guess = results[0]
            guesses.append(current_guess)
            entropy_values.append(results[1])
            new_pool = get_all_codes_matching_pattern(
                current_guess, pattern, current_pool
            )
            if debug or not alone:
                print(f"Guess n°{len(guesses)} : {current_guess}")
                print(
                    f"FeedBack : , {pattern_int_to_list(pattern)[0]} well placed, {pattern_int_to_list(pattern)[1]} misplaced"
                )
                print(f"Expected information : {results[1]} bits")
                print(
                    f"Actual information received : {log2(len(current_pool) / len(new_pool))} bits, {len(new_pool)} remaining possibilities"
                )
            current_pool = new_pool

            if pattern == 20:
                correct = True
        return secret_code, guesses, entropy_values

    def solve_all_codes(self, nb_colors, parallel=True):
        """Solve the game Mastermind with a given number of colors for all possible secret codes.
        Return a list of the result of each solve."""
        pool = get_all_codes(nb_colors)
        return [
            self.solve(
                nb_colors,
                custom_pool=pool,
                secret=code,
                debug=False,
                parallel=parallel,
            )
            for code in pool
        ]


class EntropicSolver(MastermindSolver):
    """A Mastermind solver based on maximising the entropy of the guess"""

    def __init__(self):
        super().__init__("Entropic Solver", "entr")
        self.first_guesses = self.load_first_guesses()

    def load_first_guesses(self):
        with open("src/entropic_first_guesses.json", "r") as f:
            first_guesses_dict = json.load(f)
        return first_guesses_dict

    def get_first_guess(self, nb_colors):
        return self.first_guesses[str(nb_colors)]

    def save_first_guess(self, nb_colors, guess, information_got):
        with open("src/entropic_first_guesses.json", "r") as f:
            first_guesses_dict = json.load(f)
            first_guesses_dict[str(nb_colors)] = (guess, information_got)
        with open("src/entropic_first_guesses.json", "w") as f:
            json.dump(first_guesses_dict, f)

    def get_patterns_probability_distribution(self, code, pool):
        """Return for each pattern the number of codes that get it as feedback
        when testing against all possibilities in the pool"""
        distribution = np.zeros(41, dtype=np.uint16)
        for x in pool:
            distribution[evaluate_pattern(code, x)] += 1
        return distribution / len(pool)

    def expected_information(self, code, pool):
        """Sum for all patterns the entropy formula (exception if nb_patterns = 0)
        Return a number, the average information in bits that the code would get as guess
        """

        patterns_probability_distribution = self.get_patterns_probability_distribution(
            code, pool
        )
        expected_information_of_code = sum(
            log2(1 / pattern_probability) * pattern_probability
            for pattern_probability in patterns_probability_distribution
            if pattern_probability != 0
        )
        return expected_information_of_code

    def find_best_guess_old(self, pool, nb_colors):
        """Return a tuple of 2 elements :
        1 : the string of the best guess
        2 : the entropy of this guess
        """
        ### if first guess, get it from the json file
        if len(pool) == nb_colors**4:
            if str(nb_colors) in self.first_guesses:
                results = self.get_first_guess(nb_colors)
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
        if len(pool) == nb_colors**4:
            self.save_first_guess(nb_colors, *results)
        return results

    def get_patterns_probability_distribution_matrix(self, pool):
        pattern_matrix = evaluate_pattern_matrix(pool)
        n = len(pool)
        distributions = np.zeros((n, 21), dtype=np.float32)
        n_range = np.arange(n)
        prob = 1 / n
        for j in range(n):
            distributions[n_range, pattern_matrix[:, j]] += prob
        return distributions

    def get_entropy(self, distributions):
        axis = len(distributions.shape) - 1
        return stats.entropy(distributions, base=2, axis=axis)

    def find_best_guess(self, pool, nb_colors):
        """Return a tuple of 2 elements :
        1 : the string of the best guess
        2 : the entropy of this guess
        """
        if len(pool) == nb_colors**4:
            if str(nb_colors) in self.first_guesses:
                results = self.get_first_guess(nb_colors)
                return results
        distributions = self.get_patterns_probability_distribution_matrix(pool)
        entropies = self.get_entropy(distributions)
        results = pool[np.argmax(entropies)], float(np.max(entropies))
        if len(pool) == nb_colors**4:
            self.save_first_guess(nb_colors, *results)
        return results

    def get_next_guess(self, pool, nb_colors, parallel=True):
        if parallel:
            return self.find_best_guess(pool, nb_colors)
        return self.find_best_guess_old(pool, nb_colors)


class RandomSolver(MastermindSolver):
    """A Mastermind solver based on random guesses"""

    def __init__(self):
        super().__init__("Random Solver", "rand")

    def get_next_guess(self, pool, nb_colors, parallel=True):
        return random.choice(pool), 0.0
