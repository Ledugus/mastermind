import random
import time
import matplotlib.pyplot as plt
from solvers import EntropicSolver, RandomSolver, KnuthMinMaxSolver

NB_COLORS = 5


def get_stats(solver):
    """Get the stats of a solver"""
    a = time.time()
    results = solver.solve_all_codes()
    b = time.time()

    total_time = b - a
    total_guesses = 0
    guesses_distribution = [0] * 12

    for res in results:
        total_guesses += len(res[1])
        if len(res[1]) < 12:
            guesses_distribution[len(res[1])] += 1
        else:
            guesses_distribution[11] += 1
    avg_guesses = total_guesses / len(results)
    return guesses_distribution, avg_guesses, total_time


def main():
    """Main function to test the solvers"""
    solvers = [
        EntropicSolver(NB_COLORS),
        EntropicSolver(NB_COLORS, True),
        RandomSolver(NB_COLORS),
        KnuthMinMaxSolver(NB_COLORS),
    ]
    for solver in solvers:
        guesses_distribution, avg_guesses, total_time = get_stats(solver)
        print(
            f"{solver.name} took {total_time:.2f} seconds and made {avg_guesses:.2f} guesses on average"
        )
        plt.bar(list(range(1, 13)), guesses_distribution, label=solver.name)
        plt.title(f"Guesses distribution : {solver.name} ({NB_COLORS} colors)")
        plt.xlabel("Number of guesses")
        plt.ylabel("Number of codes")
        plt.legend()
        plt.savefig(f"charts/guesses_distribution_{solver.alias}.png")
        plt.show()


if __name__ == "__main__":
    main()
