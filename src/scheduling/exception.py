class SharedException(Exception):
    def __init__(self, edge, error):
        self.edge = edge
        super().__init__(f"{error}")

class DependencyException(Exception):
    def __init__(self, edgei, edgej, error):
        self.edgei = edgei
        self.edgej = edgej
        super().__init__(f"{error}")

class ConcurrencyException(Exception):
    def __init__(self, edgei, edgej, error):
        self.edgei = edgei
        self.edgej = edgej
        super().__init__(f"{error}")