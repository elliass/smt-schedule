class Topology:
    def __init__(self, MAX_EDGES, MAX_SLOTS, MAX_CHANNELS) -> None:
        self.MAX_EDGES = MAX_EDGES
        self.MAX_SLOTS = MAX_SLOTS
        self.MAX_CHANNELS = MAX_CHANNELS

    def get_edges(self):
        # Define the list of communication represented with edges
        edges = []
        for edge in range(self.MAX_EDGES):
            edges.append(f"e{edge}")
        
        return edges