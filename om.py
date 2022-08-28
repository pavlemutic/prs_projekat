import argparse
from pathlib import Path
from copy import deepcopy

import numpy as np

verbose = False


def _error(msg, curr_val):
    print(f"{msg} Trenutna vrednost: '{curr_val}'. Vidi -h / --help za vise informacija.")
    exit()


def _parse_args():
    parser = argparse.ArgumentParser(description="Izracunavanje sistema otvorene mreze.")
    parser.add_argument("-m", "--mod", dest="mod", required=True,
                        help="Pokrece zeljeni mod, moguce opcije: analiticki, stacionarni, simulacija. "
                             "Primer: $ python om.py -m simluacija",
                        )
    parser.add_argument("-a", "--alfa", dest="alfa", required=True, type=int,
                        help="Vrednost ulaznog toka - alfa.",
                        )

    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                        help="Rezim rada za lakse debagovanje, svaki korak se ispisuje na izlaz.")

    # args = parser.parse_args(["-m", "analiticki", "-a", "8"])
    args = parser.parse_args()

    if args.mod not in ["alfas", "analiticki", "simulacija", "stacionarni"]:
        _error("error: Mod rada mora biti 'analiticki' ili 'simulacija'.", args.mod)

    if args.alfa < 1:
        _error("error: Vrednost ulaznog toka mora biti pozitivan broj.", args.alfa)

    return args


def _verbose_out(content):
    if verbose:
        print(content)


def _get_probability_matrix():
    core_matrix = [
        [0.2, 0.15, 0.1, 0.05],
        [0.3, 0.2, 0, 0],
        [0.3, 0, 0.2, 0],
        [0.3, 0, 0, 0.2]
    ]

    for k in [2, 3, 4, 5]:
        matrix = deepcopy(core_matrix)
        for row in matrix:
            row.extend(k * [round(0.5 / k, 2)])

        for _ in range(k):
            matrix.append((k + 4) * [0])

        _verbose_out(f"matrica verovatnoca:\n{matrix}")
        yield np.array(matrix), k


def _get_alpha_vector_percents(alfa, k, percents):
    for r in percents:
        a = alfa * r
        alpha_vector = [[a]] + (k + 3) * [[0]]
        _verbose_out(f"alfa vektor:\n{alpha_vector}")
        yield alpha_vector, a, f"{int(r * 100)}%"


def _get_alpha_vector_from_range(alpha_range, k):
    for alpha in alpha_range:
        yield [alpha / 100] + (k + 3) * [0], alpha / 100


def _vector_to_array(vector):
    return [round(row[0], 2) for row in vector]


def _get_average_vector(lambdas_list, k):
    average_vector = []
    axis = k + 4
    for index in range(axis):
        lam_sum = 0
        for lambda_vector in lambdas_list:
            lam_sum += lambda_vector[index]
        average_vector.append(round(lam_sum / 100, 2))

    return average_vector


def _save_to_file(file_name, content, *args, **kwargs):
    path = Path(__file__).parent / "output" / file_name
    with open(path, "w") as outfile:
        outfile.write(content)
    print(f"Upisan fajl: {path}")


def get_lambda(alfa, k, p_matrix):
    a_vector = [alfa] + (k + 3) * [0]
    pt_matrix = p_matrix.transpose()
    i_matrix = np.diag((k + 4) * [1])
    i_minus_pt = i_matrix - pt_matrix
    return _vector_to_array(np.linalg.inv(i_minus_pt) * a_vector)


def alfas(*args, **kwargs):
    mis = [200, 100, 66.67, 66.67, 40, 40, 40, 40, 40]
    servers = ["p", "d1", "d2", "d3", "k1", "k2", "k3", "k4", "k5"]
    content = f"nalazenje alfe_o\n"
    
    for p_matrix, k in _get_probability_matrix():
        content += f"\nK: {k}\n"
        alfa_max_last = 0

        alfa_found = False
        for alfa in range(1, 1000):
            if not alfa_found:
                alfa_max_current = alfa
                lam = get_lambda(alfa_max_current, k, p_matrix)

                for index, lam_item in enumerate(lam):
                    if lam_item / mis[index] > 1:
                        alfa_found = True
                        content += f"alfa max: {alfa_max_last}\n"
                        lam_last = get_lambda(alfa_max_last, k, p_matrix)
                        ro = lam_last[index] / mis[index]
                        content += f"kritican: {servers[index]}, ro: {ro}\n"

                        content += f"poslednji:\n"
                        content += f"alfa: {alfa_max_current}, ro: {lam_item / mis[index]}\n"
                        break
                
                alfa_max_last = alfa_max_current

    _save_to_file("alfe_o", content)


def analytics(**kwargs):
    alfa = kwargs.pop("alfa")
    r = kwargs.pop("r")
    content = f"protok kroz servere u funkciji od alfa: {alfa}\n"

    for p_matrix, k in _get_probability_matrix():
        content += f"\n> K: {k}\n"
        for a_vector, a, percent in _get_alpha_vector_percents(alfa, k, r):
            pt_matrix = p_matrix.transpose()
            i_matrix = np.identity(k + 4)
            i_minus_pt = i_matrix - pt_matrix
            lam_matrix = np.matmul(np.linalg.inv(i_minus_pt), a_vector)
            lam = _vector_to_array(lam_matrix)
            content += f"[{percent}] {a}:\t{lam}\n"
            _verbose_out(f"k: {k}, alfa: {a}, lambda: {lam}")

    _save_to_file("protoci_analiticki", content)


def simulation_100(**kwargs):
    pass


def stationary(**kwargs):
    min_alfa = 1 * 100
    max_alfa = kwargs.pop("alfa") * 100
    inc = int(0.1 * 100)

    for p_matrix, k in _get_probability_matrix():
        content = "alpha\tout\tdiff\n"
        for a_vector, a in _get_alpha_vector_from_range(range(min_alfa, max_alfa, inc), k):
            pt_matrix = p_matrix.transpose()
            i_matrix = np.diag((k + 4) * [1])
            i_minus_pt = i_matrix - pt_matrix
            lam = _vector_to_array(np.linalg.inv(i_minus_pt) * a_vector)
            out = round(lam[-1] * k, 1)
            content += f"{a}\t{out}\t{round(out - a, 1)}\n"

        _save_to_file(f"stacionarni_rezim_{k}", content)


if __name__ == '__main__':
    mods = {
        "alfas": alfas,
        "analiticki": analytics,
        "simulacija": simulation_100,
        "stacionarni": stationary,
    }

    r = [0.25, 0.5, 0.77, 0.99, 1]

    input_args = _parse_args()
    verbose = input_args.verbose
    mods.get(input_args.mod)(alfa=input_args.alfa, r=r)
