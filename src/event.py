import uuid


class Event:
    OUT = "OUT"

    def __init__(self, system, alpha, event_time):
        self.id = uuid.uuid4()
        self.status = "RUNNING"
        self.event_time = event_time
        self.total_time = 0
        self.history = []
        self.system = system
        self.servers = system.servers
        self.k = system.k
        self.alpha = alpha

    def go_next(self, server_name):
        if server_name == self.OUT:
            self.status = "COMPLETE"
            return

        server = [server for server in self.servers if server.name == server_name][0]
        server.process_event(self)

