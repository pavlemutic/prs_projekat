from numpy.random import default_rng as random_gen

from src.event import Event


class Simulator:

    def __init__(self, system):
        self.system = system
        self.metrics = ["mi", "s", "lam", "ro", "u", "j", "r"]
        self.results = {}

    def _reset_counters(self):
        for server in self.system.servers[:self.system.k + 4]:
            server.reset_counters()

    def _reset_calculations(self):
        for server in self.system.servers[:self.system.k + 4]:
            server.reset_calculations()

    def start(self, alpha, simulation_time):
        simulated_time = 0
        self._reset_counters()

        while simulated_time < simulation_time:
            for _ in range(random_gen().poisson(alpha)):
                Event(self.system).go_next("P")
            simulated_time += 1  # seconds

        for server in self.system.servers[:self.system.k + 4]:
            server.calculate_simulation_results(simulation_time)

    def get_results(self, alpha):
        table = []
        for metric in self.metrics:
            line = [f"{self.system.k}, {round(alpha, 2)}", metric.upper()]
            for server in self.system.servers[:self.system.k + 4]:
                line.append(getattr(server, f"{metric}_sim"))
            table.append(line)
        self._reset_calculations()
        return table
