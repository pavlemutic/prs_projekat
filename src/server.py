class Server:
    def __init__(self, name, mi=None, s=None, parallel=False):
        self._name = name
        self._mi = mi
        self._s = self._convert_to_sec(s)
        self._lam = []
        self._parallel = parallel
        # self._ro = lam / mi if mi and lam else None

    def __repr__(self):
        return f"{self.name}:\n" \
               f"\tmi: {self.mi}\n" \
               f"\ts: {self.s}\n" \
               f"\tlam: {self.lam}\n" \
               f"\tparallel: {self.parallel}\n"

    @property
    def name(self):
        return self._name

    @property
    def mi(self):
        if self._mi:
            return self._mi

        if self._s:
            self._mi = 1 / self._s
            return self._mi

    @property
    def s(self):
        if self._s:
            return self._s

        if self._mi:
            self._s = 1 / self._mi
            return self._s

    @property
    def lam(self):
        return self._lam

    # @property
    # def ro(self):
    #     if self._ro:
    #         return self._ro
    #
    #     if self._mi and self._lam:
    #         self._ro = self._lam / self._mi
    #         return self._ro

    @property
    def parallel(self):
        return self._parallel

    @staticmethod
    def _convert_to_sec(value):
        if value.endswith("ms"):
            return float(value.rstrip("ms").strip()) / 1000

        if value.endswith("s"):
            return float(value.rstrip("s").strip())

        raise ValueError(f"Value '{value}' doesn't have suffix 's' nor 'ms'")
