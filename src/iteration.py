import numpy


class Iteration:
    def __init__(self, name, lambdas=None):
        self.name = name
        self.lambdas = lambdas
        self.ro = []
        self.u = []
        self.j = []
        self.r = []

    def __repr__(self):
        return f"{self.name}:\n" \
               f"lambdas: {self.lambdas}\n" \
               f"U: {self.u}\n\n"

    @staticmethod
    def get_iteration_name(k, alpha):
        if isinstance(alpha, numpy.ndarray):
            alpha = round(alpha[0][0], 2)
        return f"{k}, {alpha}"
