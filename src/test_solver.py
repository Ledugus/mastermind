import unittest
from solvers import EntropicSolver, MastermindSolver, RandomSolver


class TestEntropicSolver(unittest.TestCase):
    def setUp(self) -> None:
        self.test_solvers: list[MastermindSolver] = [EntropicSolver(), RandomSolver()]
        return super().setUp()

    def test_find_best_guess(self):
        pool = ["AAAA", "AAAB", "AABB", "ABBB", "BBBB"]
        for solver in self.test_solvers:
            guess, entropy = solver.find_best_guess(pool, 4)
            self.assertIn(guess, pool)
            self.assertIsInstance(entropy, float)
            self.assertGreaterEqual(entropy, 0)

    def test_solve(self):
        for solver in self.test_solvers:
            results = solver.solve_all_codes(2)
            self.assertEqual(len(results), 16)
            for res in results:
                self.assertIsInstance(res, tuple)
                self.assertEqual(len(res), 3)
                self.assertGreater(8, len(res[1]))


if __name__ == "__main__":
    unittest.main()
