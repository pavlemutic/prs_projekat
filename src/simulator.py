from numpy.random import default_rng as random_gen

from src.event import Event
from src.prs import ParallelResultsStorage


class Simulator:

    def __init__(self, system):
        self.system = system
        self.results = {}

    def _reset_counters(self):
        for server in self.system.servers[:self.system.k + 4]:
            server.reset_counters()

    def start(self, alpha, simulation_time):
        simulated_time = 0
        self._reset_counters()

        while simulated_time < simulation_time:
            for _ in range(random_gen().poisson(alpha)):
                Event(self.system).go_next("P")
            simulated_time += 1  # seconds

        prs = ParallelResultsStorage()
        for server in self.system.servers[:self.system.k + 4]:
            prs.add(server.calculate_simulation_results(simulation_time))
        return prs
