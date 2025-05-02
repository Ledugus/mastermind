import random
import unittest
from solvers import EntropicSolver, MastermindSolver, RandomSolver, KnuthMinMaxSolver
from utils import get_all_codes

NB_COLORS = 2


class TestEntropicSolver(unittest.TestCase):
    def setUp(self) -> None:
        self.test_solvers: list[MastermindSolver] = [
            EntropicSolver(NB_COLORS),
            RandomSolver(NB_COLORS),
        ]
        return super().setUp()

    def test_find_best_guess(self):
        pool = ["AAAA", "AAAB", "AABB", "ABBB", "BBBB"]
        for solver in self.test_solvers:
            guess, score = solver.get_next_guess(pool)
            self.assertIn(guess, pool)
            self.assertGreaterEqual(score, 0)

    def test_solve(self):
        for solver in self.test_solvers:
            results = solver.solve_all_codes()
            self.assertEqual(len(results), 16)
            for res in results:
                self.assertIsInstance(res, tuple)
                self.assertEqual(len(res), 3)
                self.assertGreater(8, len(res[1]))

    def test_knuth_min_max_solver(self):
        nb_colors = 6
        solver = KnuthMinMaxSolver(nb_colors)
        full_pool = get_all_codes(nb_colors)
        results = solver.solve_all_codes()
        self.assertEqual(len(results), nb_colors**4)
        for res in results:
            self.assertIsInstance(res, tuple)
            self.assertEqual(len(res), 3)
            self.assertGreaterEqual(5, len(res[1]))


if __name__ == "__main__":
    unittest.main()
