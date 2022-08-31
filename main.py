from pathlib import Path
from datetime import datetime

from tabulate import tabulate
import numpy as np
import matplotlib.pyplot as plt

from src.system import System
from src.iteration import Iteration
from src.simulator import Simulator
from src import helpers as hlp


def _output_file():
    return Path(__file__).parent / "output"


def save_to_file(file_name, content):
    path = _output_file() / "files" / file_name
    with open(path, "w") as outfile:
        outfile.write(content)
    print(f"Upisan fajl: {path}")


def save_figure(data):
    plt.plot(data.get("k"), data.get("a"))
    plt.title('A-max(K)')
    plt.xlabel('K')
    plt.ylabel('A-max')
    path = _output_file() / "figures" / "graph_a-max_k.png"
    plt.savefig(path)


def analytics_alpha_max():
    content = "Alfa Maks u zavisnosti od K, sa kriticnim resursom.\n\n"
    results = []
    graph = {"a": [], "k": []}

    for p_matrix, k in system.gen_probability_matrix():
        alfa_max_last = 0

        for alpha in range(1, 1000):
            if system.alpha_max.get(k):
                break
            a_vector = np.array([[alpha]] + (k + 3) * [[0]])
            lam, _ = hlp.calculate_lambda(a_vector, p_matrix, k)
            for index, lam_item in enumerate(lam):
                if lam_item / system.mis[index] > 1:
                    system.alpha_max[k] = alfa_max_last
                    server_name = system.server_names[index]
                    results += [[k, alfa_max_last, server_name]]
                    graph["a"].append(alfa_max_last)
                    graph["k"].append(k)
                    break
            alfa_max_last = alpha

    content += tabulate(results, headers=["K", "Alfa Maks", "Kriticni resurs"])
    save_to_file("alfa_maks", content)
    save_figure(graph)


def analytics_lambdas():
    content = "Protok kroz servere u funkciji od alfa."

    for p_matrix, k in system.gen_probability_matrix():
        results = []
        a_max = system.alpha_max.get(k)
        content += f"\n\nAlpha MAX: {a_max}\n"

        for row_line, row in enumerate(p_matrix):
            server = system.get_server_by_id(row_line)
            server.next_servers[k] = {a: b for a, b in zip(system.server_names[:k + 4], row)}

        for a_vector, percent in system.gen_alpha_vector(a_max, k):
            lam_vector, lam_array = hlp.calculate_lambda(a_vector, p_matrix, k)
            iteration = Iteration(k=k, a_vector=a_vector)
            iteration.lam = lam_vector
            iteration.ro = np.array([lam / mi for lam, mi in zip(lam_array, system.mis)])
            system.iterations[iteration.name] = iteration

            results += [[f"[{percent}] {iteration.name}"] + lam_array]

        headers = ["%, K, Alpha"] + system.server_names[:k + 4]
        content += tabulate(results, headers=headers)

    save_to_file("protoci_analiticki", content)


def analytics_jackson():
    content = "Iskoriscenja resursa, prosecan broj poslova u svakom resursu i vreme odziva."

    for p_matrix, k in system.gen_probability_matrix():
        results = []
        a_max = system.alpha_max.get(k)
        content += f"\n\nAlpha MAX: {a_max}\n"
        for a_vector, percent in system.gen_alpha_vector(a_max, k):
            iteration = system.get_iteration(k=k, a=a_vector)
            iteration.u = np.matmul(system.s_matrix(k), iteration.lam)
            iteration.j = np.array(list(map(lambda ro: ro / (1 - ro), iteration.ro_array)))
            iteration.r = [j / x for j, x in zip(iteration.j_array, iteration.lam_array)]

            results += [[iteration.name, "MI"] + system.mis[:k + 4]]
            results += [[iteration.name, "S"] + system.ss[:k + 4]]
            results += [[iteration.name, "LAM"] + iteration.lam_array]
            results += [[iteration.name, "RO"] + iteration.ro_array]
            results += [[iteration.name, "U"] + iteration.u_array]
            results += [[iteration.name, "J"] + iteration.j_array]
            results += [[iteration.name, "R(s)"] + iteration.r_array]
            results += [[]]

        headers = ["K, Alpha", "Metric"] + system.server_names[:k + 4]
        content += tabulate(results, headers=headers)

    save_to_file("rezultati_analiticki", content)


def simulation(simulation_time=1800, repeats=1):
    content = f"Simulacija u trajanju od {round(simulation_time / 3600, 2)}h i {repeats} ponavljanja."
    simulator = Simulator(system)
    start_time = datetime.now()

    for p_matrix, k in system.gen_probability_matrix():
        results = []
        system.k = k
        a_max = system.alpha_max.get(k)
        content += f"\n\nAlpha MAX: {a_max}\n"
        for r in system.percentiles:
            alpha = a_max * r
            for _ in range(repeats):
                simulator.start(alpha=alpha, simulation_time=simulation_time)
            results += simulator.get_results(alpha)
            results += [[]]

        headers = ["K, Alpha", "Metric"] + system.server_names[:k + 4]
        content += tabulate(results, headers=headers)

    save_to_file(f"rezultati_simulacija_{repeats}x", content)
    print(f"Simulation time: {datetime.now() - start_time}")


if __name__ == '__main__':
    system = System(template_path="system_template.json")

    analytics_alpha_max()
    analytics_lambdas()
    analytics_jackson()

    # simulation()
    simulation(repeats=3)
