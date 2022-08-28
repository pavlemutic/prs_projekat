import json
from copy import deepcopy
from pathlib import Path

import numpy as np

from src.server import Server


class System:

    def __init__(self, template_path):
        with open(Path(template_path), "r") as template_file:
            template_dict = json.load(template_file)

        self._name = template_dict.get("name", "default_system")
        self._multiplication = template_dict.get("multiplication", [])
        self._percentiles = template_dict.get("percentiles", [])
        self._servers = [Server(**server) for server in template_dict.get("servers", [])]
        self._probability_matrix_core = np.array(template_dict.get("probability_matrix_core", []))

        self._probability_matrix = None
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
    def probability_matrix(self):
        for k in self.multiplication:
            matrix = deepcopy(self._probability_matrix_core)

            for _ in range(k):
                matrix = np.append(matrix, [[round(0.5 / k, 2)]] * 4, 1)

            for _ in range(k):
                matrix = np.append(matrix, [(k + 4) * [0]], 0)

            yield matrix, k

    @property
    def server_names(self):
        return [server.name for server in self._servers]

    @property
    def mis(self):
        return [server.mi for server in self._servers]

    def s_matrix(self, k):
        return np.diag([server.s for server in self._servers][0:k+4])

    def alpha_vector(self, alpha, k):
        for r in self.percentiles:
            alpha_vector = np.array([[alpha * r]] + (k + 3) * [[0]])
            yield alpha_vector, f"{int(r * 100)}%"
