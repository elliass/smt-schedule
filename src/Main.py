from NetworkTopology import NetworkTopology
from Node import Tag, Anchor
from TSCHSolver import TSCHSolver
import json

class Main:
    def __init__(self, max_solutions=1, max_slots=4, max_channels=1):
        self.network = NetworkTopology()
        self.max_solutions = max_solutions
        self.max_slots = max_slots
        self.max_channels = max_channels
        self.tsch_solver = TSCHSolver(self.network, max_solutions, self.max_slots, self.max_channels)

    def setup_topology(self):
        # Implement the logic to set up the topology and communication edges
        # Read JSON file with topology definition
        with open('input.json', 'r') as file:
            cells = json.load(file)

        for cell_key, cell_value in cells.items():
            tags = cell_value.get("tags", [])
            anchors = cell_value.get("anchors", [])
            parent =  ["t1","a1"]
            cap = cell_value.get("cap", [])
            ranging = cell_value.get("ranging", [])
            forwarding = cell_value.get("forwarding", [])
            # print(cell_key)
            # print("Tags:", tags, "- Anchors:", anchors, "- Parent:", parent)

            # Initialize nodes
            tag_nodes = [ Tag(tag) for tag in tags ]
            anchors_nodes = [ Anchor(anchors) for anchors in anchors ]

            # Add nodes to network topology
            nodes = tag_nodes + anchors_nodes
            for node in nodes:
                self.network.add_node(node)

            # Add connections edges
            for edge in ranging + cap:
                node1, node2 = edge[0], edge[1]
                self.network.add_edges(Tag(node1), Anchor(node2))
            
            for edge in forwarding:
                node1, node2 = edge[0], edge[1]
                self.network.add_edges(Anchor(node1), Anchor(node2))
        # # +--------+
        # # | Cell 1 |
        # # +--------+
        # # Create nodes
        # tag1 = Tag("t1")
        # anchor1 = Anchor("a1")
        # anchor2 = Anchor("a2")
        # anchor3 = Anchor("a3")
        
        # # Add nodes
        # self.network.add_node(tag1)
        # self.network.add_node(anchor1)
        # self.network.add_node(anchor2)
        # self.network.add_node(anchor3)

        # # Add connections
        # self.network.add_edges(tag1, anchor1) # CAP
        # self.network.add_edges(tag1, anchor1)
        # self.network.add_edges(tag1, anchor2)
        # self.network.add_edges(tag1, anchor3)
        # self.network.add_edges(anchor2, anchor1)
        # self.network.add_edges(anchor3, anchor1)

        # # +--------+
        # # | Cell 2 |
        # # +--------+
        # # Add nodes
        # tag2 = Tag("t2")
        # anchor4 = Anchor("a4")
        # anchor5 = Anchor("a5")
        # anchor6 = Anchor("a6")

        # self.network.add_node(tag2)
        # self.network.add_node(anchor4)
        # self.network.add_node(anchor5)
        # self.network.add_node(anchor6)

        # # Add connections
        # self.network.add_edges(tag2, anchor4)
        # self.network.add_edges(tag2, anchor5)
        # self.network.add_edges(tag2, anchor6)
        # self.network.add_edges(anchor5, anchor4)
        # self.network.add_edges(anchor6, anchor4)
        # self.network.add_edges(anchor4, anchor1)

    def run_tsch_algorithm(self):
        # Implement the logic to run the TSCH algorithm and display results
        # Find feasible solutions
        solutions, result_summary = self.tsch_solver.run_solver()

        # Display solutions
        for idx, solution in enumerate(solutions):
            # print(f"--- Solution {idx+1} ---")
            # self.tsch_solver.display(solution)
            # print()
            results = self.tsch_solver.verify(solution)
            if results.__contains__(False):
                print("+-------------------------------+")
                print("| Solution is not verified      |")
                print("+-------------------------------+")
                break

        # Print last solution found
        found = len(solutions)
        if found > 0:
            print(f"--- Solution {found} ---")
            self.tsch_solver.display(solutions[found-1])
            print()
            # print("+-------------------------------+")
            # print("| All solutions are verified    |")
            # print("+-------------------------------+")

        self.tsch_solver.summarize(result_summary)
        self.tsch_solver.assess_quality()


if __name__ == "__main__":
    main = Main(max_solutions=100, max_slots=4, max_channels=1)
    main.setup_topology()
    main.run_tsch_algorithm()
