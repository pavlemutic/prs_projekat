from random import randint, choices


class Server:

    OUT = "OUT"

    def __init__(self, name, id=None, mi=None, s=None):
        self._id = id
        self._name = name
        self._mi = mi
        self._s = self._convert_to_sec(s)

        self.active = True
        self.events_history = {}
        self.total_process_time = 0
        self.chunk_process_time = 0
        self.total_time = 0
        self.events_count = 0
        self.next_servers = {}

    def __repr__(self):
        return f"{self.name}:\n" \
               f"\tmi: {self.mi}\n" \
               f"\ts: {self.s}\n" \
               f"\tnext: {self.next_servers}\n"

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

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
        process_time = randint(1, self.s * 1000 * 2) / 1000
        self.events_history[event.id] = process_time
        self.total_process_time += process_time + event.event_time
        event.total_time += process_time + event.event_time
        event.history.append(self.name)
        self.events_count += 1

        names, percents = self._get_next_servers(event.k)
        next_server_name = choices(names, weights=percents, k=1)[0]
        event.go_next(next_server_name)

    def get_statistic(self):
        lam = self.events_count / int(self.total_process_time)
        ro = lam / self.mi
        u = lam * self.s
        j = ro / (1 - ro)
        return f"\n{self.name}:\n" \
               f"MI: {self.mi}\n" \
               f"LAM: {lam}\n" \
               f"RO: {ro}\n" \
               f"U: {u}\n" \
               f"J: {j}\n" \
               f"R: {self.total_process_time}\n" \
               f"CNT: {self.events_count}\n"
