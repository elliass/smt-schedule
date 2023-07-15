from abc import ABC, abstractmethod

class Node(ABC):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    @abstractmethod
    def communicate(self, other):
        pass

    def is_tag(self):
        return False

    def is_anchor(self):
        return False

class Tag(Node):
    def communicate(self, other):
        # print(f"{self.name} -> {other}")
        return (self.name, other.name)
    
    def is_tag(self):
        return True

class Anchor(Node):
    def communicate(self, other):
        # print(f"{self.name} -> {other}")
        return (self.name, other.name)
    
    def is_anchor(self):
        return True