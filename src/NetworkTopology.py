from Communication import Communication

class NetworkTopology:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.communication = []

    def add_node(self, node):
        self.nodes.append(node)

    def add_edges(self, node1, node2):
        name = f"e{len(self.get_edges())}"
        edge = Communication(node1, node2, name)
        self.edges.append(edge)

    def get_edges(self):
        return self.edges
    
    def get_edges_str(self):
        # edges_str = [ f"e{edge}" for edge in range(1, len(self.edges) + 1) ]
        edges_str = [ edge.name for edge in self.edges ]
        return edges_str

    def get_communication(self) -> list[str]:
        for edge in self.get_edges():
            node1, node2 = edge.get_nodes()
            self.communication.append(node1.communicate(node2))
        return self.communication

    def get_ranging(self) -> list[Communication]:
        ranging = [ edge for edge in self.edges if edge.is_ranging()]
        return ranging
    
    def get_forwarding(self) -> list[Communication]:
        forwarding = [ edge for edge in self.edges if edge.is_forwarding()]
        return forwarding