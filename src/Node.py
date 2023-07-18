from UWBCommunication import UWBCommunication
from abc import ABC, abstractmethod

class Node(ABC):
    def __init__(self, name):
        self.name = name
        self.communications = []
        self.parent = None
        self.queue = []

    def __str__(self):
        return self.name
    
    @abstractmethod
    def communicate(self, other):
        pass

    @abstractmethod
    def exchange(self, other):
        pass

    def is_tag(self):
        return False

    def is_anchor(self):
        return False
    
    def set_communication(self, edge):
        self.communications.append(edge)
    
    def get_communication(self) -> list[UWBCommunication]:
        return self.communications
    
    def set_parent(self, parent_node):
        self.parent = parent_node
    
    def get_parent(self):
        return self.parent
    
    def set_queue(self, payload):
        self.queue.append(payload)
    
    def get_queue(self):
        return self.queue
    
    def delete_forwarded_payload(self):
        self.queue = []

class Tag(Node):
    def communicate(self, other):
        # print(f"{self.name} -> {other}")
        return (self.name, other.name)
    
    def exchange(self, other, payload):
        other.set_queue(payload)
        return f"Ranging between {self.name} and {other}"

    def is_tag(self):
        return True
    

class Anchor(Node):
    def communicate(self, other):
        # print(f"{self.name} -> {other}")
        return (self.name, other.name)
    
    def exchange(self, other, payload):
        other.set_queue(payload)
        self.delete_forwarded_payload()
        return f"Forwarding between {self.name} and {other}"
    
    def is_anchor(self):
        return True