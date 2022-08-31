from numpy import mean


class StorageShelf:
    def __init__(self, name, *args):
        self.name = name
        self.mi = [args[0]]
        self.s = [args[1]]
        self.lam = [args[2]]
        self.ro = [args[3]]
        self.u = [args[4]]
        self.j = [args[5]]
        self.r = [args[6]]

    def __add__(self, other):
        if not isinstance(other, StorageShelf):
            raise TypeError(f"Add failed, type must be 'StorageShelf', but was '{type(other)}'")

        if self.name != other.name:
            raise ValueError(f"Add failed, object names are not equal '{self.name}' vs '{other.name}'")

        self.mi.extend(other.mi)
        self.s.extend(other.s)
        self.lam.extend(other.lam)
        self.ro.extend(other.ro)
        self.u.extend(other.u)
        self.j.extend(other.j)
        self.r.extend(other.r)

        return self


class ParallelResultsStorage:
    def __init__(self):
        self.shelves = {}
        self._metrics = ["mi", "s", "lam", "ro", "u", "j", "r"]

    def add(self, shelf):
        self.shelves[shelf.name] = shelf

    def extend(self, prs_list):
        for prs in prs_list:
            if not self.shelves:
                self.shelves = prs.shelves
                continue

            for name, remote_shelf_item in prs.shelves.items():
                local_shelf_item = self.shelves.get(name)
                local_shelf_item += remote_shelf_item

    def release(self, k, alpha):
        table = []
        for metric in self._metrics:
            line = [f"{k}, {round(alpha, 2)}", metric.upper()]
            for _, shelf_item in self.shelves.items():
                line.append(round(mean(getattr(shelf_item, metric)), 3))
            table.append(line)
        return table

