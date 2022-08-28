import json
from copy import deepcopy
from pathlib import Path

import numpy as np

from src.server import Server
from src.iteration import Iteration


class System:

    def __init__(self, template_path):
        with open(Path(template_path), "r") as template_file:
            template_dict = json.load(template_file)

        self._name = template_dict.get("name", "default_system")
        self._mul_min = template_dict.get("multiplication_min", 1)
        self._mul_max = template_dict.get("multiplication_max", 2)
        self._multiplication = range(self._mul_min, self._mul_max + 1)
        self._percentiles = template_dict.get("percentiles", [])
        self._servers = [Server(**server) for server in template_dict.get("servers", [])]
        self._probability_matrix_core = np.array(template_dict.get("probability_matrix_core", []))

        self._alpha_max = {}
        self.iterations = {}

    @property
    def name(self):
        return self._name

    @property
    def multiplication(self):
        return self._multiplication

    @property
    def percentiles(self):
        return self._percentiles

    @property
    def servers(self):
        return self._servers

    @property
    def alpha_max(self):
        return self._alpha_max

    @property
    def server_names(self):
        return [server.name for server in self._servers]

    @property
    def mis(self):
        return [server.mi for server in self._servers]

    @property
    def ss(self):
        return [server.s for server in self._servers]

    def gen_probability_matrix(self, k=None):
        k_array = k if k else self.multiplication

        for k in k_array:
            matrix = deepcopy(self._probability_matrix_core)

            for _ in range(k):
                # add columns
                matrix = np.append(matrix, [[round(0.5 / k, 2)]] * 4, 1)

            for _ in range(k):
                # add rows
                matrix = np.append(matrix, [(k + 4) * [0]], 0)

            yield matrix, k

    def gen_alpha_vector(self, alpha, k):
        for r in self.percentiles:
            alpha_vector = np.array([[alpha * r]] + (k + 3) * [[0]])
            yield alpha_vector, f"{int(r * 100)}%"

    def s_matrix(self, k):
        return np.diag(self.ss[0:k+4])

    def get_iteration(self, name=None, k=None, a=None):
        if not (name or k and list(a)):
            raise AttributeError("'name' or 'k' and 'a_vector' must be provided.")

        iter_name = name if name else Iteration.get_iteration_name(k, a)
        return self.iterations.get(iter_name)
