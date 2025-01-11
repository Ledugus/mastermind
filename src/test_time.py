from time import time
from solvers import EntropicSolver
from utils import get_all_codes, evaluate_patterns, evaluate_pattern_matrix


def test_time_pattern_evaluation():
    t0 = time()
    evaluate_patterns(get_all_codes(8))
    print("Naïve method", time() - t0)
    t0 = time()
    evaluate_pattern_matrix(get_all_codes(8))
    print("Vectorized method", time() - t0)


def test_entropy_calculation(nb_colors=3):
    solver = EntropicSolver()
    t0 = time()

    for code in get_all_codes(nb_colors):
        solver.expected_information(code, get_all_codes(nb_colors))
    print("Loop solution", time() - t0)
    t0 = time()
    solver.get_entropy(
        solver.get_patterns_probability_distribution_matrix(get_all_codes(nb_colors))
    )
    print("Vectorized solution", time() - t0)


def test_solve_time(nb_colors=4):
    solver = EntropicSolver()
    t0 = time()
    solver.solve_all_codes(nb_colors, parallel=False)
    print(time() - t0)
    t0 = time()
    solver.solve_all_codes(nb_colors)
    print(time() - t0)


def correctness_parallel_solve():
    solver = EntropicSolver()
    results = solver.solve_all_codes(3, parallel=False)
    results_parallel = solver.solve_all_codes(3)
    for res, res_parallel in zip(results, results_parallel[:10]):
        print(res[0], res_parallel[0])
        print(res[1], res_parallel[1])
        print()


test_solve_time()
