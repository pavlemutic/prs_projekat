import numpy as np
from pathlib import Path


def calculate_lambda(a_vector, p_matrix, k):
    pt_matrix = p_matrix.transpose()
    i_matrix = np.identity(k + 4)
    i_minus_pt = i_matrix - pt_matrix
    lam_matrix = np.matmul(np.linalg.inv(i_minus_pt), a_vector)
    return lam_matrix, vector_to_array(lam_matrix)


def vector_to_array(vector):
    return [round(row[0], 2) for row in vector]


def get_alpha_vector(alpha, k):
    return np.array([[alpha]] + (k + 3) * [[0]])


def get_alpha_vector_percents(alpha, percentiles, k):
    for r in percentiles:
        alpha_vector = get_alpha_vector(alpha * r, k)
        yield alpha_vector, f"{int(r * 100)}%"


def save_to_file(file_name, content):
    path = Path(__file__).parent.parent / "output" / file_name
    with open(path, "w") as outfile:
        outfile.write(content)
    print(f"Upisan fajl: {path}")
