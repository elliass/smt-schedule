class Topology:
    def __init__(self, max_edges, max_slots, max_channels):
        self.MAX_EDGES = max_edges
        self.MAX_SLOTS = max_slots
        self.MAX_CHANNELS = max_channels

    def get_edges(self):
        # Define the list of communication represented with edges
        edges = [f"e{edge}" for edge in range(self.MAX_EDGES)]
        return edges