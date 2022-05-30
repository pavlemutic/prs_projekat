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
                        help="Pokrece zeljeni mod, moguce opcije: analiticki, simulacija. "
                             "Primer: $ python om.py -m simluacija",
                        )
    parser.add_argument("-a", "--alfa", dest="alfa", required=True, type=int,
                        help="Vrednost ulaznog toka - alfa.",
                        )

    # parser.add_argument("-k", "--korisnicki-diskovi", dest="k", required=True, type=int,
    #                     help="Broj korisnickih diskova, min 2, max 5.",
    #                     )

    args = parser.parse_args(["-m", "analiticki", "-a", "8"])
    # args = parser.parse_args()

    if args.mod not in ["analiticki", "simulacija"]:
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


def _get_alpha(alfa, k):
    for r in [0.25, 0.5, 0.77, 0.99]:
        a = alfa * r
        yield [a] + (k + 3) * [0], a


def _get_i_matrix(k):
    axis = k + 4
    matrix = []
    for a in range(axis):
        matrix.append([1 if a == b else 0 for b in range(axis)])
    return np.array(matrix)


def _matrix_to_vector(matrix):
    return [round(row[0], 2) for row in matrix]


def _save_to_file(file_name, content):
    path = Path(__file__).parent / "output" / file_name
    with open(path, "w") as outfile:
        outfile.write(content)
    print(f"Upisan fajl: {path}")


def analytics(alfa):
    content = f"protok kroz servere u funkciji od alfa: {alfa}\n"

    for p_matrix, k in _get_probability_matrix():
        content += f"\n> K: {k}\n"
        for a_vector, a in _get_alpha(alfa, k):
            pt_matrix = p_matrix.transpose()
            i_matrix = _get_i_matrix(k)
            i_minus_pt = i_matrix - pt_matrix
            lam = _matrix_to_vector(np.linalg.inv(i_minus_pt) * a_vector)
            content += f"{a}:\t{lam}\n"

    _save_to_file("protoci_analiticki", content)


def simulation(alfa):
    print("simulation")


def _main():
    mods = {
        "analiticki": analytics,
        "simulacija": simulation,
    }

    args = _parse_args()
    mods.get(args.mod)(args.alfa)


if __name__ == '__main__':
    _main()
