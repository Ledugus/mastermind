import matplotlib.pyplot as plt
import mastermind_simul_v2 as v2
import mastermind_simul_v3 as v3


def get_guesses_distribution(nb_colors):
    liste = [0]*8
    pool = v2.get_all_combinations(nb_colors)
    for x in pool:
        liste[v3.play_game(nb_colors, pool, set_secret=True, secret=x)] += 1
    total = 0
    for y in range(8):
        total += y*liste[y]
    print("Mean: ", total/len(pool))
    plt.bar(range(1, 8), liste[1:8])
    plt.ylabel('Number of occurences')
    plt.xlabel('Number of guesses needed')
    plt.savefig(f"nb_of_guesses_{nb_colors}_colors.png")


get_guesses_distribution(7)
