from abc import ABC, abstractmethod

class UWBCommunication:
    def __init__(self, node1, node2, name):
        self.node1 = node1
        self.node2 = node2
        self.name = name
        self.assigned_cell = {}

    def __str__(self):
        return self.name
    
    def get_node1(self):
        return self.node1
    
    def get_node2(self):
        return self.node2
    
    def get_nodes(self):
        return (self.node1, self.node2)
    
    def is_cap(self):
        return False
    
    def is_ranging(self):
        return False
    
    def is_forwarding(self):
        return False
    
    def set_cell(self, timeslot, channel):
        self.assigned_cell = {'timeslot' : timeslot, 'channel': channel}
    
    def get_cell(self):
        return self.assigned_cell

class CAP(UWBCommunication):
    def is_cap(self):
        return True

    def get_tag(self):
        return self.node1 
    
    def get_anchor(self):
        return self.node2

class Ranging(UWBCommunication):
    def is_ranging(self):
        return True

    def get_tag(self):
        return self.node1 
    
    def get_anchor(self):
        return self.node2

class Forwarding(UWBCommunication):
    def is_forwarding(self):
        return True
    
    def get_child(self):
        return self.node1 
    
    def get_parent(self):
        return self.node2