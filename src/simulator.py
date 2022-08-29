from pathlib import Path
from random import randint

from src.event import Event


class Simulator:

    def __init__(self, system):
        self.system = system
        self.simulation_time = 0
        self.all_events = []

    @property
    def events_count(self):
        return len(self.all_events)

    def start(self, alpha, k, max_time=0):
        content = "Simulacija otvorene mreze.\n"
        self.system.k = k

        if max_time:
            self.system.set_max_time(max_time)

        while self.simulation_time < max_time:
            event_time = randint(1, int(1 / alpha * 1000)) / 1000
            event = Event(self.system, alpha, event_time)
            self.all_events.append(event)
            if self.events_count % alpha == 0:
                self.simulation_time = self.events_count / alpha

            server = self.system.get_server_by_name("P")
            server.process_event(event)

        content += f"\nALPHA: {alpha}\n"
        content += f"INPUT EVENTS: {self.events_count}\n"
        content += f"AVG EVENT TIME: {sum([event.total_time for event in self.all_events]) / self.events_count}\n"

        total_time = self.all_events[-1].total_time
        for event in self.all_events[:-1]:
            total_time += event.event_time

        content += f"TOTAL TIME: {total_time}s -> {total_time / 1800} min\n"

        for server in self.system.servers[:k + 4]:
            content += f"{server.get_statistic()}\n"

        path = Path(__file__).parent.parent / "output" / "rezultati_simulacija"
        with open(path, "w") as outfile:
            outfile.write(content)
        print(f"Upisan fajl: {path}")

