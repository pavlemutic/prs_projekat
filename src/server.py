class Server:
    def __init__(self, name, mi=None, s=None):
        self._name = name
        self._mi = mi
        self._s = self._convert_to_sec(s)

    def __repr__(self):
        return f"{self.name}:\n" \
               f"\tmi: {self.mi}\n" \
               f"\ts: {self.s}\n"

    @property
    def name(self):
        return self._name

    @property
    def mi(self):
        if self._mi:
            return self._mi

        if self._s:
            self._mi = round(1 / self._s, 2)
            return self._mi

    @property
    def s(self):
        if self._s:
            return self._s

        if self._mi:
            self._s = round(1 / self._mi, 2)
            return self._s

    @staticmethod
    def _convert_to_sec(value):
        if value.endswith("ms"):
            return float(value.rstrip("ms").strip()) / 1000

        if value.endswith("s"):
            return float(value.rstrip("s").strip())

        raise ValueError(f"Value '{value}' doesn't have suffix 's' nor 'ms'")
