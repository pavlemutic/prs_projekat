import numpy


class Iteration:
    def __init__(self, name=None, k=None, a_vector=None):
        if not (name or k and list(a_vector)):
            raise AttributeError("'name' or 'k' and 'a_vector' must be provided.")

        self._name = name if name else self.get_iteration_name(k, a_vector)
        self.lam = []
        self.ro = []
        self.u = []
        self.j = []
        self.r = []

    def __repr__(self):
        return f"{self.name}:\n" \
               f"lambdas: {self.lam}\n" \
               f"U: {self.u}\n\n"

    @property
    def name(self):
        return self._name

    @property
    def lam_array(self):
        return self._vector_to_array(self.lam)

    @property
    def ro_array(self):
        return self._vector_to_array(self.ro)

    @property
    def u_array(self):
        return self._vector_to_array(self.u)

    @property
    def j_array(self):
        return self._vector_to_array(self.j)

    @property
    def r_array(self):
        return self._vector_to_array(self.r)

    @staticmethod
    def _vector_to_array(vector):
        vector = vector.flatten() if isinstance(vector, numpy.ndarray) else vector
        return [round(item, 2) for item in vector]

    @staticmethod
    def get_iteration_name(k, alpha):
        if isinstance(alpha, numpy.ndarray):
            alpha = round(alpha[0][0], 2)
        return f"{k}, {alpha}"
