import argparse
from pathlib import Path
from copy import deepcopy

import numpy as np


def _error(msg, curr_val):
    print(f"{msg} Trenutna vrednost: '{curr_val}'. Vidi -h / --help za vise informacija.")
    exit()


def _parse_args():
    # implementiraj verobise -v, koji ce da printa svaku matricu i svaki korak
    parser = argparse.ArgumentParser(description="Izracunavanje sistema otvorene mreze.")
    parser.add_argument("-m", "--mod", dest="mod", required=True,
                        help="Pokrece zeljeni mod, moguce opcije: analiticki, stacionarni, simulacija. "
                             "Primer: $ python om.py -m simluacija",
                        )
    parser.add_argument("-a", "--alfa", dest="alfa", required=True, type=int,
                        help="Vrednost ulaznog toka - alfa.",
                        )

    # parser.add_argument("-k", "--korisnicki-diskovi", dest="k", required=True, type=int,
    #                     help="Broj korisnickih diskova, min 2, max 5.",
    #                     )

    # args = parser.parse_args(["-m", "analiticki", "-a", "8"])
    args = parser.parse_args()

    if args.mod not in ["analiticki", "simulacija", "stacionarni"]:
        _error("error: Mod rada mora biti 'analiticki' ili 'simulacija'.", args.mod)

    if args.alfa < 1:
        _error("error: Vrednost ulaznog toka mora biti pozitivan broj.", args.alfa)

    # if args.k not in [2, 3, 4, 5]:
    #     _error("error: Broj korisnickih diskova mora biti minimalno 2 i maksimalno 5.", args.k)

    return args


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

        yield np.array(matrix), k


def _get_alpha_vector_percents(alfa, k, percents):
    for r in percents:
        a = alfa * r
        yield [a] + (k + 3) * [0], a, f"{int(r * 100)}%"


def _get_alpha_vector_from_range(alpha_range, k):
    for alpha in alpha_range:
        yield [alpha / 100] + (k + 3) * [0], alpha / 100


def _matrix_to_vector(matrix):
    return [round(row[0], 2) for row in matrix]


def _get_average_vector(lambdas_list, k):
    average_vector = []
    axis = k + 4
    for index in range(axis):
        lam_sum = 0
        for lambda_vector in lambdas_list:
            lam_sum += lambda_vector[index]
        average_vector.append(round(lam_sum / 100, 2))

    return average_vector


def _save_to_file(file_name, content):
    path = Path(__file__).parent / "output" / file_name
    with open(path, "w") as outfile:
        outfile.write(content)
    print(f"Upisan fajl: {path}")


def analytics(**kwargs):
    alfa = kwargs.pop("alfa")
    r = kwargs.pop("r")
    content = f"protok kroz servere u funkciji od alfa: {alfa}\n"

    for p_matrix, k in _get_probability_matrix():
        content += f"\n> K: {k}\n"
        for a_vector, a, percent in _get_alpha_vector_percents(alfa, k, r):
            pt_matrix = p_matrix.transpose()
            i_matrix = np.diag((k + 4) * [1])
            i_minus_pt = i_matrix - pt_matrix
            lam = _matrix_to_vector(np.linalg.inv(i_minus_pt) * a_vector)
            content += f"[{percent}] {a}:\t{lam}\n"

    _save_to_file("protoci_analiticki", content)


def simulation_100(**kwargs):
    alfa = kwargs.pop("alfa")
    r = kwargs.pop("r")
    reps = 100
    content = f"simulacija usrednjenih vrednosti od 100 ponavljanja za alfa: {alfa}\n\n"

    for p_matrix, k in _get_probability_matrix():
        for a_vector, a, percent in _get_alpha_vector_percents(alfa, k, r):
            lambdas_list = []
            for _ in range(reps):
                pt_matrix = p_matrix.transpose()
                i_matrix = np.diag((k + 4) * [1])
                i_minus_pt = i_matrix - pt_matrix
                lambdas_list.append(_matrix_to_vector(np.linalg.inv(i_minus_pt) * a_vector))
            avg_lambda = _get_average_vector(lambdas_list, k)
            content += f"({k}, {a}):\t{avg_lambda}\n"

    _save_to_file("rezultati_simulacija_usrednjeno", content)


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
            lam = _matrix_to_vector(np.linalg.inv(i_minus_pt) * a_vector)
            out = round(lam[-1] * k, 1)
            content += f"{a}\t{out}\t{round(out - a, 1)}\n"

        _save_to_file(f"stacionarni_rezim_{k}", content)


if __name__ == '__main__':
    mods = {
        "analiticki": analytics,
        "simulacija": simulation_100,
        "stacionarni": stationary,
    }

    r = [0.25, 0.5, 0.77, 0.99]

    input_args = _parse_args()
    mods.get(input_args.mod)(alfa=input_args.alfa, r=r)
