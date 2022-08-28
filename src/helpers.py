import numpy as np


def calculate_lambda(a_vector, p_matrix, k):
    pt_matrix = p_matrix.transpose()
    i_matrix = np.identity(k + 4)
    i_minus_pt = i_matrix - pt_matrix
    lam_vector = np.matmul(np.linalg.inv(i_minus_pt), a_vector)
    return lam_vector, vector_to_array(lam_vector)


def vector_to_array(vector):
    return [round(row[0], 2) for row in vector]



