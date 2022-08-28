from tabulate import tabulate
import numpy as np

from src.system import System
from src.iteration import Iteration
from src import helpers as hlp


def analytics_alpha_max():
    content = "Alfa Maks u zavisnosti od K, sa kriticnim resursom.\n\n"
    results = []

    for p_matrix, k in system.probability_matrix:
        alfa_max_last = 0

        for alpha in range(1, 1000):
            if system.alpha_max.get(k):
                break
            a_vector = hlp.get_alpha_vector(alpha, k)
            lam, _ = hlp.calculate_lambda(a_vector, p_matrix, k)
            for index, lam_item in enumerate(lam):
                if lam_item / system.mis[index] > 1:
                    system.alpha_max[k] = alfa_max_last
                    server_name = system.server_names[index]
                    results += [[k, alfa_max_last, server_name]]
                    break
            alfa_max_last = alpha

    content += tabulate(results, headers=["K", "Alfa Maks", "Kriticni resurs"])
    hlp.save_to_file("alfa_maks", content)


def analytics_lambdas():
    content = "Protok kroz servere u funkciji od alfa."

    for p_matrix, k in system.probability_matrix:
        results = []
        a_max = system.alpha_max.get(k)
        content += f"\n\nAlpha MAX: {a_max}\n"
        for a_vector, percent in system.alpha_vector(a_max, k):
            lam_vector, lam_array = hlp.calculate_lambda(a_vector, p_matrix, k)
            iter_name = Iteration.get_iteration_name(k, a_vector)
            iteration = Iteration(name=iter_name, lambdas=lam_vector)
            iteration.ro = [lam / mi for lam, mi in zip(lam_array, system.mis)]
            system.iterations[iter_name] = iteration

            results += [[f"[{percent}] {iter_name}"] + lam_array]

        content += tabulate(results,
                            headers=["%, K, Alpha"] + system.server_names[0:k + 4])

    hlp.save_to_file("protoci_analiticki", content)


def analytics_jackson():
    # U, J, T
    content = "Iskoriscenja resursa, prosecan broj poslova u svakom resursu i vreme odziva."

    for p_matrix, k in system.probability_matrix:
        results = []
        a_max = system.alpha_max.get(k)
        content += f"\n\nAlpha MAX: {a_max}\n"
        for a_vector, percent in system.alpha_vector(a_max, k):
            iter_name = Iteration.get_iteration_name(k, a_vector)
            iteration = system.iterations.get(iter_name)

            iteration.u = np.matmul(system.s_matrix(k), iteration.lambdas)
            iteration.j = list(map(lambda ro: ro / (1 - ro), iteration.ro))
            iteration.r = [j / x for j, x in zip(iteration.j, list(iteration.lambdas))]

            results += [[iter_name, "U"] + hlp.vector_to_array(iteration.u)]
            results += [[iter_name, "J"] + iteration.j]
            results += [[iter_name, "RO"] + iteration.ro]
            results += [[iter_name, "R"] + iteration.r]

        content += tabulate(results, headers=["K, Alpha", "Metric"] + system.server_names[0:k + 4])

    hlp.save_to_file("rezultati_analiticki", content)


if __name__ == '__main__':
    system = System(template_path="system_template.json")

    # for server in system.servers:
    #     print(server)

    analytics_alpha_max()
    analytics_lambdas()
    analytics_jackson()
