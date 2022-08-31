from random import choices
from numpy.random import default_rng as random_gen

from src.prs import StorageShelf


class Server:

    OUT = "OUT"

    def __init__(self, name, id=None, mi=None, s=None):
        self.id = id
        self.pid = []
        self.name = name
        self._mi = mi
        self._s = self._convert_to_sec(s)

        self.total_process_time = 0
        self.events_count = 0
        self.next_servers = {}

    @property
    def mi(self):
        if self._mi:
            return self._mi

        if self._s:
            self._mi = round(1 / self._s, 3)
            return self._mi

    @property
    def s(self):
        if self._s:
            return self._s

        if self._mi:
            self._s = round(1 / self._mi, 3)
            return self._s

    @staticmethod
    def _convert_to_sec(value):
        if value.endswith("ms"):
            return float(value.rstrip("ms").strip()) / 1000

        if value.endswith("s"):
            return float(value.rstrip("s").strip())

        raise ValueError(f"Value '{value}' doesn't have suffix 's' nor 'ms'")

    def _get_next_servers(self, k):
        names = []
        percents = []

        for name, percent in self.next_servers[k].items():
            names.append(name)
            percents.append(percent)

        names.append(self.OUT)
        percents.append(1 - sum(percents))
        return names, percents

    def process_event(self, event):
        process_time = random_gen().standard_exponential() * self.s
        self.total_process_time += process_time
        self.events_count += 1

        names, percents = self._get_next_servers(event.k)
        next_server_name = choices(names, weights=percents, k=1)[0]
        event.go_next(next_server_name)

    def calculate_simulation_results(self, simulation_time):
        s = self.total_process_time / self.events_count
        mi = 1 / s
        lam = self.events_count / simulation_time
        ro = lam / mi
        u = lam * s
        j = ro / (1 - ro)
        r = j / lam

        return StorageShelf(self.name, mi, s, lam, ro, u, j, r)

    def reset_counters(self):
        self.events_count = 0
        self.total_process_time = 0
