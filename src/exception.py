class CapException(Exception):
    def __init__(self, edge):
        self.edge = edge
        super().__init__(f"Cap exception occurred with value: {edge}")

class DependencyException(Exception):
    def __init__(self, edgei, edgej):
        self.edgei = edgei
        self.edgej = edgej
        super().__init__(f"Dependency exception occurred between: {edgei} and {edgej}")

class ConcurrencyException(Exception):
    def __init__(self, edgei, edgej):
        self.edgei = edgei
        self.edgej = edgej
        super().__init__(f"Concurrency exception occurred between: {edgei} and {edgej}")