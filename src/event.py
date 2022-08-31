import uuid


class Event:
    OUT = "OUT"

    def __init__(self, system):
        self.id = uuid.uuid4()
        self.system = system
        self.k = system.k

    def go_next(self, server_name):
        if server_name != self.OUT:
            server = self.system.get_server_by_name(server_name)
            server.process_event(self)
