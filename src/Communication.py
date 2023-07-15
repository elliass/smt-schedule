class Communication:
    def __init__(self, node1, node2, name):
        self.node1 = node1
        self.node2 = node2
        self.name = name

    def __str__(self):
        return self.name

    def get_node1(self):
        return self.node1
    
    def get_node2(self):
        return self.node2
    
    def get_nodes(self):
        return (self.node1, self.node2)

    def is_ranging(self):
        return self.get_node1().is_tag()
    
    def is_forwarding(self):
        return self.get_node1().is_anchor()