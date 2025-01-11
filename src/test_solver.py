import unittest
from solvers import EntropicSolver


class TestEntropicSolver(unittest.TestCase):
    def setUp(self) -> None:
        self.test_solver = EntropicSolver()
        return super().setUp()

    def test_init(self):
        self.assertTrue(self.test_solver.first_guesses)

    def test_find_best_guess(self):
        pool = ["AAAA", "AAAB", "AABB", "ABBB", "BBBB"]
        guess, entropy = self.test_solver.find_best_guess(pool, 4)
        self.assertIn(guess, pool)
        self.assertIsInstance(entropy, float)
        self.assertGreater(entropy, 0)


if __name__ == "__main__":
    unittest.main()
